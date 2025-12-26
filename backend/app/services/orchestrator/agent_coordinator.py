"""
Agent协调器
负责Agent选择、调度、执行管理和结果聚合
"""

import asyncio
from typing import Dict, Any, List, Optional
from enum import Enum

from app.core.logging import get_logger
from app.core.exceptions import AgentNotFoundException, AgentExecutionException
from app.services.agents.base import BaseAgent, AgentResult
from app.services.agents.literature.grammar_checker import GrammarCheckerAgent
from app.services.agents.literature.polish_agent import PolishAgent
from app.services.agents.literature.structure_analyzer import StructureAnalyzerAgent
from app.services.agents.literature.health_scorer import HealthScorerAgent
from app.services.agents.science.math_validator import MathValidatorAgent
from app.services.agents.science.logic_tree_builder import LogicTreeBuilderAgent
from app.services.agents.science.debugger_agent import DebuggerAgent
from app.services.agents.common.chat_agent import ChatAgent
from app.services.agents.common.ocr_agent import OCRAgent
from app.cache.cache_strategies import agent_lock_manager

logger = get_logger(__name__)


class AgentType(str, Enum):
    """Agent类型枚举"""
    GRAMMAR_CHECKER = "grammar_checker"
    POLISH = "polish"
    STRUCTURE_ANALYZER = "structure_analyzer"
    HEALTH_SCORER = "health_scorer"
    MATH_VALIDATOR = "math_validator"
    LOGIC_TREE_BUILDER = "logic_tree_builder"
    DEBUGGER = "debugger"
    CHAT = "chat"
    OCR = "ocr"


