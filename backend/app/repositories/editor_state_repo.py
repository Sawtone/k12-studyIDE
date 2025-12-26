"""
EditorState Repository
编辑器状态数据访问层
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.database.models import EditorState
from app.core.logging import get_logger

logger = get_logger(__name__)


class EditorStateRepository:
    """
    编辑器状态Repository

    职责：
    1. 编辑器状态的保存和查询
    2. 版本历史管理
    3. 内容哈希去重
    4. 版本回滚支持
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(
        self,
        session_id: str,
        content: str,
        content_hash: Optional[str] = None,
        word_count: Optional[int] = None,
        cursor_position: Optional[Dict[str, int]] = None,
        selections: Optional[List[Dict[str, Any]]] = None,
        version: Optional[int] = None,
        parent_version: Optional[int] = None,
        change_type: Optional[str] = None,
        changed_range: Optional[Dict[str, int]] = None
    ) -> EditorState:
        """
        保存编辑器状态

        Args:
            session_id: 会话ID
            content: 内容文本
            content_hash: 内容哈希
            word_count: 字数统计
            cursor_position: 光标位置
            selections: 选择区域
            version: 版本号
            parent_version: 父版本号
            change_type: 变更类型
            changed_range: 变更范围

        Returns:
            EditorState对象
        """
        try:
            # 如果没有指定版本号，获取最新版本号+1
            if version is None:
                latest = await self.get_latest_version(session_id)
                version = (latest.version + 1) if latest else 1

            editor_state = EditorState(
                session_id=session_id,
                content=content,
                content_hash=content_hash,
                word_count=word_count,
                cursor_position=cursor_position,
                selections=selections,
                version=version,
                parent_version=parent_version,
                change_type=change_type,
                changed_range=changed_range
            )

            self.db.add(editor_state)
            await self.db.flush()
            await self.db.refresh(editor_state)

            logger.info(f"保存编辑器状态: session={session_id}, version={version}")

            return editor_state

        except Exception as e:
            logger.error(f"保存编辑器状态失败: {str(e)}")
            raise

    async def get_by_version(
        self,
        session_id: str,
        version: int
    ) -> Optional[EditorState]:
        """
        获取指定版本的编辑器状态

        Args:
            session_id: 会话ID
            version: 版本号

        Returns:
            EditorState对象或None
        """
        try:
            query = select(EditorState).where(
                EditorState.session_id == session_id,
                EditorState.version == version
            )

            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"获取编辑器状态失败: {str(e)}")
            raise

    async def get_latest_version(
        self,
        session_id: str
    ) -> Optional[EditorState]:
        """
        获取最新版本的编辑器状态

        Args:
            session_id: 会话ID

        Returns:
            EditorState对象或None
        """
        try:
            query = select(EditorState).where(
                EditorState.session_id == session_id
            ).order_by(EditorState.version.desc()).limit(1)

            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"获取最新编辑器状态失败: {str(e)}")
            raise

    async def get_version_history(
        self,
        session_id: str,
        from_version: int = 1,
        to_version: int = 999999,
        limit: int = 50
    ) -> List[EditorState]:
        """
        获取版本历史

        Args:
            session_id: 会话ID
            from_version: 起始版本号
            to_version: 结束版本号
            limit: 返回数量限制

        Returns:
            EditorState列表
        """
        try:
            query = select(EditorState).where(
                EditorState.session_id == session_id,
                EditorState.version >= from_version,
                EditorState.version <= to_version
            ).order_by(EditorState.version.desc()).limit(limit)

            result = await self.db.execute(query)
            states = result.scalars().all()

            return list(states)

        except Exception as e:
            logger.error(f"获取版本历史失败: {str(e)}")
            raise

    async def get_by_content_hash(
        self,
        session_id: str,
        content_hash: str
    ) -> Optional[EditorState]:
        """
        根据内容哈希获取编辑器状态（用于去重）

        Args:
            session_id: 会话ID
            content_hash: 内容哈希

        Returns:
            EditorState对象或None
        """
        try:
            query = select(EditorState).where(
                EditorState.session_id == session_id,
                EditorState.content_hash == content_hash
            ).order_by(EditorState.version.desc()).limit(1)

            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"根据哈希获取编辑器状态失败: {str(e)}")
            raise

    async def get_version_count(
        self,
        session_id: str
    ) -> int:
        """
        获取版本总数

        Args:
            session_id: 会话ID

        Returns:
            版本总数
        """
        try:
            query = select(func.count(EditorState.id)).where(
                EditorState.session_id == session_id
            )

            result = await self.db.execute(query)
            return result.scalar() or 0

        except Exception as e:
            logger.error(f"获取版本总数失败: {str(e)}")
            raise

    async def delete_old_versions(
        self,
        session_id: str,
        keep_latest: int = 100
    ) -> int:
        """
        删除旧版本（保留最新的N个版本）

        Args:
            session_id: 会话ID
            keep_latest: 保留最新的版本数

        Returns:
            删除的数量
        """
        try:
            # 获取要保留的最小版本号
            subquery = select(EditorState.version).where(
                EditorState.session_id == session_id
            ).order_by(EditorState.version.desc()).limit(keep_latest).subquery()

            min_version_query = select(func.min(subquery.c.version))
            result = await self.db.execute(min_version_query)
            min_version = result.scalar()

            if min_version is None:
                return 0

            # 删除旧版本
            stmt = delete(EditorState).where(
                EditorState.session_id == session_id,
                EditorState.version < min_version
            )

            result = await self.db.execute(stmt)
            deleted_count = result.rowcount

            logger.info(f"删除旧版本: session={session_id}, deleted={deleted_count}")

            return deleted_count

        except Exception as e:
            logger.error(f"删除旧版本失败: {str(e)}")
            raise

    async def get_version_diff(
        self,
        session_id: str,
        from_version: int,
        to_version: int
    ) -> Dict[str, Any]:
        """
        获取两个版本之间的差异

        Args:
            session_id: 会话ID
            from_version: 起始版本号
            to_version: 目标版本号

        Returns:
            差异信息字典
        """
        try:
            # 获取两个版本
            from_state = await self.get_by_version(session_id, from_version)
            to_state = await self.get_by_version(session_id, to_version)

            if not from_state or not to_state:
                return {}

            # 计算差异
            word_count_diff = (to_state.word_count or 0) - (from_state.word_count or 0)

            # 获取中间的所有变更
            intermediate_query = select(EditorState).where(
                EditorState.session_id == session_id,
                EditorState.version > from_version,
                EditorState.version <= to_version
            ).order_by(EditorState.version)

            result = await self.db.execute(intermediate_query)
            intermediate_states = result.scalars().all()

            changes = [
                {
                    'version': state.version,
                    'change_type': state.change_type,
                    'changed_range': state.changed_range,
                    'timestamp': state.timestamp.isoformat() if state.timestamp else None
                }
                for state in intermediate_states
            ]

            return {
                'from_version': from_version,
                'to_version': to_version,
                'word_count_diff': word_count_diff,
                'changes': changes,
                'total_changes': len(changes)
            }

        except Exception as e:
            logger.error(f"获取版本差异失败: {str(e)}")
            raise

    async def get_statistics(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        获取编辑器状态统计信息

        Args:
            session_id: 会话ID

        Returns:
            统计信息字典
        """
        try:
            query = select(
                func.count(EditorState.id).label('total_versions'),
                func.max(EditorState.version).label('latest_version'),
                func.avg(EditorState.word_count).label('avg_word_count'),
                func.max(EditorState.word_count).label('max_word_count')
            ).where(
                EditorState.session_id == session_id
            )

            result = await self.db.execute(query)
            row = result.first()

            return {
                'total_versions': row.total_versions or 0,
                'latest_version': row.latest_version or 0,
                'avg_word_count': float(row.avg_word_count or 0),
                'max_word_count': row.max_word_count or 0
            }

        except Exception as e:
            logger.error(f"获取编辑器统计失败: {str(e)}")
            raise
