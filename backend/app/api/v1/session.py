"""
会话管理API路由
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.orchestrator.session_manager import SessionManager
from app.services.orchestrator.mode_dispatcher import mode_dispatcher
from app.schemas.request import (
    CreateSessionRequest,
    UpdateSessionRequest,
    SyncEditorRequest,
    RestoreSessionRequest
)
from app.schemas.response import (
    SessionResponse,
    SessionDetailResponse,
    SessionListResponse,
    EditorSyncResponse,
    EditorHistoryResponse
)
from app.core.exceptions import SessionNotFoundException, SessionConflictException
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/sessions", tags=["会话管理"])


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建新会话",
    description="创建一个新的学习会话，支持自动模式检测"
)
async def create_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_db)
) -> SessionResponse:
    """创建新会话"""
    try:
        manager = SessionManager(db)

        # 创建会话
        session = await manager.create_session(
            user_id=request.user_id,
            mode=request.mode,
            title=request.title,
            grade_level=request.grade_level,
            subject=request.subject
        )

        # 构建WebSocket URL
        ws_url = f"ws://localhost:8000/ws/session/{session.session_id}"

        return SessionResponse(
            session_id=str(session.session_id),
            mode=session.mode,
            status=session.status,
            created_at=session.created_at,
            ws_url=ws_url
        )

    except Exception as e:
        logger.error(f"创建会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建会话失败: {str(e)}"
        )


@router.get(
    "/{session_id}",
    response_model=SessionDetailResponse,
    summary="获取会话详情",
    description="获取指定会话的详细信息"
)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> SessionDetailResponse:
    """获取会话详情"""
    try:
        manager = SessionManager(db)
        session = await manager.get_session(session_id)

        return SessionDetailResponse(
            session_id=str(session.session_id),
            user_id=session.user_id,
            mode=session.mode,
            title=session.title,
            grade_level=session.grade_level,
            status=session.status,
            statistics={
                "total_interactions": session.total_interactions,
                "ai_calls": session.total_ai_calls,
                "tokens_used": session.total_tokens_used
            },
            created_at=session.created_at,
            updated_at=session.updated_at
        )

    except SessionNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话失败: {str(e)}"
        )


@router.get(
    "",
    response_model=SessionListResponse,
    summary="获取会话列表",
    description="获取用户的会话列表，支持分页和筛选"
)
async def get_session_list(
    user_id: str,
    session_status: Optional[str] = None,
    mode: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
) -> SessionListResponse:
    """获取会话列表"""
    try:
        manager = SessionManager(db)
        sessions, total = await manager.get_session_list(
            user_id=user_id,
            status=session_status,
            mode=mode,
            page=page,
            limit=limit
        )

        # 构建响应
        session_list = []
        for session in sessions:
            # 获取内容预览
            preview = ""
            try:
                from app.cache.cache_strategies import session_cache
                cached_content = await session_cache.get_content(str(session.session_id))
                if cached_content and cached_content.get("content"):
                    content = cached_content.get("content", "")
                    # 截取前100个字符作为预览，去除多余空白
                    preview = content.strip()[:100]
                    if len(content) > 100:
                        preview += "..."
            except Exception as e:
                logger.debug(f"获取会话预览失败: {str(e)}")
                preview = ""

            session_list.append({
                "session_id": str(session.session_id),
                "title": session.title,
                "mode": session.mode,
                "status": session.status,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "preview": preview
            })

        total_pages = (total + limit - 1) // limit

        return SessionListResponse(
            sessions=session_list,
            pagination={
                "page": page,
                "page_size": limit,
                "total": total,
                "total_pages": total_pages
            }
        )

    except Exception as e:
        logger.error(f"获取会话列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话列表失败: {str(e)}"
        )


@router.patch(
    "/{session_id}",
    response_model=SessionDetailResponse,
    summary="更新会话信息",
    description="更新会话的标题、状态或模式"
)
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    db: AsyncSession = Depends(get_db)
) -> SessionDetailResponse:
    """更新会话信息"""
    try:
        manager = SessionManager(db)

        # 准备更新数据
        updates = {}
        if request.title is not None:
            updates["title"] = request.title
        if request.status is not None:
            updates["status"] = request.status
        if request.mode is not None:
            updates["mode"] = request.mode

        # 更新会话
        session = await manager.update_session(session_id, **updates)

        return SessionDetailResponse(
            session_id=str(session.session_id),
            user_id=session.user_id,
            mode=session.mode,
            title=session.title,
            grade_level=session.grade_level,
            status=session.status,
            statistics={
                "total_interactions": session.total_interactions,
                "ai_calls": session.total_ai_calls,
                "tokens_used": session.total_tokens_used
            },
            created_at=session.created_at,
            updated_at=session.updated_at
        )

    except SessionNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"更新会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新会话失败: {str(e)}"
        )


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除会话",
    description="软删除指定会话"
)
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> None:
    """删除会话"""
    try:
        manager = SessionManager(db)
        await manager.delete_session(session_id)

    except SessionNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"删除会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除会话失败: {str(e)}"
        )


@router.post(
    "/{session_id}/editor/sync",
    response_model=EditorSyncResponse,
    summary="同步编辑器状态",
    description="同步编辑器内容和光标位置"
)
async def sync_editor(
    session_id: str,
    request: SyncEditorRequest,
    db: AsyncSession = Depends(get_db)
) -> EditorSyncResponse:
    """同步编辑器状态"""
    try:
        manager = SessionManager(db)

        # 同步编辑器状态
        editor_state = await manager.sync_editor_state(
            session_id=session_id,
            content=request.content,
            cursor_position=request.cursor_position.dict() if request.cursor_position else None,
            selections=[s.dict() for s in request.selections] if request.selections else None,
            version=request.version
        )

        return EditorSyncResponse(
            version=editor_state.version,
            saved=True,
            content_hash=editor_state.content_hash,
            word_count=editor_state.word_count
        )

    except SessionNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except SessionConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"同步编辑器状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步编辑器状态失败: {str(e)}"
        )


@router.post(
    "/{session_id}/restore",
    response_model=EditorSyncResponse,
    summary="恢复会话到指定版本",
    description="将会话的编辑器内容恢复到历史版本"
)
async def restore_session(
    session_id: str,
    request: RestoreSessionRequest,
    db: AsyncSession = Depends(get_db)
) -> EditorSyncResponse:
    """
    恢复会话到指定版本

    功能：
    1. 验证目标版本是否存在
    2. 加载目标版本的内容
    3. 创建新版本（不是真的回退，而是创建新版本）
    4. 更新编辑器状态
    5. 清除相关缓存
    """
    try:
        manager = SessionManager(db)

        # 验证会话存在
        session = await manager.get_session(session_id)

        # 执行版本恢复
        editor_state = await manager.rollback_to_version(
            session_id=session_id,
            target_version=request.version
        )

        logger.info(
            f"会话版本恢复成功: session={session_id}, "
            f"target_version={request.version}, new_version={editor_state.version}"
        )

        return EditorSyncResponse(
            version=editor_state.version,
            saved=True,
            content_hash=editor_state.content_hash,
            word_count=editor_state.word_count
        )

    except SessionNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        # 版本不存在或无效
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"版本恢复失败: {str(e)}"
        )
    except Exception as e:
        logger.error(f"版本恢复失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"版本恢复失败: {str(e)}"
        )


@router.get(
    "/{session_id}/editor/history",
    response_model=EditorHistoryResponse,
    summary="获取编辑历史",
    description="获取会话的编辑历史记录，支持版本范围查询"
)
async def get_editor_history(
    session_id: str,
    from_version: Optional[int] = None,
    to_version: Optional[int] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
) -> EditorHistoryResponse:
    """
    获取编辑历史

    功能：
    1. 查询指定版本范围的编辑历史
    2. 支持分页限制
    3. 返回每个版本的内容和变更信息
    4. 按版本号倒序排列（最新的在前）

    参数：
    - from_version: 起始版本号（可选）
    - to_version: 结束版本号（可选）
    - limit: 返回数量限制（默认50）
    """
    try:
        manager = SessionManager(db)

        # 验证会话存在
        session = await manager.get_session(session_id)

        # 获取版本历史
        history = await manager.get_editor_history(
            session_id=session_id,
            from_version=from_version,
            to_version=to_version,
            limit=limit
        )

        # 构建响应
        history_items = []
        for editor_state in history:
            history_items.append({
                "version": editor_state.version,
                "content": editor_state.content,
                "change_type": editor_state.change_type,
                "changed_range": editor_state.changed_range,
                "timestamp": editor_state.timestamp.isoformat() if editor_state.timestamp else None
            })

        logger.info(
            f"获取编辑历史成功: session={session_id}, "
            f"from={from_version}, to={to_version}, count={len(history_items)}"
        )

        return EditorHistoryResponse(
            history=history_items
        )

    except SessionNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取编辑历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取编辑历史失败: {str(e)}"
        )