class AgentCoordinator:
    """
    Agent协调器

    职责：
    1. Agent注册和管理
    2. Agent选择和路由
    3. Agent执行管理
    4. 结果聚合
    5. 错误处理和重试
    """

    def __init__(self) -> None:
        """初始化Agent协调器"""
        self.agents: Dict[str, type[BaseAgent]] = {}
        self._register_agents()
        logger.info("Agent协调器已初始化")

    def _register_agents(self) -> None:
        """注册所有Agent"""
        # 文科模式Agents
        self.agents[AgentType.GRAMMAR_CHECKER] = GrammarCheckerAgent
        self.agents[AgentType.POLISH] = PolishAgent
        self.agents[AgentType.STRUCTURE_ANALYZER] = StructureAnalyzerAgent
        self.agents[AgentType.HEALTH_SCORER] = HealthScorerAgent

        # 理科模式Agents
        self.agents[AgentType.MATH_VALIDATOR] = MathValidatorAgent
        self.agents[AgentType.LOGIC_TREE_BUILDER] = LogicTreeBuilderAgent
        self.agents[AgentType.DEBUGGER] = DebuggerAgent

        # 通用Agents
        self.agents[AgentType.CHAT] = ChatAgent
        self.agents[AgentType.OCR] = OCRAgent

        logger.info(f"已注册 {len(self.agents)} 个Agent")

    def get_agent(self, agent_type: str, **kwargs: Any) -> BaseAgent:
        """
        获取Agent实例

        Args:
            agent_type: Agent类型
            **kwargs: Agent初始化参数

        Returns:
            Agent实例

        Raises:
            AgentNotFoundException: Agent不存在
        """
        if agent_type not in self.agents:
            raise AgentNotFoundException(agent_type)

        agent_class = self.agents[agent_type]
        return agent_class(**kwargs)

    async def execute_agent(
        self,
        agent_type: str,
        session_id: str,
        request_id: str,
        agent_kwargs: Optional[Dict[str, Any]] = None,
        **input_kwargs: Any
    ) -> AgentResult:
        """
        执行单个Agent

        Args:
            agent_type: Agent类型
            session_id: 会话ID
            request_id: 请求ID
            agent_kwargs: Agent初始化参数
            **input_kwargs: Agent执行参数

        Returns:
            Agent执行结果
        """
        agent_kwargs = agent_kwargs or {}

        # 尝试获取执行锁
        lock_acquired = await agent_lock_manager.acquire_lock(
            session_id=session_id,
            agent_name=agent_type,
            request_id=request_id
        )

        if not lock_acquired:
            logger.warning(f"Agent {agent_type} 正在执行中，跳过本次请求")
            return AgentResult(
                success=False,
                data=None,
                error="Agent正在执行中，请稍后再试",
                metadata={"agent": agent_type, "locked": True}
            )

        try:
            # 创建Agent实例
            agent = self.get_agent(agent_type, **agent_kwargs)

            # 执行Agent
            logger.info(f"开始执行Agent: {agent_type}, 会话: {session_id}")
            result = await agent.run(**input_kwargs)

            logger.info(
                f"Agent执行完成: {agent_type}, 成功: {result.success}, "
                f"耗时: {result.metadata.get('execution_time_ms', 0):.2f}ms"
            )

            return result

        except Exception as e:
            logger.error(f"Agent执行失败: {agent_type}, 错误: {str(e)}")
            return AgentResult(
                success=False,
                data=None,
                error=str(e),
                metadata={"agent": agent_type}
            )

        finally:
            # 释放锁
            await agent_lock_manager.release_lock(
                session_id=session_id,
                agent_name=agent_type,
                request_id=request_id
            )

    async def execute_agent_chain(
        self,
        agents: List[tuple[str, Dict[str, Any]]],
        session_id: str,
        request_id: str,
        initial_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        串行执行多个Agent

        Args:
            agents: Agent列表 [(agent_type, agent_kwargs), ...]
            session_id: 会话ID
            request_id: 请求ID
            initial_input: 初始输入

        Returns:
            所有Agent的执行结果
        """
        results = {}
        current_input = initial_input.copy()

        for agent_type, agent_kwargs in agents:
            logger.info(f"执行Agent链: {agent_type}")

            # 执行Agent
            result = await self.execute_agent(
                agent_type=agent_type,
                session_id=session_id,
                request_id=f"{request_id}_{agent_type}",
                agent_kwargs=agent_kwargs,
                **current_input
            )

            # 保存结果
            results[agent_type] = result

            # 如果失败，终止链式执行
            if not result.success:
                logger.warning(f"Agent链执行失败: {agent_type}, 终止后续执行")
                break

            # 将当前结果作为下一个Agent的输入
            if result.data:
                current_input.update(result.data)

        return results

    async def execute_parallel_agents(
        self,
        agents: List[tuple[str, Dict[str, Any], Dict[str, Any]]],
        session_id: str,
        request_id: str
    ) -> Dict[str, AgentResult]:
        """
        并行执行多个Agent

        Args:
            agents: Agent列表 [(agent_type, agent_kwargs, input_kwargs), ...]
            session_id: 会话ID
            request_id: 请求ID

        Returns:
            所有Agent的执行结果
        """
        logger.info(f"并行执行 {len(agents)} 个Agent")

        # 创建所有Agent的执行任务
        tasks = []
        agent_types = []

        for agent_type, agent_kwargs, input_kwargs in agents:
            task = self.execute_agent(
                agent_type=agent_type,
                session_id=session_id,
                request_id=f"{request_id}_{agent_type}",
                agent_kwargs=agent_kwargs,
                **input_kwargs
            )
            tasks.append(task)
            agent_types.append(agent_type)

        # 并行执行所有任务
        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        # 组织结果
        results = {}
        for agent_type, result in zip(agent_types, results_list):
            if isinstance(result, Exception):
                logger.error(f"Agent {agent_type} 执行异常: {str(result)}")
                results[agent_type] = AgentResult(
                    success=False,
                    data=None,
                    error=str(result),
                    metadata={"agent": agent_type}
                )
            else:
                results[agent_type] = result

        logger.info(f"并行执行完成，成功: {sum(1 for r in results.values() if r.success)}/{len(agents)}")

        return results

    async def route_and_execute(
        self,
        task_type: str,
        session_id: str,
        request_id: str,
        context: Dict[str, Any],
        **kwargs: Any
    ) -> AgentResult:
        """
        根据任务类型路由并执行Agent

        Args:
            task_type: 任务类型
            session_id: 会话ID
            request_id: 请求ID
            context: 上下文信息
            **kwargs: 其他参数

        Returns:
            Agent执行结果
        """
        # 任务类型到Agent的映射
        task_agent_map = {
            "grammar_check": AgentType.GRAMMAR_CHECKER,
            "polish": AgentType.POLISH,
            "structure_analysis": AgentType.STRUCTURE_ANALYZER,
            "health_score": AgentType.HEALTH_SCORER,
            "math_validation": AgentType.MATH_VALIDATOR,
            "logic_tree": AgentType.LOGIC_TREE_BUILDER,
            "chat": AgentType.CHAT,
            "ocr": AgentType.OCR
        }

        agent_type = task_agent_map.get(task_type)
        if not agent_type:
            raise AgentNotFoundException(task_type)

        # 准备Agent初始化参数
        agent_kwargs = {}
        if "grade_level" in context:
            agent_kwargs["grade_level"] = context["grade_level"]
        if "mode" in context:
            agent_kwargs["mode"] = context["mode"]
        if "subject" in context:
            agent_kwargs["subject"] = context["subject"]

        # 执行Agent
        return await self.execute_agent(
            agent_type=agent_type,
            session_id=session_id,
            request_id=request_id,
            agent_kwargs=agent_kwargs,
            **kwargs
        )

    async def handle_agent_failure(
        self,
        agent_type: str,
        session_id: str,
        request_id: str,
        error: Exception,
        retry_count: int = 0,
        max_retries: int = 3
    ) -> AgentResult:
        """
        处理Agent执行失败

        功能：
        1. 判断错误类型（可重试 vs 不可重试）
        2. 实现重试机制（指数退避）
        3. 降级策略（使用简化版Agent或返回默认结果）
        4. 记录错误日志和指标
        5. 通知用户

        Args:
            agent_type: Agent类型
            session_id: 会话ID
            request_id: 请求ID
            error: 异常对象
            retry_count: 当前重试次数
            max_retries: 最大重试次数

        Returns:
            Agent执行结果（可能是降级结果）
        """
        from app.core.metrics import metrics_collector
        import asyncio

        error_str = str(error)
        error_type = type(error).__name__

        logger.error(
            f"Agent执行失败: agent={agent_type}, session={session_id}, "
            f"error_type={error_type}, error={error_str}, retry={retry_count}/{max_retries}"
        )

        # 记录错误指标
        metrics_collector.record_error(
            error_type=f"agent_failure_{agent_type}",
            error_code=error_type
        )

        # 判断是否可重试
        retryable_errors = [
            "TimeoutError",
            "ConnectionError",
            "RateLimitError",
            "ServiceUnavailableError"
        ]

        is_retryable = any(err in error_type for err in retryable_errors)

        # 如果可重试且未达到最大重试次数
        if is_retryable and retry_count < max_retries:
            # 计算退避时间（指数退避：2^retry_count 秒）
            backoff_time = 2 ** retry_count
            logger.info(f"将在 {backoff_time} 秒后重试 Agent: {agent_type}")

            await asyncio.sleep(backoff_time)

            # 重试执行
            try:
                result = await self.execute_agent(
                    agent_type=agent_type,
                    session_id=session_id,
                    request_id=f"{request_id}_retry_{retry_count + 1}",
                    agent_kwargs={}
                )

                if result.success:
                    logger.info(f"Agent重试成功: {agent_type}, retry={retry_count + 1}")
                    return result
                else:
                    # 重试仍然失败，继续降级处理
                    return await self.handle_agent_failure(
                        agent_type=agent_type,
                        session_id=session_id,
                        request_id=request_id,
                        error=Exception(result.error or "Unknown error"),
                        retry_count=retry_count + 1,
                        max_retries=max_retries
                    )

            except Exception as retry_error:
                # 重试过程中出现新错误
                return await self.handle_agent_failure(
                    agent_type=agent_type,
                    session_id=session_id,
                    request_id=request_id,
                    error=retry_error,
                    retry_count=retry_count + 1,
                    max_retries=max_retries
                )

        # 不可重试或已达到最大重试次数，执行降级策略
        logger.warning(f"Agent执行失败，执行降级策略: {agent_type}")

        # 降级策略：返回友好的错误信息和建议
        fallback_data = self._get_fallback_response(agent_type, error_str)

        return AgentResult(
            success=False,
            data=fallback_data,
            error=f"Agent执行失败: {error_str}",
            metadata={
                "agent": agent_type,
                "error_type": error_type,
                "retry_count": retry_count,
                "fallback": True
            }
        )

    def _get_fallback_response(self, agent_type: str, error: str) -> Dict[str, Any]:
        """
        获取降级响应

        Args:
            agent_type: Agent类型
            error: 错误信息

        Returns:
            降级响应数据
        """
        # 根据不同的Agent类型返回不同的降级响应
        fallback_responses = {
            "grammar_checker": {
                "errors": [],
                "message": "语法检查服务暂时不可用，请稍后再试",
                "suggestions": ["请检查网络连接", "稍后重新提交"]
            },
            "polish": {
                "versions": [],
                "message": "文本润色服务暂时不可用，请稍后再试",
                "suggestions": ["请检查网络连接", "稍后重新提交"]
            },
            "structure_analyzer": {
                "tree": {},
                "relationships": [],
                "message": "结构分析服务暂时不可用，请稍后再试"
            },
            "health_scorer": {
                "dimensions": {},
                "overall_score": 0,
                "message": "健康度评分服务暂时不可用，请稍后再试"
            },
            "math_validator": {
                "validation_results": [],
                "message": "数学验证服务暂时不可用，请稍后再试"
            },
            "logic_tree_builder": {
                "nodes": [],
                "edges": [],
                "message": "逻辑树构建服务暂时不可用，请稍后再试"
            },
            "debugger": {
                "execution_trace": [],
                "message": "调试服务暂时不可用，请稍后再试"
            },
            "chat": {
                "content": "抱歉，我现在无法回答您的问题。请稍后再试。",
                "message_type": "error"
            },
            "ocr": {
                "text": "",
                "regions": [],
                "message": "OCR识别服务暂时不可用，请稍后再试"
            }
        }

        return fallback_responses.get(agent_type, {
            "message": f"服务暂时不可用: {error}",
            "suggestions": ["请稍后重试"]
        })

    def get_agent_stats(self, agent_type: str) -> Dict[str, Any]:
        """
        获取Agent统计信息

        Args:
            agent_type: Agent类型

        Returns:
            统计信息
        """
        from app.core.metrics import metrics_collector

        # 从metrics_collector获取统计信息
        all_metrics = metrics_collector.get_metrics()
        agent_metrics = all_metrics.get("agent_calls", {}).get(agent_type, {})

        # 计算统计数据
        total_calls = agent_metrics.get("count", 0)
        success_count = agent_metrics.get("success", 0)
        total_time_ms = agent_metrics.get("total_time_ms", 0)
        total_tokens = agent_metrics.get("total_tokens", 0)

        # 计算成功率
        success_rate = (success_count / total_calls * 100) if total_calls > 0 else 0.0

        # 计算平均执行时间
        avg_execution_time_ms = (total_time_ms / total_calls) if total_calls > 0 else 0.0

        # 获取最近的错误信息
        error_count = agent_metrics.get("error", 0)
        recent_errors = []
        if error_count > 0:
            # 从错误指标中查找与此Agent相关的错误
            errors = all_metrics.get("errors", {})
            for error_key, count in errors.items():
                if agent_type in error_key:
                    recent_errors.append({
                        "error": error_key,
                        "count": count
                    })

        return {
            "agent_type": agent_type,
            "total_calls": total_calls,
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": round(success_rate, 2),
            "avg_execution_time_ms": round(avg_execution_time_ms, 2),
            "total_tokens": total_tokens,
            "recent_errors": recent_errors[:5]  # 最多返回5个最近的错误
        }


# 创建全局Agent协调器实例
agent_coordinator = AgentCoordinator()
