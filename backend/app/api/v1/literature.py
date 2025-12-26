"""
文科模式API路由
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.orchestrator.agent_coordinator import agent_coordinator
from app.services.orchestrator.session_manager import SessionManager
from app.repositories.analysis_repo import AnalysisRepository
from app.schemas.request import (
    GrammarCheckRequest,
    PolishRequest,
    StructureAnalyzeRequest,
    HealthScoreRequest
)
from app.schemas.response import (
    GrammarCheckResponse,
    PolishResponse,
    StructureAnalyzeResponse,
    HealthScoreResponse
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/literature", tags=["文科模式"])


@router.post(
    "/check/grammar",
    response_model=GrammarCheckResponse,
    summary="语法检查",
    description="检查文章中的语法错误、错别字和病句"
)
async def check_grammar(
    request: GrammarCheckRequest,
    db: AsyncSession = Depends(get_db)
) -> GrammarCheckResponse:
    """语法检查"""
    try:
        # 获取会话信息
        session_manager = SessionManager(db)
        session = await session_manager.get_session(request.session_id)

        # 获取内容
        content = request.content
        if not content:
            # 从缓存获取最新内容
            from app.cache.cache_strategies import session_cache
            cached_content = await session_cache.get_content(request.session_id)
            if cached_content:
                content = cached_content.get("content", "")

        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未提供内容且缓存中无内容"
            )

        # 执行Agent
        result = await agent_coordinator.execute_agent(
            agent_type="grammar_checker",
            session_id=request.session_id,
            request_id=str(uuid.uuid4()),
            agent_kwargs={"grade_level": session.grade_level or "middle"},
            content=content,
            language=request.language,
            check_types=request.check_types,
            context=request.context
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"语法检查失败: {result.error}"
            )

        # 获取错误列表并确保每个错误都有 id 字段
        errors = result.data.get("errors", [])

        # 为缺少 id 的错误生成唯一 ID
        for i, error in enumerate(errors):
            if "id" not in error or not error.get("id"):
                error["id"] = f"err_{uuid.uuid4().hex[:8]}_{i}"

        # 获取内容版本和哈希
        import hashlib
        from app.cache.cache_strategies import session_cache

        cached_content = await session_cache.get_content(request.session_id)
        content_version = cached_content.get("version", 1) if cached_content else 1
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # 保存分析结果
        analysis_repo = AnalysisRepository(db)
        await analysis_repo.save_literature_analysis(
            session_id=request.session_id,
            analysis_type="grammar",
            content_version=content_version,
            content_hash=content_hash,
            results=result.data,
            processing_time_ms=int(result.metadata.get("execution_time_ms", 0)),
            tokens_used=result.metadata.get("tokens_used", 0),
            model_used=result.metadata.get("model", "")
        )

        return GrammarCheckResponse(
            errors=errors,
            processing_time_ms=int(result.metadata.get("execution_time_ms", 0)),
            from_cache=result.metadata.get("from_cache", False)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"语法检查失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语法检查失败: {str(e)}"
        )


@router.post(
    "/polish",
    response_model=PolishResponse,
    summary="文本润色",
    description="对文本进行润色，提供多个版本供选择"
)
async def polish_text(
    request: PolishRequest,
    db: AsyncSession = Depends(get_db)
) -> PolishResponse:
    """文本润色"""
    try:
        # 获取会话信息
        session_manager = SessionManager(db)
        session = await session_manager.get_session(request.session_id)

        # 执行Agent
        result = await agent_coordinator.execute_agent(
            agent_type="polish",
            session_id=request.session_id,
            request_id=str(uuid.uuid4()),
            agent_kwargs={},
            text=request.text,
            polish_direction=request.polish_direction,
            target_style=request.target_style,
            context=request.context,
            grade_level=session.grade_level or "middle"
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文本润色失败: {result.error}"
            )

        return PolishResponse(**result.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文本润色失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文本润色失败: {str(e)}"
        )


@router.get(
    "/structure/{session_id}",
    response_model=StructureAnalyzeResponse,
    summary="获取文章结构",
    description="分析文章的组织结构和逻辑关系"
)
async def get_structure(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> StructureAnalyzeResponse:
    """获取文章结构"""
    try:
        # 获取会话信息
        session_manager = SessionManager(db)
        session = await session_manager.get_session(session_id)

        # 从缓存获取内容
        from app.cache.cache_strategies import session_cache
        cached_content = await session_cache.get_content(session_id)
        if not cached_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缓存中无内容"
            )

        content = cached_content.get("content", "")

        # 执行Agent
        result = await agent_coordinator.execute_agent(
            agent_type="structure_analyzer",
            session_id=session_id,
            request_id=str(uuid.uuid4()),
            agent_kwargs={},
            content=content,
            grade_level=session.grade_level or "middle"
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"结构分析失败: {result.error}"
            )

        return StructureAnalyzeResponse(**result.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"结构分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"结构分析失败: {str(e)}"
        )


@router.get(
    "/health/{session_id}",
    response_model=HealthScoreResponse,
    summary="获取文章健康度",
    description="多维度评估文章质量"
)
async def get_health_score(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> HealthScoreResponse:
    """获取文章健康度"""
    try:
        # 获取会话信息
        session_manager = SessionManager(db)
        session = await session_manager.get_session(session_id)

        # 从缓存获取内容
        from app.cache.cache_strategies import session_cache
        cached_content = await session_cache.get_content(session_id)
        if not cached_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缓存中无内容"
            )

        content = cached_content.get("content", "")

        # 执行Agent
        result = await agent_coordinator.execute_agent(
            agent_type="health_scorer",
            session_id=session_id,
            request_id=str(uuid.uuid4()),
            agent_kwargs={},
            content=content,
            grade_level=session.grade_level or "middle"
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"健康度评分失败: {result.error}"
            )

        return HealthScoreResponse(**result.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"健康度评分失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"健康度评分失败: {str(e)}"
        )


@router.post(
    "/structure/analyze",
    response_model=StructureAnalyzeResponse,
    summary="重新分析文章结构",
    description="对文章进行结构分析，生成新的结构树"
)
async def analyze_structure(
    request: StructureAnalyzeRequest,
    db: AsyncSession = Depends(get_db)
) -> StructureAnalyzeResponse:
    """
    重新分析文章结构

    功能：
    1. 分析文章的组织结构
    2. 识别段落层次关系
    3. 构建文档结构树
    4. 保存结构数据到数据库
    5. 返回结构分析结果
    """
    try:
        # 获取会话信息
        session_manager = SessionManager(db)
        session = await session_manager.get_session(request.session_id)

        # 获取内容
        content = request.content
        if not content:
            # 从缓存获取最新内容
            from app.cache.cache_strategies import session_cache
            cached_content = await session_cache.get_content(request.session_id)
            if cached_content:
                content = cached_content.get("content", "")

        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未提供内容且缓存中无内容"
            )

        # 执行Structure Analyzer Agent
        result = await agent_coordinator.execute_agent(
            agent_type="structure_analyzer",
            session_id=request.session_id,
            request_id=str(uuid.uuid4()),
            agent_kwargs={},
            content=content,
            grade_level=session.grade_level or "middle"
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"结构分析失败: {result.error}"
            )

        # 获取内容版本和哈希
        import hashlib
        from app.cache.cache_strategies import session_cache

        cached_content = await session_cache.get_content(request.session_id)
        content_version = cached_content.get("version", 1) if cached_content else 1
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # 保存结构分析结果
        analysis_repo = AnalysisRepository(db)
        await analysis_repo.save_literature_analysis(
            session_id=request.session_id,
            analysis_type="structure",
            content_version=content_version,
            content_hash=content_hash,
            results=result.data,
            processing_time_ms=int(result.metadata.get("execution_time_ms", 0)),
            tokens_used=result.metadata.get("tokens_used", 0),
            model_used=result.metadata.get("model", "")
        )

        # 保存文档结构树
        if result.data.get("tree"):
            from app.repositories.document_structure_repo import DocumentStructureRepository
            structure_repo = DocumentStructureRepository(db)

            # 将树形结构转换为节点列表
            nodes = []

            def flatten_tree(node, parent_node_id=None, level=0, position=0):
                """递归展平树形结构"""
                node_data = {
                    "node_type": node.get("type", "section"),
                    "node_id": node.get("id", f"node_{len(nodes)}"),
                    "level": level,
                    "position_in_parent": position,
                    "content_summary": node.get("summary", ""),
                    "full_text": node.get("title", ""),
                    "start_pos": node.get("start_pos", 0),
                    "end_pos": node.get("end_pos", 0),
                    "analysis_data": {
                        "title": node.get("title"),
                        "summary": node.get("summary")
                    }
                }
                if parent_node_id:
                    node_data["parent_node_id"] = parent_node_id

                nodes.append(node_data)

                # 递归处理子节点
                if node.get("children"):
                    for i, child in enumerate(node["children"]):
                        flatten_tree(child, node_data["node_id"], level + 1, i)

            # 展平树形结构
            tree = result.data.get("tree", {})
            if tree:
                flatten_tree(tree)

                # 保存到数据库
                await structure_repo.save_structure_tree(
                    session_id=request.session_id,
                    content_version=1,
                    nodes=nodes
                )

        logger.info(f"结构分析成功: session={request.session_id}")

        return StructureAnalyzeResponse(**result.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"结构分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"结构分析失败: {str(e)}"
        )


@router.post(
    "/health/analyze",
    response_model=HealthScoreResponse,
    summary="重新评估文章健康度",
    description="对文章进行多维度质量评估，生成健康度报告"
)
async def analyze_health(
    request: HealthScoreRequest,
    db: AsyncSession = Depends(get_db)
) -> HealthScoreResponse:
    """
    重新评估文章健康度

    功能：
    1. 多维度评估文章质量
    2. 分析结构、连贯性、清晰度、语法、丰富度
    3. 生成整体评分和等级
    4. 提供改进建议
    5. 保存评估结果到数据库
    """
    try:
        # 获取会话信息
        session_manager = SessionManager(db)
        session = await session_manager.get_session(request.session_id)

        # 获取内容
        content = request.content
        if not content:
            # 从缓存获取最新内容
            from app.cache.cache_strategies import session_cache
            cached_content = await session_cache.get_content(request.session_id)
            if cached_content:
                content = cached_content.get("content", "")

        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未提供内容且缓存中无内容"
            )

        # 执行Health Scorer Agent
        result = await agent_coordinator.execute_agent(
            agent_type="health_scorer",
            session_id=request.session_id,
            request_id=str(uuid.uuid4()),
            agent_kwargs={},
            content=content,
            grade_level=session.grade_level or "middle"
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"健康度评估失败: {result.error}"
            )

        # 获取内容版本和哈希
        import hashlib
        from app.cache.cache_strategies import session_cache

        cached_content = await session_cache.get_content(request.session_id)
        content_version = cached_content.get("version", 1) if cached_content else 1
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # 保存健康度评估结果
        analysis_repo = AnalysisRepository(db)
        await analysis_repo.save_literature_analysis(
            session_id=request.session_id,
            analysis_type="health",
            content_version=content_version,
            content_hash=content_hash,
            results=result.data,
            processing_time_ms=int(result.metadata.get("execution_time_ms", 0)),
            tokens_used=result.metadata.get("tokens_used", 0),
            model_used=result.metadata.get("model", "")
        )

        logger.info(
            f"健康度评估成功: session={request.session_id}, "
            f"score={result.data.get('overall_score', 0)}"
        )

        return HealthScoreResponse(**result.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"健康度评估失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"健康度评估失败: {str(e)}"
        )
