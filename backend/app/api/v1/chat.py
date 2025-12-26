"""
对话API路由
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.orchestrator.agent_coordinator import agent_coordinator
from app.services.orchestrator.session_manager import SessionManager
from app.repositories.chat_history_repo import ChatHistoryRepository
from app.schemas.request import ChatMessageRequest, ChatFeedbackRequest
from app.schemas.response import ChatMessageResponse, ChatHistoryResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["智能对话"])


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    summary="发送聊天消息",
    description="向AI助手发送消息并获取回复"
)
async def send_message(
    request: ChatMessageRequest,
    db: AsyncSession = Depends(get_db)
) -> ChatMessageResponse:
    """发送聊天消息"""
    try:
        # 获取会话信息
        session_manager = SessionManager(db)
        session = await session_manager.get_session(request.session_id)

        # 获取聊天历史
        chat_repo = ChatHistoryRepository(db)
        chat_history = await chat_repo.get_recent_context(
            session_id=request.session_id,
            limit=10
        )

        # 保存用户消息
        user_message = await chat_repo.save_message(
            session_id=request.session_id,
            role="user",
            content=request.message,
            context=request.context
        )

        # 执行Chat Agent
        result = await agent_coordinator.execute_agent(
            agent_type="chat",
            session_id=request.session_id,
            request_id=str(uuid.uuid4()),
            agent_kwargs={
                "grade_level": session.grade_level or "middle",
                "mode": session.mode,
                "subject": session.subject or ""
            },
            message=request.message,
            context=request.context,
            chat_history=chat_history
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"对话失败: {result.error}"
            )

        # 保存助手回复
        assistant_message = await chat_repo.save_message(
            session_id=request.session_id,
            role="assistant",
            content=result.data.get("content", ""),
            message_type=result.data.get("message_type"),
            related_agent="chat_agent",
            tokens_used=result.metadata.get("tokens_used"),
            model_used=result.metadata.get("model"),
            reply_to_message_id=user_message.id
        )

        return ChatMessageResponse(
            message_id=assistant_message.id,
            role="assistant",
            content=result.data.get("content", ""),
            message_type=result.data.get("message_type"),
            action_items=result.data.get("action_items", []),
            created_at=assistant_message.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送消息失败: {str(e)}"
        )


@router.get(
    "/history/{session_id}",
    response_model=ChatHistoryResponse,
    summary="获取聊天历史",
    description="获取会话的聊天历史记录"
)
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    before_message_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
) -> ChatHistoryResponse:
    """获取聊天历史"""
    try:
        chat_repo = ChatHistoryRepository(db)
        messages = await chat_repo.get_chat_history(
            session_id=session_id,
            limit=limit,
            before_message_id=before_message_id
        )

        message_list = [
            ChatMessageResponse(
                message_id=msg.id,
                role=msg.role,
                content=msg.content,
                message_type=msg.message_type,
                action_items=[],
                created_at=msg.created_at
            )
            for msg in messages
        ]

        return ChatHistoryResponse(
            messages=message_list,
            has_more=len(messages) >= limit
        )

    except Exception as e:
        logger.error(f"获取聊天历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取聊天历史失败: {str(e)}"
        )


@router.post(
    "/feedback",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="反馈消息质量",
    description="对AI回复进行评分和反馈"
)
async def submit_feedback(
    request: ChatFeedbackRequest,
    db: AsyncSession = Depends(get_db)
) -> None:
    """提交反馈"""
    try:
        chat_repo = ChatHistoryRepository(db)
        await chat_repo.update_message_feedback(
            message_id=request.message_id,
            user_rating=request.rating,
            user_feedback=request.feedback,
            is_helpful=request.is_helpful
        )

    except Exception as e:
        logger.error(f"提交反馈失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交反馈失败: {str(e)}"
        )
