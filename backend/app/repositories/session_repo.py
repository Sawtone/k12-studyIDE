"""
Session Repository
会话数据访问层
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.database.models import Session
from app.core.logging import get_logger

logger = get_logger(__name__)


class SessionRepository:
    """
    会话Repository

    职责：
    1. 会话的CRUD操作
    2. 会话列表查询和过滤
    3. 会话统计信息更新
    4. 过期会话清理
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        session_id: str,
        user_id: str,
        mode: str,
        title: Optional[str] = None,
        grade_level: Optional[str] = None,
        subject: Optional[str] = None
    ) -> Session:
        """
        创建新会话

        Args:
            session_id: 会话ID
            user_id: 用户ID
            mode: 学习模式
            title: 会话标题
            grade_level: 年级水平
            subject: 学科

        Returns:
            Session对象
        """
        try:
            session = Session(
                session_id=session_id,
                user_id=user_id,
                mode=mode,
                title=title,
                grade_level=grade_level,
                subject=subject,
                status='active'
            )

            self.db.add(session)
            await self.db.flush()
            await self.db.refresh(session)

            logger.info(f"创建会话: session_id={session_id}, user_id={user_id}, mode={mode}")

            return session

        except Exception as e:
            logger.error(f"创建会话失败: {str(e)}")
            raise

    async def get_by_id(self, session_id: str) -> Optional[Session]:
        """
        根据ID获取会话

        Args:
            session_id: 会话ID

        Returns:
            Session对象或None
        """
        try:
            query = select(Session).where(Session.session_id == session_id)
            result = await self.db.execute(query)
            session = result.scalar_one_or_none()

            if session:
                # 更新最后访问时间
                session.last_accessed_at = datetime.utcnow()
                await self.db.flush()

            return session

        except Exception as e:
            logger.error(f"获取会话失败: {str(e)}")
            raise

    async def update(
        self,
        session_id: str,
        **updates: Any
    ) -> Optional[Session]:
        """
        更新会话信息

        Args:
            session_id: 会话ID
            **updates: 要更新的字段

        Returns:
            更新后的Session对象
        """
        try:
            # 添加updated_at
            updates['updated_at'] = datetime.utcnow()

            stmt = update(Session).where(
                Session.session_id == session_id
            ).values(**updates).returning(Session)

            result = await self.db.execute(stmt)
            session = result.scalar_one_or_none()

            if session:
                await self.db.flush()
                logger.info(f"更新会话: session_id={session_id}, fields={list(updates.keys())}")

            return session

        except Exception as e:
            logger.error(f"更新会话失败: {str(e)}")
            raise

    async def delete(self, session_id: str) -> bool:
        """
        软删除会话

        Args:
            session_id: 会话ID

        Returns:
            是否成功删除
        """
        try:
            stmt = update(Session).where(
                Session.session_id == session_id
            ).values(
                status='deleted',
                updated_at=datetime.utcnow()
            )

            result = await self.db.execute(stmt)
            success = result.rowcount > 0

            if success:
                logger.info(f"删除会话: session_id={session_id}")

            return success

        except Exception as e:
            logger.error(f"删除会话失败: {str(e)}")
            raise

    async def list_by_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        mode: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> tuple[List[Session], int]:
        """
        获取用户的会话列表

        Args:
            user_id: 用户ID
            status: 状态过滤
            mode: 模式过滤
            page: 页码
            limit: 每页数量

        Returns:
            (会话列表, 总数)
        """
        try:
            # 构建查询
            query = select(Session).where(Session.user_id == user_id)

            if status:
                query = query.where(Session.status == status)

            if mode:
                query = query.where(Session.mode == mode)

            # 获取总数
            count_query = select(func.count()).select_from(query.subquery())
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()

            # 分页查询
            query = query.order_by(Session.created_at.desc())
            query = query.offset((page - 1) * limit).limit(limit)

            result = await self.db.execute(query)
            sessions = result.scalars().all()

            return list(sessions), total

        except Exception as e:
            logger.error(f"获取会话列表失败: {str(e)}")
            raise

    async def increment_stats(
        self,
        session_id: str,
        interactions: int = 0,
        ai_calls: int = 0,
        tokens: int = 0
    ) -> None:
        """
        增加会话统计信息

        Args:
            session_id: 会话ID
            interactions: 交互次数增量
            ai_calls: AI调用次数增量
            tokens: Token使用量增量
        """
        try:
            stmt = update(Session).where(
                Session.session_id == session_id
            ).values(
                total_interactions=Session.total_interactions + interactions,
                total_ai_calls=Session.total_ai_calls + ai_calls,
                total_tokens_used=Session.total_tokens_used + tokens,
                updated_at=datetime.utcnow()
            )

            await self.db.execute(stmt)
            logger.debug(f"更新会话统计: session_id={session_id}")

        except Exception as e:
            logger.error(f"更新会话统计失败: {str(e)}")
            raise

    async def cleanup_expired(
        self,
        days: int = 30,
        batch_size: int = 100
    ) -> int:
        """
        清理过期会话

        Args:
            days: 保留天数
            batch_size: 批量处理大小

        Returns:
            清理的数量
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # 查找过期会话
            query = select(Session.session_id).where(
                Session.status == 'active',
                Session.last_accessed_at < cutoff_date
            ).limit(batch_size)

            result = await self.db.execute(query)
            expired_ids = [row[0] for row in result.fetchall()]

            if not expired_ids:
                return 0

            # 批量更新为archived状态
            stmt = update(Session).where(
                Session.session_id.in_(expired_ids)
            ).values(
                status='archived',
                updated_at=datetime.utcnow()
            )

            result = await self.db.execute(stmt)
            count = result.rowcount

            logger.info(f"清理过期会话: count={count}, cutoff_date={cutoff_date}")

            return count

        except Exception as e:
            logger.error(f"清理过期会话失败: {str(e)}")
            raise

    async def get_statistics(
        self,
        user_id: Optional[str] = None,
        mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取会话统计信息

        Args:
            user_id: 用户ID（可选）
            mode: 模式（可选）

        Returns:
            统计信息字典
        """
        try:
            query = select(
                func.count(Session.session_id).label('total_sessions'),
                func.sum(Session.total_interactions).label('total_interactions'),
                func.sum(Session.total_ai_calls).label('total_ai_calls'),
                func.sum(Session.total_tokens_used).label('total_tokens'),
                func.avg(Session.total_interactions).label('avg_interactions')
            )

            if user_id:
                query = query.where(Session.user_id == user_id)

            if mode:
                query = query.where(Session.mode == mode)

            result = await self.db.execute(query)
            row = result.first()

            return {
                'total_sessions': row.total_sessions or 0,
                'total_interactions': row.total_interactions or 0,
                'total_ai_calls': row.total_ai_calls or 0,
                'total_tokens': row.total_tokens or 0,
                'avg_interactions': float(row.avg_interactions or 0)
            }

        except Exception as e:
            logger.error(f"获取会话统计失败: {str(e)}")
            raise

    async def batch_create(
        self,
        sessions: List[Dict[str, Any]]
    ) -> List[Session]:
        """
        批量创建会话

        Args:
            sessions: 会话数据列表

        Returns:
            创建的会话对象列表

        Examples:
            >>> sessions = [
            ...     {"session_id": "s1", "user_id": "u1", "mode": "literature"},
            ...     {"session_id": "s2", "user_id": "u1", "mode": "science"}
            ... ]
            >>> await repo.batch_create(sessions)
        """
        try:
            session_objects = []

            for session_data in sessions:
                session = Session(
                    session_id=session_data["session_id"],
                    user_id=session_data["user_id"],
                    mode=session_data["mode"],
                    title=session_data.get("title"),
                    grade_level=session_data.get("grade_level"),
                    subject=session_data.get("subject"),
                    status='active'
                )
                session_objects.append(session)
                self.db.add(session)

            await self.db.flush()

            for session in session_objects:
                await self.db.refresh(session)

            logger.info(f"批量创建会话: {len(session_objects)} 个")

            return session_objects

        except Exception as e:
            logger.error(f"批量创建会话失败: {str(e)}")
            raise

    async def batch_update(
        self,
        updates: List[Dict[str, Any]]
    ) -> int:
        """
        批量更新会话

        Args:
            updates: 更新列表，每个包含session_id和要更新的字段

        Returns:
            更新的会话数量

        Examples:
            >>> updates = [
            ...     {"session_id": "s1", "title": "新标题1"},
            ...     {"session_id": "s2", "status": "archived"}
            ... ]
            >>> count = await repo.batch_update(updates)
        """
        try:
            updated_count = 0

            for update_data in updates:
                session_id = update_data.pop("session_id")
                update_data['updated_at'] = datetime.utcnow()

                stmt = update(Session).where(
                    Session.session_id == session_id
                ).values(**update_data)

                result = await self.db.execute(stmt)
                if result.rowcount > 0:
                    updated_count += 1

            await self.db.flush()

            logger.info(f"批量更新会话: {updated_count} 个")

            return updated_count

        except Exception as e:
            logger.error(f"批量更新会话失败: {str(e)}")
            raise

    async def batch_delete(
        self,
        session_ids: List[str],
        hard_delete: bool = False
    ) -> int:
        """
        批量删除会话

        Args:
            session_ids: 会话ID列表
            hard_delete: 是否硬删除（True）或软删除（False）

        Returns:
            删除的会话数量

        Examples:
            >>> count = await repo.batch_delete(["s1", "s2"], hard_delete=False)
        """
        try:
            if hard_delete:
                # 硬删除
                stmt = delete(Session).where(Session.session_id.in_(session_ids))
            else:
                # 软删除
                stmt = update(Session).where(
                    Session.session_id.in_(session_ids)
                ).values(
                    status='deleted',
                    updated_at=datetime.utcnow()
                )

            result = await self.db.execute(stmt)
            deleted_count = result.rowcount

            await self.db.flush()

            logger.info(f"批量{'硬' if hard_delete else '软'}删除会话: {deleted_count} 个")

            return deleted_count

        except Exception as e:
            logger.error(f"批量删除会话失败: {str(e)}")
            raise
