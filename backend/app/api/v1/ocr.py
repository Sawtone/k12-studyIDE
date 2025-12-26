"""
OCR API路由
提供图片文字识别和手写识别功能
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.orchestrator.agent_coordinator import agent_coordinator
from app.schemas.response import OCRResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ocr", tags=["OCR"])


@router.post(
    "/image",
    response_model=OCRResponse,
    summary="图片OCR识别",
    description="识别图片中的文字内容，支持印刷体和手写体"
)
async def recognize_image(
    file: UploadFile = File(..., description="图片文件"),
    language: str = Form("zh", description="语言：zh（中文）或 en（英文）"),
    session_id: Optional[str] = Form(None, description="会话ID（可选）"),
    db: AsyncSession = Depends(get_db)
) -> OCRResponse:
    """图片OCR识别"""
    try:
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只支持图片文件"
            )

        # 验证文件大小（最大10MB）
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件过大（{file_size_mb:.2f}MB），最大支持10MB"
            )

        # 执行OCR Agent
        import uuid
        result = await agent_coordinator.execute_agent(
            agent_type="ocr",
            session_id=session_id or str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            agent_kwargs={
                "language": language
            },
            image_data=file_content,
            image_filename=file.filename
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OCR识别失败: {result.error}"
            )

        return OCRResponse(
            text=result.data.get('text', ''),
            confidence=result.data.get('confidence', 0.0),
            regions=result.data.get('regions', []),
            processing_time_ms=int(result.metadata.get('execution_time_ms', 0))
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图片OCR识别失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片OCR识别失败: {str(e)}"
        )


@router.post(
    "/handwriting",
    response_model=OCRResponse,
    summary="手写识别",
    description="识别手写文字，针对学生手写作业优化"
)
async def recognize_handwriting(
    file: UploadFile = File(..., description="图片文件"),
    language: str = Form("zh", description="语言：zh（中文）或 en（英文）"),
    session_id: Optional[str] = Form(None, description="会话ID（可选）"),
    db: AsyncSession = Depends(get_db)
) -> OCRResponse:
    """手写识别"""
    try:
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只支持图片文件"
            )

        # 验证文件大小（最大10MB）
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件过大（{file_size_mb:.2f}MB），最大支持10MB"
            )

        # 执行OCR Agent（手写模式）
        import uuid
        result = await agent_coordinator.execute_agent(
            agent_type="ocr",
            session_id=session_id or str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            agent_kwargs={
                "language": language,
                "mode": "handwriting"  # 手写模式
            },
            image_data=file_content,
            image_filename=file.filename
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"手写识别失败: {result.error}"
            )

        return OCRResponse(
            text=result.data.get('text', ''),
            confidence=result.data.get('confidence', 0.0),
            regions=result.data.get('regions', []),
            processing_time_ms=int(result.metadata.get('execution_time_ms', 0))
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"手写识别失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"手写识别失败: {str(e)}"
        )
