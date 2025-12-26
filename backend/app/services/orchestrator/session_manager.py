"""
会话管理器
负责会话生命周期管理、编辑器状态同步、版本控制
"""

import hashlib
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.database.models import Session as SessionModel, EditorState
from app.cache.cache_strategies import session_cache
from app.core.logging import get_logger
from app.core.exceptions import (
    SessionNotFoundException,
    SessionConflictException,
    ValidationException
)

logger = get_logger(__name__)


class SessionManager:
    """
    会话管理器

    职责：
    1. 会话生命周期管理
    2. 编辑器状态同步
    3. 版本控制
    4. 缓存管理
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        初始化会话管理器

        Args:
            db: 数据库会话
        """
        self.db = db
        self.cache = session_cache

    async def create_session(
        self,
        user_id: str,
        mode: Optional[str] = None,
        title: Optional[str] = None,
        grade_level: Optional[str] = None,
        subject: Optional[str] = None
    ) -> SessionModel:
        """
        创建新会话

        Args:
            user_id: 用户ID
            mode: 学习模式 (literature/science)
            title: 会话标题
            grade_level: 年级水平
            subject: 科目

        Returns:
            创建的会话对象
        """
        # 如果未指定模式，默认为文科模式
        if not mode:
            mode = "literature"

        # 验证模式
        if mode not in ["literature", "science"]:
            raise ValidationException(
                field="mode",
                reason=f"无效的模式: {mode}，仅支持literature和science"
            )

        # 创建会话对象
        session = SessionModel(
            user_id=user_id,
            mode=mode,
            title=title or f"学习会话 - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            grade_level=grade_level,
            subject=subject,
            status="active"
        )

        # 保存到数据库
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        # 初始化Redis缓存
        await self.cache.set_runtime_state(
            session_id=str(session.session_id),
            state={
                "status": "active",
                "mode": mode,
                "last_heartbeat": datetime.utcnow().isoformat(),
                "cursor_line": 0,
                "cursor_column": 0,
                "active_agent": None
            }
        )

        logger.info(f"创建会话成功: {session.session_id}, 用户: {user_id}, 模式: {mode}")

        return session

    async def get_session(self, session_id: str) -> SessionModel:
        """
        获取会话

        Args:
            session_id: 会话ID

        Returns:
            会话对象

        Raises:
            SessionNotFoundException: 会话不存在
        """
        # 查询数据库
        result = await self.db.execute(
            select(SessionModel).where(SessionModel.session_id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            raise SessionNotFoundException(session_id)

        # 更新最后访问时间
        session.last_accessed_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def update_session(
        self,
        session_id: str,
        **updates: Any
    ) -> SessionModel:
        """
        更新会话信息

        Args:
            session_id: 会话ID
            **updates: 要更新的字段

        Returns:
            更新后的会话对象
        """
        session = await self.get_session(session_id)

        # 更新允许的字段
        allowed_fields = ["title", "status", "mode", "grade_level", "subject"]
        for field, value in updates.items():
            if field in allowed_fields and hasattr(session, field):
                setattr(session, field, value)

        session.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(session)

        logger.info(f"更新会话: {session_id}, 字段: {list(updates.keys())}")

        return session

    async def delete_session(self, session_id: str) -> None:
        """
        删除会话（软删除）

        Args:
            session_id: 会话ID
        """
        session = await self.get_session(session_id)
        session.status = "deleted"
        session.updated_at = datetime.utcnow()
        await self.db.commit()

        # 清理缓存
        await self.cache.delete_session_cache(session_id)

        logger.info(f"删除会话: {session_id}")

    async def sync_editor_state(
        self,
        session_id: str,
        content: str,
        cursor_position: Optional[Dict[str, int]] = None,
        selections: Optional[List[Dict[str, Any]]] = None,
        version: Optional[int] = None,
        change_type: Optional[str] = None,
        changed_range: Optional[Dict[str, int]] = None
    ) -> EditorState:
        """
        同步编辑器状态

        Args:
            session_id: 会话ID
            content: 内容文本
            cursor_position: 光标位置
            selections: 选择区域
            version: 版本号
            change_type: 变更类型
            changed_range: 变更范围

        Returns:
            编辑器状态对象

        Raises:
            SessionConflictException: 版本冲突
        """
        # 验证会话存在
        session = await self.get_session(session_id)

        # 计算内容哈希
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # 计算字数
        word_count = len(content)

        # 获取当前最新版本
        result = await self.db.execute(
            select(EditorState)
            .where(EditorState.session_id == session_id)
            .order_by(EditorState.version.desc())
            .limit(1)
        )
        latest_state = result.scalar_one_or_none()

        # 确定新版本号
        if version is not None:
            # 如果指定了版本号，检查是否冲突
            if latest_state and version <= latest_state.version:
                raise SessionConflictException(
                    session_id=session_id,
                    expected_version=version,
                    actual_version=latest_state.version
                )
            new_version = version
        else:
            # 自动递增版本号
            new_version = (latest_state.version + 1) if latest_state else 1

        # 创建新的编辑器状态
        editor_state = EditorState(
            session_id=session_id,
            content=content,
            content_hash=content_hash,
            word_count=word_count,
            cursor_position=cursor_position,
            selections=selections,
            version=new_version,
            parent_version=latest_state.version if latest_state else None,
            change_type=change_type,
            changed_range=changed_range
        )

        self.db.add(editor_state)
        await self.db.commit()
        await self.db.refresh(editor_state)

        # 更新会话统计
        session.total_interactions += 1
        session.updated_at = datetime.utcnow()
        await self.db.commit()

        # 更新缓存
        await self.cache.set_content(
            session_id=session_id,
            content=content,
            version=new_version,
            word_count=word_count
        )

        # 更新运行时状态
        if cursor_position:
            await self.cache.update_runtime_field(
                session_id=session_id,
                field="cursor_line",
                value=cursor_position.get("line", 0)
            )
            await self.cache.update_runtime_field(
                session_id=session_id,
                field="cursor_column",
                value=cursor_position.get("column", 0)
            )

        logger.info(
            f"同步编辑器状态: {session_id}, 版本: {new_version}, "
            f"字数: {word_count}"
        )

        return editor_state

    async def get_editor_history(
        self,
        session_id: str,
        from_version: Optional[int] = None,
        to_version: Optional[int] = None,
        limit: int = 50
    ) -> List[EditorState]:
        """
        获取编辑历史

        Args:
            session_id: 会话ID
            from_version: 起始版本
            to_version: 结束版本
            limit: 限制数量

        Returns:
            编辑器状态列表
        """
        query = select(EditorState).where(EditorState.session_id == session_id)

        if from_version is not None:
            query = query.where(EditorState.version >= from_version)

        if to_version is not None:
            query = query.where(EditorState.version <= to_version)

        query = query.order_by(EditorState.version.desc()).limit(limit)

        result = await self.db.execute(query)
        states = result.scalars().all()

        return list(states)

    async def rollback_to_version(
        self,
        session_id: str,
        target_version: int
    ) -> EditorState:
        """
        回滚到指定版本

        Args:
            session_id: 会话ID
            target_version: 目标版本号

        Returns:
            新创建的编辑器状态

        Raises:
            ValidationException: 目标版本不存在
        """
        # 查找目标版本
        result = await self.db.execute(
            select(EditorState)
            .where(
                EditorState.session_id == session_id,
                EditorState.version == target_version
            )
        )
        target_state = result.scalar_one_or_none()

        if not target_state:
            raise ValidationException(
                field="target_version",
                reason=f"版本 {target_version} 不存在"
            )

        # 创建新版本（不是真的回退，而是创建新版本）
        new_state = await self.sync_editor_state(
            session_id=session_id,
            content=target_state.content,
            cursor_position=target_state.cursor_position,
            selections=target_state.selections,
            change_type="rollback"
        )

        logger.info(f"回滚会话 {session_id} 到版本 {target_version}")

        return new_state

    async def get_session_list(
        self,
        user_id: str,
        status: Optional[str] = None,
        mode: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> tuple[List[SessionModel], int]:
        """
        获取用户的会话列表

        Args:
            user_id: 用户ID
            status: 状态筛选
            mode: 模式筛选
            page: 页码
            limit: 每页数量

        Returns:
            (会话列表, 总数)
        """
        query = select(SessionModel).where(SessionModel.user_id == user_id)

        if status:
            query = query.where(SessionModel.status == status)

        if mode:
            query = query.where(SessionModel.mode == mode)

        # 计算总数
        count_result = await self.db.execute(
            select(SessionModel.session_id).where(SessionModel.user_id == user_id)
        )
        total = len(count_result.all())

        # 分页查询
        offset = (page - 1) * limit
        query = query.order_by(SessionModel.created_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        sessions = result.scalars().all()

        return list(sessions), total

    async def cleanup_expired_sessions(
        self,
        days: int = 30,
        batch_size: int = 100
    ) -> int:
        """
        清理过期会话（后台任务）

        功能：
        1. 查找超过指定天数未访问的会话
        2. 将状态更新为archived
        3. 清理相关缓存
        4. 支持批量处理

        Args:
            days: 保留天数（默认30天）
            batch_size: 批量处理大小

        Returns:
            清理的会话数量
        """
        try:
            from datetime import datetime, timedelta
            from app.repositories.session_repo import SessionRepository

            session_repo = SessionRepository(self.db)

            # 清理过期会话
            cleaned_count = await session_repo.cleanup_expired(
                days=days,
                batch_size=batch_size
            )

            if cleaned_count > 0:
                logger.info(f"清理过期会话完成: count={cleaned_count}, days={days}")

                # 清理相关缓存
                # 注意：这里只清理Redis中的会话缓存，数据库记录保留为archived状态
                # 实际的缓存清理可以在后台任务中异步执行

            return cleaned_count

        except Exception as e:
            logger.error(f"清理过期会话失败: {str(e)}")
            raise
