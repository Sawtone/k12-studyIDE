"""
分析结果Repository
负责文科和理科分析结果的数据访问
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError

from app.database.models import LiteratureAnalysis, MathStep, LogicTreeNode, DebugSession
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnalysisRepository:
    """分析结果数据访问层"""

    def __init__(self, db: AsyncSession) -> None:
        """
        初始化Repository

        Args:
            db: 数据库会话
        """
        self.db = db

    async def save_literature_analysis(
        self,
        session_id: str,
        analysis_type: str,
        content_version: int,
        content_hash: str,
        results: Dict[str, Any],
        processing_time_ms: int,
        tokens_used: int,
        model_used: str
    ) -> LiteratureAnalysis:
        """
        保存文科分析结果

        Args:
            session_id: 会话ID
            analysis_type: 分析类型
            content_version: 内容版本
            content_hash: 内容哈希
            results: 分析结果
            processing_time_ms: 处理时间
            tokens_used: Token使用量
            model_used: 使用的模型

        Returns:
            分析结果对象
        """
        # 检查是否已存在相同的分析结果
        existing = await self.get_literature_analysis_by_hash(
            session_id=session_id,
            analysis_type=analysis_type,
            content_hash=content_hash
        )

        if existing:
            # 更新缓存命中次数
            existing.cache_hit_count += 1
            await self.db.commit()
            await self.db.refresh(existing)
            logger.info(f"更新分析结果缓存命中次数: {existing.id}")
            return existing

        # 创建新的分析结果
        analysis = LiteratureAnalysis(
            session_id=session_id,
            analysis_type=analysis_type,
            content_version=content_version,
            content_hash=content_hash,
            results=results,
            processing_time_ms=processing_time_ms,
            tokens_used=tokens_used,
            model_used=model_used,
            is_cached=False,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )

        self.db.add(analysis)

        try:
            await self.db.commit()
            await self.db.refresh(analysis)
            logger.info(f"保存文科分析结果: {analysis.id}, 类型: {analysis_type}")
            return analysis
        except IntegrityError:
            # 处理并发插入导致的唯一约束冲突
            await self.db.rollback()
            logger.info(f"检测到并发插入冲突，重新获取已存在的分析结果")

            # 重新查询已存在的记录
            existing = await self.get_literature_analysis_by_hash(
                session_id=session_id,
                analysis_type=analysis_type,
                content_hash=content_hash
            )

            if existing:
                # 更新缓存命中次数
                existing.cache_hit_count += 1
                await self.db.commit()
                await self.db.refresh(existing)
                logger.info(f"更新分析结果缓存命中次数: {existing.id}")
                return existing
            else:
                # 如果仍然找不到，说明可能是其他问题，重新抛出异常
                raise

    async def get_literature_analysis_by_hash(
        self,
        session_id: str,
        analysis_type: str,
        content_hash: str
    ) -> Optional[LiteratureAnalysis]:
        """
        根据内容哈希获取分析结果

        Args:
            session_id: 会话ID
            analysis_type: 分析类型
            content_hash: 内容哈希

        Returns:
            分析结果对象或None
        """
        result = await self.db.execute(
            select(LiteratureAnalysis).where(
                and_(
                    LiteratureAnalysis.session_id == session_id,
                    LiteratureAnalysis.analysis_type == analysis_type,
                    LiteratureAnalysis.content_hash == content_hash,
                    or_(
                        LiteratureAnalysis.expires_at.is_(None),
                        LiteratureAnalysis.expires_at > datetime.utcnow()
                    )
                )
            )
        )

        return result.scalar_one_or_none()

    async def get_literature_analysis_list(
        self,
        session_id: str,
        analysis_type: Optional[str] = None,
        limit: int = 10
    ) -> List[LiteratureAnalysis]:
        """
        获取会话的分析结果列表

        Args:
            session_id: 会话ID
            analysis_type: 分析类型（可选）
            limit: 限制数量

        Returns:
            分析结果列表
        """
        query = select(LiteratureAnalysis).where(
            LiteratureAnalysis.session_id == session_id
        )

        if analysis_type:
            query = query.where(LiteratureAnalysis.analysis_type == analysis_type)

        query = query.order_by(LiteratureAnalysis.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def save_math_steps(
        self,
        session_id: str,
        content_version: int,
        steps: List[Dict[str, Any]]
    ) -> List[MathStep]:
        """
        保存数学步骤

        Args:
            session_id: 会话ID
            content_version: 内容版本
            steps: 步骤列表

        Returns:
            保存的步骤对象列表
        """
        saved_steps = []

        for step_data in steps:
            step = MathStep(
                session_id=session_id,
                content_version=content_version,
                step_number=step_data.get("step_number", 0),
                step_order=step_data.get("step_order", 0),
                step_content=step_data.get("step_content", ""),
                formula=step_data.get("formula"),
                symbolic_form=step_data.get("symbolic_form"),
                variables_before=step_data.get("variables_before"),
                variables_after=step_data.get("variables_after"),
                variables_introduced=step_data.get("variables_introduced"),
                is_valid=step_data.get("is_valid"),
                validation_details=step_data.get("validation_details"),
                errors=step_data.get("errors"),
                warnings=step_data.get("warnings"),
                next_step_hint=step_data.get("next_step_hint"),
                start_pos=step_data.get("start_pos"),
                end_pos=step_data.get("end_pos")
            )

            self.db.add(step)
            saved_steps.append(step)

        await self.db.commit()

        for step in saved_steps:
            await self.db.refresh(step)

        logger.info(f"保存数学步骤: {len(saved_steps)}个, 会话: {session_id}")

        return saved_steps

    async def get_math_steps(
        self,
        session_id: str,
        content_version: Optional[int] = None
    ) -> List[MathStep]:
        """
        获取数学步骤

        Args:
            session_id: 会话ID
            content_version: 内容版本（可选）

        Returns:
            步骤列表
        """
        query = select(MathStep).where(MathStep.session_id == session_id)

        if content_version is not None:
            query = query.where(MathStep.content_version == content_version)

        query = query.order_by(MathStep.step_order)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def save_logic_tree_nodes(
        self,
        session_id: str,
        content_version: int,
        nodes: List[Dict[str, Any]]
    ) -> List[LogicTreeNode]:
        """
        保存逻辑树节点

        Args:
            session_id: 会话ID
            content_version: 内容版本
            nodes: 节点列表

        Returns:
            保存的节点对象列表
        """
        saved_nodes = []

        for node_data in nodes:
            node = LogicTreeNode(
                session_id=session_id,
                content_version=content_version,
                node_id=node_data.get("node_id", ""),
                node_type=node_data.get("node_type", "intermediate"),
                content=node_data.get("content", ""),
                symbolic_form=node_data.get("symbolic_form"),
                description=node_data.get("description"),
                level=node_data.get("level", 0),
                position=node_data.get("position"),
                depends_on=node_data.get("depends_on"),
                required_by=node_data.get("required_by"),
                status=node_data.get("status", "incomplete"),
                completion_percentage=node_data.get("completion_percentage"),
                reasoning=node_data.get("reasoning"),
                formula_used=node_data.get("formula_used")
            )

            self.db.add(node)
            saved_nodes.append(node)

        await self.db.commit()

        for node in saved_nodes:
            await self.db.refresh(node)

        logger.info(f"保存逻辑树节点: {len(saved_nodes)}个, 会话: {session_id}")

        return saved_nodes

    async def get_logic_tree_nodes(
        self,
        session_id: str,
        content_version: Optional[int] = None
    ) -> List[LogicTreeNode]:
        """
        获取逻辑树节点

        Args:
            session_id: 会话ID
            content_version: 内容版本（可选）

        Returns:
            节点列表
        """
        query = select(LogicTreeNode).where(LogicTreeNode.session_id == session_id)

        if content_version is not None:
            query = query.where(LogicTreeNode.content_version == content_version)

        query = query.order_by(LogicTreeNode.level, LogicTreeNode.id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def batch_create_literature_analyses(
        self,
        analyses: List[Dict[str, Any]]
    ) -> List[LiteratureAnalysis]:
        """
        批量创建文科分析结果

        Args:
            analyses: 分析结果列表

        Returns:
            创建的分析对象列表
        """
        try:
            analysis_objects = []

            for analysis_data in analyses:
                # 先检查是否已存在
                existing = await self.get_literature_analysis_by_hash(
                    session_id=analysis_data["session_id"],
                    analysis_type=analysis_data["analysis_type"],
                    content_hash=analysis_data["content_hash"]
                )

                if existing:
                    # 如果已存在，更新缓存命中次数
                    existing.cache_hit_count += 1
                    analysis_objects.append(existing)
                    logger.info(f"批量创建时发现已存在的分析结果: {existing.id}")
                else:
                    # 创建新的分析结果
                    analysis = LiteratureAnalysis(
                        session_id=analysis_data["session_id"],
                        analysis_type=analysis_data["analysis_type"],
                        content_version=analysis_data["content_version"],
                        content_hash=analysis_data["content_hash"],
                        results=analysis_data["results"],
                        processing_time_ms=analysis_data.get("processing_time_ms"),
                        tokens_used=analysis_data.get("tokens_used"),
                        model_used=analysis_data.get("model_used"),
                        is_cached=False
                    )
                    analysis_objects.append(analysis)
                    self.db.add(analysis)

            await self.db.commit()

            for analysis in analysis_objects:
                await self.db.refresh(analysis)

            logger.info(f"批量创建文科分析结果: {len(analysis_objects)} 个")

            return analysis_objects

        except IntegrityError as e:
            logger.error(f"批量创建文科分析结果时发生唯一约束冲突: {str(e)}")
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error(f"批量创建文科分析结果失败: {str(e)}")
            await self.db.rollback()
            raise

    async def batch_delete_analyses(
        self,
        session_id: str,
        analysis_ids: Optional[List[int]] = None
    ) -> int:
        """
        批量删除分析结果

        Args:
            session_id: 会话ID
            analysis_ids: 分析ID列表（可选，为空则删除该会话所有分析）

        Returns:
            删除的数量
        """
        try:
            from sqlalchemy import delete

            if analysis_ids:
                stmt = delete(LiteratureAnalysis).where(
                    and_(
                        LiteratureAnalysis.session_id == session_id,
                        LiteratureAnalysis.id.in_(analysis_ids)
                    )
                )
            else:
                stmt = delete(LiteratureAnalysis).where(
                    LiteratureAnalysis.session_id == session_id
                )

            result = await self.db.execute(stmt)
            deleted_count = result.rowcount

            await self.db.commit()

            logger.info(f"批量删除分析结果: {deleted_count} 个")

            return deleted_count

        except Exception as e:
            logger.error(f"批量删除分析结果失败: {str(e)}")
            await self.db.rollback()
            raise

    async def batch_update_math_steps(
        self,
        step_updates: List[Dict[str, Any]]
    ) -> int:
        """
        批量更新数学步骤

        Args:
            step_updates: 步骤更新列表，每个包含step_id和要更新的字段

        Returns:
            更新的步骤数量
        """
        try:
            updated_count = 0

            for update_data in step_updates:
                step_id = update_data.pop("step_id")

                stmt = select(MathStep).where(MathStep.id == step_id)
                result = await self.db.execute(stmt)
                step = result.scalar_one_or_none()

                if step:
                    for key, value in update_data.items():
                        if hasattr(step, key):
                            setattr(step, key, value)
                    updated_count += 1

            await self.db.commit()

            logger.info(f"批量更新数学步骤: {updated_count} 个")

            return updated_count

        except Exception as e:
            logger.error(f"批量更新数学步骤失败: {str(e)}")
            await self.db.rollback()
            raise

    async def save_debug_session(
        self,
        session_id: str,
        breakpoint_step_id: Optional[int] = None,
        breakpoint_step_number: Optional[int] = None,
        execution_trace: Optional[List[Dict[str, Any]]] = None,
        current_state: Optional[Dict[str, Any]] = None,
        insights: Optional[List[Dict[str, Any]]] = None,
        warnings: Optional[List[str]] = None,
        next_actions: Optional[List[str]] = None,
        **kwargs
    ) -> DebugSession:
        """
        保存调试会话

        Args:
            session_id: 会话ID
            breakpoint_step_id: 断点步骤ID
            breakpoint_step_number: 断点步骤号
            execution_trace: 执行追踪
            current_state: 当前状态
            insights: 洞察列表
            warnings: 警告列表
            next_actions: 下一步操作列表

        Returns:
            调试会话对象
        """
        try:
            debug_session = DebugSession(
                session_id=session_id,
                breakpoint_step_id=breakpoint_step_id,
                breakpoint_step_number=breakpoint_step_number,
                execution_trace=execution_trace or [],
                current_state=current_state or {},
                insights=insights or [],
                warnings=warnings or [],
                next_actions=next_actions or []
            )

            self.db.add(debug_session)
            await self.db.commit()
            await self.db.refresh(debug_session)

            logger.info(f"保存调试会话: {debug_session.id}, 会话: {session_id}")

            return debug_session

        except Exception as e:
            logger.error(f"保存调试会话失败: {str(e)}")
            await self.db.rollback()
            raise

    async def get_debug_sessions(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[DebugSession]:
        """
        获取调试会话列表

        Args:
            session_id: 会话ID
            limit: 限制数量

        Returns:
            调试会话列表
        """
        query = select(DebugSession).where(
            DebugSession.session_id == session_id
        ).order_by(DebugSession.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())
