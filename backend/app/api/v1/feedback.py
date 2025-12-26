"""
Feedback API路由
处理用户对AI建议的反馈
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.schemas.request import AcceptFeedbackRequest, RejectFeedbackRequest, ReportIssueRequest
from app.repositories.user_action_repo import UserActionRepository
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/feedback", tags=["用户反馈"])


@router.post(
    "/accept",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="接受AI建议",
    description="用户接受并应用AI的建议"
)
async def accept_feedback(
    request: AcceptFeedbackRequest,
    db: AsyncSession = Depends(get_db)
) -> None:
    """接受AI建议"""
    try:
        user_action_repo = UserActionRepository(db)

        # 记录用户操作
        await user_action_repo.record_action(
            session_id=request.session_id,
            action_type="accept_suggestion",
            target_type=request.target_type,
            target_id=request.target_id,
            action_data={
                "action": request.action,
                "modified_content": request.modified_content,
                "timestamp": "now"
            }
        )

        # 如果是错误标注，更新其状态
        if request.target_type == "error":
            from app.repositories.error_annotation_repo import ErrorAnnotationRepository
            error_repo = ErrorAnnotationRepository(db)
            await error_repo.update_status(
                annotation_id=int(request.target_id.replace("err_", "")),
                status="accepted",
                user_action=request.action
            )

        logger.info(f"用户接受建议: session={request.session_id}, target={request.target_id}")

    except Exception as e:
        logger.error(f"接受反馈失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"接受反馈失败: {str(e)}"
        )


@router.post(
    "/reject",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="拒绝AI建议",
    description="用户拒绝AI的建议"
)
async def reject_feedback(
    request: RejectFeedbackRequest,
    db: AsyncSession = Depends(get_db)
) -> None:
    """拒绝AI建议"""
    try:
        user_action_repo = UserActionRepository(db)

        # 记录用户操作
        await user_action_repo.record_action(
            session_id=request.session_id,
            action_type="reject_suggestion",
            target_type=request.target_type,
            target_id=request.target_id,
            action_data={
                "reason": request.reason,
                "comment": request.comment,
                "timestamp": "now"
            }
        )

        # 如果是错误标注，更新其状态
        if request.target_type == "error":
            from app.repositories.error_annotation_repo import ErrorAnnotationRepository
            error_repo = ErrorAnnotationRepository(db)
            await error_repo.update_status(
                annotation_id=int(request.target_id.replace("err_", "")),
                status="rejected",
                user_feedback=request.comment
            )

        logger.info(f"用户拒绝建议: session={request.session_id}, target={request.target_id}, reason={request.reason}")

    except Exception as e:
        logger.error(f"拒绝反馈失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"拒绝反馈失败: {str(e)}"
        )


@router.post(
    "/report",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="报告问题",
    description="用户报告系统问题或提供反馈"
)
async def report_issue(
    request: ReportIssueRequest,
    db: AsyncSession = Depends(get_db)
) -> None:
    """报告问题"""
    try:
        user_action_repo = UserActionRepository(db)

        # 记录问题报告
        await user_action_repo.record_action(
            session_id=request.session_id,
            action_type="report_issue",
            target_type="system",
            target_id=None,
            action_data={
                "issue_type": request.issue_type,
                "description": request.description,
                "context": request.context,
                "timestamp": "now"
            }
        )

        logger.warning(f"用户报告问题: session={request.session_id}, type={request.issue_type}, desc={request.description[:100]}")

        # 发送问题报告通知
        try:
            # 1. 记录到指标系统（用于监控和告警）
            from app.core.metrics import metrics_collector
            metrics_collector.record_issue_report(
                issue_type=request.issue_type,
                session_id=request.session_id
            )

            # 2. 如果是严重问题，记录到错误日志
            if request.issue_type in ["system_error", "data_loss", "security"]:
                logger.error(
                    f"严重问题报告: session={request.session_id}, "
                    f"type={request.issue_type}, desc={request.description}"
                )

            # 3. 可以在这里添加其他通知机制：
            # - 发送邮件给管理员
            # - 推送到Slack/钉钉等即时通讯工具
            # - 创建工单到问题追踪系统（如Jira、GitHub Issues）
            # - 触发PagerDuty等告警系统
            #
            # 示例：
            # if request.issue_type == "system_error":
            #     await send_admin_notification(
            #         title=f"系统错误报告 - {request.session_id}",
            #         content=request.description,
            #         priority="high"
            #     )

        except Exception as notify_error:
            # 通知失败不应该影响问题记录
            logger.error(f"发送问题通知失败: {str(notify_error)}")

    except Exception as e:
        logger.error(f"报告问题失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"报告问题失败: {str(e)}"
        )
