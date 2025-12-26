"""
聊天历史Repository
负责聊天消息的数据访问
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database.models import ChatMessage
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChatHistoryRepository:
    """聊天历史数据访问层"""

    def __init__(self, db: AsyncSession) -> None:
        """
        初始化Repository

        Args:
            db: 数据库会话
        """
        self.db = db

    async def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        context: Optional[Dict[str, Any]] = None,
        message_type: Optional[str] = None,
        related_agent: Optional[str] = None,
        tokens_used: Optional[int] = None,
        model_used: Optional[str] = None,
        reply_to_message_id: Optional[int] = None
    ) -> ChatMessage:
        """
        保存聊天消息

        Args:
            session_id: 会话ID
            role: 角色 (user/assistant/system)
            content: 消息内容
            context: 上下文信息
            message_type: 消息类型
            related_agent: 相关Agent
            tokens_used: Token使用量
            model_used: 使用的模型
            reply_to_message_id: 回复的消息ID

        Returns:
            消息对象
        """
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            context=context,
            message_type=message_type,
            related_agent=related_agent,
            tokens_used=tokens_used,
            model_used=model_used,
            reply_to_message_id=reply_to_message_id
        )

        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        logger.info(f"保存聊天消息: {message.id}, 角色: {role}, 会话: {session_id}")

        return message

    async def get_message(self, message_id: int) -> Optional[ChatMessage]:
        """
        获取单条消息

        Args:
            message_id: 消息ID

        Returns:
            消息对象或None
        """
        result = await self.db.execute(
            select(ChatMessage).where(ChatMessage.id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_chat_history(
        self,
        session_id: str,
        limit: int = 50,
        before_message_id: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        获取聊天历史

        Args:
            session_id: 会话ID
            limit: 限制数量
            before_message_id: 在此消息之前（用于分页）

        Returns:
            消息列表
        """
        query = select(ChatMessage).where(ChatMessage.session_id == session_id)

        if before_message_id:
            query = query.where(ChatMessage.id < before_message_id)

        query = query.order_by(ChatMessage.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        messages = list(result.scalars().all())

        # 反转顺序，使其按时间正序排列
        messages.reverse()

        return messages

    async def update_message_feedback(
        self,
        message_id: int,
        user_rating: Optional[int] = None,
        user_feedback: Optional[str] = None,
        is_helpful: Optional[bool] = None
    ) -> Optional[ChatMessage]:
        """
        更新消息反馈

        Args:
            message_id: 消息ID
            user_rating: 用户评分
            user_feedback: 用户反馈
            is_helpful: 是否有帮助

        Returns:
            更新后的消息对象或None
        """
        message = await self.get_message(message_id)
        if not message:
            return None

        if user_rating is not None:
            message.user_rating = user_rating
        if user_feedback is not None:
            message.user_feedback = user_feedback
        if is_helpful is not None:
            message.is_helpful = is_helpful

        await self.db.commit()
        await self.db.refresh(message)

        logger.info(f"更新消息反馈: {message_id}")

        return message

    async def get_recent_context(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取最近的对话上下文

        Args:
            session_id: 会话ID
            limit: 限制数量

        Returns:
            上下文列表
        """
        messages = await self.get_chat_history(session_id, limit=limit)

        context = []
        for msg in messages:
            context.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat() if msg.created_at else None
            })

        return context

    async def batch_create(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[ChatMessage]:
        """
        批量创建聊天消息

        Args:
            messages: 消息列表，每个消息包含必要字段

        Returns:
            创建的消息对象列表

        Examples:
            >>> messages = [
            ...     {"session_id": "s1", "role": "user", "content": "hello"},
            ...     {"session_id": "s1", "role": "assistant", "content": "hi"}
            ... ]
            >>> await repo.batch_create(messages)
        """
        try:
            message_objects = []

            for msg_data in messages:
                message = ChatMessage(
                    session_id=msg_data["session_id"],
                    role=msg_data["role"],
                    content=msg_data["content"],
                    context=msg_data.get("context"),
                    message_type=msg_data.get("message_type"),
                    related_agent=msg_data.get("related_agent"),
                    tokens_used=msg_data.get("tokens_used"),
                    model_used=msg_data.get("model_used"),
                    reply_to_message_id=msg_data.get("reply_to_message_id")
                )
                message_objects.append(message)
                self.db.add(message)

            await self.db.commit()

            for message in message_objects:
                await self.db.refresh(message)

            logger.info(f"批量创建聊天消息: {len(message_objects)} 条")

            return message_objects

        except Exception as e:
            logger.error(f"批量创建聊天消息失败: {str(e)}")
            await self.db.rollback()
            raise

    async def batch_update(
        self,
        updates: List[Dict[str, Any]]
    ) -> int:
        """
        批量更新聊天消息

        Args:
            updates: 更新列表，每个包含message_id和要更新的字段

        Returns:
            更新的消息数量

        Examples:
            >>> updates = [
            ...     {"message_id": 1, "user_rating": 5},
            ...     {"message_id": 2, "is_helpful": True}
            ... ]
            >>> count = await repo.batch_update(updates)
        """
        try:
            updated_count = 0

            for update_data in updates:
                message_id = update_data.pop("message_id")
                message = await self.get_message(message_id)

                if message:
                    for key, value in update_data.items():
                        if hasattr(message, key):
                            setattr(message, key, value)
                    updated_count += 1

            await self.db.commit()

            logger.info(f"批量更新聊天消息: {updated_count} 条")

            return updated_count

        except Exception as e:
            logger.error(f"批量更新聊天消息失败: {str(e)}")
            await self.db.rollback()
            raise

    async def batch_delete(
        self,
        message_ids: List[int]
    ) -> int:
        """
        批量删除聊天消息

        Args:
            message_ids: 消息ID列表

        Returns:
            删除的消息数量

        Examples:
            >>> count = await repo.batch_delete([1, 2, 3])
        """
        try:
            from sqlalchemy import delete

            stmt = delete(ChatMessage).where(ChatMessage.id.in_(message_ids))
            result = await self.db.execute(stmt)
            deleted_count = result.rowcount

            await self.db.commit()

            logger.info(f"批量删除聊天消息: {deleted_count} 条")

            return deleted_count

        except Exception as e:
            logger.error(f"批量删除聊天消息失败: {str(e)}")
            await self.db.rollback()
            raise
