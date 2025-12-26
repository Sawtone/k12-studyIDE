"""
ErrorAnnotation Repository
错误标注数据访问层
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.database.models import ErrorAnnotation
from app.core.logging import get_logger

logger = get_logger(__name__)


class ErrorAnnotationRepository:
    """
    错误标注Repository

    职责：
    1. 保存语法检查发现的错误
    2. 查询会话的错误标注
    3. 更新错误状态（接受/拒绝）
    4. 统计错误类型分布
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_annotation(
        self,
        session_id: str,
        content_version: int,
        error_type: str,
        severity: str,
        start_pos: int,
        end_pos: int,
        original_text: str,
        suggestion: Optional[str] = None,
        explanation: Optional[str] = None,
        confidence: Optional[float] = None,
        line_number: Optional[int] = None
    ) -> ErrorAnnotation:
        """
        保存错误标注

        Args:
            session_id: 会话ID
            content_version: 内容版本号
            error_type: 错误类型（typo, grammar, syntax, style）
            severity: 严重程度（low, medium, high）
            start_pos: 起始位置
            end_pos: 结束位置
            original_text: 原始文本
            suggestion: 建议修改
            explanation: 错误解释
            confidence: 置信度（0-1）
            line_number: 行号

        Returns:
            ErrorAnnotation对象
        """
        try:
            annotation = ErrorAnnotation(
                session_id=session_id,
                content_version=content_version,
                error_type=error_type,
                severity=severity,
                start_pos=start_pos,
                end_pos=end_pos,
                original_text=original_text,
                suggestion=suggestion,
                explanation=explanation,
                confidence=confidence,
                line_number=line_number,
                status='pending'
            )

            self.db.add(annotation)
            await self.db.flush()
            await self.db.refresh(annotation)

            logger.info(f"保存错误标注: session={session_id}, type={error_type}, pos={start_pos}-{end_pos}")

            return annotation

        except Exception as e:
            logger.error(f"保存错误标注失败: {str(e)}")
            raise

    async def batch_save_annotations(
        self,
        session_id: str,
        content_version: int,
        annotations: List[Dict[str, Any]]
    ) -> List[ErrorAnnotation]:
        """
        批量保存错误标注

        Args:
            session_id: 会话ID
            content_version: 内容版本号
            annotations: 标注列表

        Returns:
            ErrorAnnotation对象列表
        """
        try:
            saved_annotations = []

            for ann_data in annotations:
                annotation = ErrorAnnotation(
                    session_id=session_id,
                    content_version=content_version,
                    error_type=ann_data.get('error_type', 'unknown'),
                    severity=ann_data.get('severity', 'medium'),
                    start_pos=ann_data['start_pos'],
                    end_pos=ann_data['end_pos'],
                    original_text=ann_data['original_text'],
                    suggestion=ann_data.get('suggestion'),
                    explanation=ann_data.get('explanation'),
                    confidence=ann_data.get('confidence'),
                    line_number=ann_data.get('line_number'),
                    status='pending'
                )
                self.db.add(annotation)
                saved_annotations.append(annotation)

            await self.db.flush()

            logger.info(f"批量保存错误标注: session={session_id}, count={len(annotations)}")

            return saved_annotations

        except Exception as e:
            logger.error(f"批量保存错误标注失败: {str(e)}")
            raise

    async def get_annotations_by_version(
        self,
        session_id: str,
        content_version: int,
        status: Optional[str] = None
    ) -> List[ErrorAnnotation]:
        """
        获取指定版本的错误标注

        Args:
            session_id: 会话ID
            content_version: 内容版本号
            status: 状态过滤（可选）

        Returns:
            ErrorAnnotation列表
        """
        try:
            query = select(ErrorAnnotation).where(
                ErrorAnnotation.session_id == session_id,
                ErrorAnnotation.content_version == content_version
            )

            if status:
                query = query.where(ErrorAnnotation.status == status)

            query = query.order_by(ErrorAnnotation.start_pos)

            result = await self.db.execute(query)
            annotations = result.scalars().all()

            return list(annotations)

        except Exception as e:
            logger.error(f"获取错误标注失败: {str(e)}")
            raise

    async def get_annotation_by_id(
        self,
        annotation_id: int
    ) -> Optional[ErrorAnnotation]:
        """
        根据ID获取错误标注

        Args:
            annotation_id: 标注ID

        Returns:
            ErrorAnnotation对象或None
        """
        try:
            query = select(ErrorAnnotation).where(ErrorAnnotation.id == annotation_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"获取错误标注失败: {str(e)}")
            raise

    async def update_status(
        self,
        annotation_id: int,
        status: str,
        user_action: Optional[str] = None,
        user_feedback: Optional[str] = None
    ) -> None:
        """
        更新错误标注状态

        Args:
            annotation_id: 标注ID
            status: 新状态（accepted, rejected, ignored）
            user_action: 用户操作（applied, modified, dismissed）
            user_feedback: 用户反馈
        """
        try:
            update_data = {
                'status': status,
                'resolved_at': datetime.utcnow()
            }

            if user_action:
                update_data['user_action'] = user_action

            if user_feedback:
                update_data['user_feedback'] = user_feedback

            stmt = update(ErrorAnnotation).where(
                ErrorAnnotation.id == annotation_id
            ).values(**update_data)

            await self.db.execute(stmt)

            logger.info(f"更新错误标注状态: id={annotation_id}, status={status}")

        except Exception as e:
            logger.error(f"更新错误标注状态失败: {str(e)}")
            raise

    async def delete_annotations_by_version(
        self,
        session_id: str,
        content_version: int
    ) -> int:
        """
        删除指定版本的所有错误标注

        Args:
            session_id: 会话ID
            content_version: 内容版本号

        Returns:
            删除的数量
        """
        try:
            stmt = delete(ErrorAnnotation).where(
                ErrorAnnotation.session_id == session_id,
                ErrorAnnotation.content_version == content_version
            )

            result = await self.db.execute(stmt)
            deleted_count = result.rowcount

            logger.info(f"删除错误标注: session={session_id}, version={content_version}, count={deleted_count}")

            return deleted_count

        except Exception as e:
            logger.error(f"删除错误标注失败: {str(e)}")
            raise

    async def get_error_statistics(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        获取错误统计信息

        Args:
            session_id: 会话ID

        Returns:
            统计信息字典
        """
        try:
            from sqlalchemy import func

            # 按错误类型统计
            type_query = select(
                ErrorAnnotation.error_type,
                func.count(ErrorAnnotation.id).label('count')
            ).where(
                ErrorAnnotation.session_id == session_id
            ).group_by(ErrorAnnotation.error_type)

            type_result = await self.db.execute(type_query)
            type_stats = {row.error_type: row.count for row in type_result}

            # 按状态统计
            status_query = select(
                ErrorAnnotation.status,
                func.count(ErrorAnnotation.id).label('count')
            ).where(
                ErrorAnnotation.session_id == session_id
            ).group_by(ErrorAnnotation.status)

            status_result = await self.db.execute(status_query)
            status_stats = {row.status: row.count for row in status_result}

            # 总数
            total_query = select(func.count(ErrorAnnotation.id)).where(
                ErrorAnnotation.session_id == session_id
            )
            total_result = await self.db.execute(total_query)
            total = total_result.scalar()

            return {
                'total': total,
                'by_type': type_stats,
                'by_status': status_stats
            }

        except Exception as e:
            logger.error(f"获取错误统计失败: {str(e)}")
            raise
