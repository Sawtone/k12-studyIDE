"""
理科模式API路由
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.orchestrator.agent_coordinator import agent_coordinator
from app.services.orchestrator.session_manager import SessionManager
from app.repositories.analysis_repo import AnalysisRepository
from app.schemas.request import (
    ValidateStepsRequest,
    BuildLogicTreeRequest,
    DecomposeStepsRequest,
    DebugRequest
)
from app.schemas.response import (
    ValidateStepsResponse,
    LogicTreeResponse,
    DecomposeStepsResponse,
    DebugResponse
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/science", tags=["理科模式"])


@router.post(
    "/steps/validate",
    response_model=ValidateStepsResponse,
    summary="验证数学步骤",
    description="验证数学解题步骤的正确性"
)
async def validate_steps(
    request: ValidateStepsRequest,
    db: AsyncSession = Depends(get_db)
) -> ValidateStepsResponse:
    """验证数学步骤"""
    try:
        # 获取会话信息
        session_manager = SessionManager(db)
        session = await session_manager.get_session(request.session_id)

        # 准备步骤数据
        steps = [
            {
                "step_number": step.step_number,
                "content": step.content,
                "formula": step.formula
            }
            for step in request.steps
        ]

        # 执行Agent
        result = await agent_coordinator.execute_agent(
            agent_type="math_validator",
            session_id=request.session_id,
            request_id=str(uuid.uuid4()),
            agent_kwargs={},
            problem_statement=request.problem_statement,
            steps=steps
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"步骤验证失败: {result.error}"
            )

        # 保存数学步骤
        analysis_repo = AnalysisRepository(db)
        if result.data.get("validation_results"):
            await analysis_repo.save_math_steps(
                session_id=request.session_id,
                content_version=1,
                steps=[
                    {
                        "step_number": v.get("step_number", 0),
                        "step_order": i,
                        "step_content": steps[i].get("content", ""),
                        "formula": steps[i].get("formula"),
                        "symbolic_form": v.get("symbolic_form"),
                        "variables_before": v.get("variables_state"),
                        "variables_after": v.get("variables_state"),
                        "is_valid": v.get("is_valid"),
                        "validation_details": v,
                        "errors": v.get("errors"),
                        "warnings": v.get("warnings"),
                        "next_step_hint": v.get("next_step_hint")
                    }
                    for i, v in enumerate(result.data["validation_results"])
                ]
            )

        return ValidateStepsResponse(**result.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"步骤验证失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"步骤验证失败: {str(e)}"
        )


@router.post(
    "/logic-tree/build",
    response_model=LogicTreeResponse,
    summary="构建逻辑推导树",
    description="分析问题并构建逻辑推导树"
)
async def build_logic_tree(
    request: BuildLogicTreeRequest,
    db: AsyncSession = Depends(get_db)
) -> LogicTreeResponse:
    """构建逻辑推导树"""
    try:
        # 获取会话信息
        session_manager = SessionManager(db)
        session = await session_manager.get_session(request.session_id)

        # 执行Agent
        result = await agent_coordinator.execute_agent(
            agent_type="logic_tree_builder",
            session_id=request.session_id,
            request_id=str(uuid.uuid4()),
            agent_kwargs={},
            problem_statement=request.problem_statement,
            existing_steps=request.existing_steps or []
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"逻辑树构建失败: {result.error}"
            )

        # 保存逻辑树节点
        analysis_repo = AnalysisRepository(db)
        if result.data.get("logic_tree", {}).get("nodes"):
            await analysis_repo.save_logic_tree_nodes(
                session_id=request.session_id,
                content_version=1,
                nodes=result.data["logic_tree"]["nodes"]
            )

        return LogicTreeResponse(**result.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"逻辑树构建失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"逻辑树构建失败: {str(e)}"
        )


@router.get(
    "/logic-tree/{session_id}",
    response_model=LogicTreeResponse,
    summary="获取逻辑树",
    description="获取已构建的逻辑推导树"
)
async def get_logic_tree(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> LogicTreeResponse:
    """获取逻辑树"""
    try:
        # 获取逻辑树节点
        analysis_repo = AnalysisRepository(db)
        nodes = await analysis_repo.get_logic_tree_nodes(session_id)

        if not nodes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到逻辑树"
            )

        # 构建响应
        return LogicTreeResponse(
            problem_analysis={
                "knowns": [],
                "target": {},
                "variables": []
            },
            logic_tree={
                "nodes": [
                    {
                        "id": node.node_id,
                        "type": node.node_type,
                        "content": node.content,
                        "symbolic": node.symbolic_form,
                        "depends_on": node.depends_on or [],
                        "required_by": node.required_by or [],
                        "status": node.status,
                        "reasoning": node.reasoning
                    }
                    for node in nodes
                ]
            },
            derivation_paths=[],
            suggestions=[]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取逻辑树失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取逻辑树失败: {str(e)}"
        )


@router.post(
    "/steps/decompose",
    response_model=DecomposeStepsResponse,
    summary="将题目拆解为步骤",
    description="使用AI将数学题目拆解为详细的解题步骤"
)
async def decompose_steps(
    request: DecomposeStepsRequest,
    db: AsyncSession = Depends(get_db)
) -> DecomposeStepsResponse:
    """
    将题目拆解为步骤

    功能：
    1. 分析题目的已知条件和目标
    2. 规划解题思路
    3. 生成详细的解题步骤
    4. 为每个步骤提供推理说明
    """
    try:
        # 获取会话信息
        session_manager = SessionManager(db)
        session = await session_manager.get_session(request.session_id)

        # 执行Math Validator Agent进行题目分解
        # 注意：这里复用math_validator，但传入特殊参数表示是分解模式
        result = await agent_coordinator.execute_agent(
            agent_type="math_validator",
            session_id=request.session_id,
            request_id=str(uuid.uuid4()),
            agent_kwargs={
                "mode": "decompose",  # 分解模式
                "grade_level": session.grade_level or "middle"
            },
            problem_statement=request.problem_text,
            steps=[]  # 空步骤列表，表示需要生成步骤
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"题目拆解失败: {result.error}"
            )

        # 从结果中提取拆解的步骤
        decomposed_steps = result.data.get("decomposed_steps", [])

        # 如果Agent返回的是validation_results格式，转换为decomposed_steps格式
        if not decomposed_steps and result.data.get("validation_results"):
            decomposed_steps = [
                {
                    "step_number": i + 1,
                    "content": step.get("step_content", ""),
                    "formulas": [step.get("formula", "")] if step.get("formula") else [],
                    "reasoning": step.get("next_step_hint", "")
                }
                for i, step in enumerate(result.data["validation_results"])
            ]

        logger.info(f"题目拆解成功: session={request.session_id}, steps={len(decomposed_steps)}")

        return DecomposeStepsResponse(
            steps=decomposed_steps
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"题目拆解失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"题目拆解失败: {str(e)}"
        )


@router.post(
    "/debug",
    response_model=DebugResponse,
    summary="断点调试",
    description="在指定步骤设置断点，追踪变量状态和执行过程"
)
async def debug_steps(
    request: DebugRequest,
    db: AsyncSession = Depends(get_db)
) -> DebugResponse:
    """
    断点调试

    功能：
    1. 在指定步骤设置断点
    2. 追踪从第1步到断点的所有变量状态变化
    3. 检查已使用和未使用的条件
    4. 提供调试洞察和建议
    5. 验证当前状态的正确性
    """
    try:
        # 获取会话信息
        session_manager = SessionManager(db)
        session = await session_manager.get_session(request.session_id)

        # 准备步骤数据
        steps = [
            {
                "step_number": step.step_number,
                "content": step.content,
                "formula": step.formula
            }
            for step in request.steps
        ]

        # 执行Debugger Agent
        result = await agent_coordinator.execute_agent(
            agent_type="debugger",
            session_id=request.session_id,
            request_id=str(uuid.uuid4()),
            agent_kwargs={
                "grade_level": session.grade_level or "middle"
            },
            problem_statement=request.problem_statement,
            steps=steps,
            breakpoint_step_number=request.breakpoint_step_number
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"断点调试失败: {result.error}"
            )

        # 保存调试会话到数据库
        analysis_repo = AnalysisRepository(db)

        # 获取断点对应的步骤ID（如果存在）
        breakpoint_step_id = None
        if request.breakpoint_step_number <= len(steps):
            # 这里简化处理，实际应该查询数据库获取step_id
            breakpoint_step_id = None

        # 保存调试会话
        await analysis_repo.save_debug_session(
            session_id=request.session_id,
            breakpoint_step_id=breakpoint_step_id,
            breakpoint_step_number=request.breakpoint_step_number,
            execution_trace=result.data.get("execution_trace", []),
            current_state=result.data.get("current_state", {}),
            insights=result.data.get("insights", []),
            warnings=result.data.get("warnings", []),
            next_actions=result.data.get("next_possible_actions", [])
        )

        logger.info(
            f"断点调试成功: session={request.session_id}, "
            f"breakpoint={request.breakpoint_step_number}"
        )

        return DebugResponse(
            execution_trace=result.data.get("execution_trace", []),
            current_state=result.data.get("current_state", {}),
            insights=result.data.get("insights", []),
            next_possible_actions=result.data.get("next_possible_actions", []),
            validation=result.data.get("validation", {})
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"断点调试失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"断点调试失败: {str(e)}"
        )
