"""
Agent基类
定义所有Agent的统一接口和通用功能
"""

import time
import hashlib
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel

from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import AgentExecutionException, AgentTimeoutException
from app.services.llm.qwen_client import qwen_client, QwenResponse
from app.services.llm.model_router import model_router, TaskType
from app.cache.cache_strategies import analysis_cache
from app.core.metrics import metrics_collector

logger = get_logger(__name__)


class AgentConfig(BaseModel):
    """Agent配置"""
    name: str
    task_type: TaskType
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    timeout_seconds: int = settings.agent_timeout_seconds
    retry_attempts: int = settings.agent_retry_attempts
    enable_cache: bool = True
    cache_ttl: int = settings.cache_ttl_seconds


class AgentResult(BaseModel):
    """Agent执行结果"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BaseAgent(ABC):
    """
    Agent基类

    设计原则：
    1. 单一职责：每个Agent只做一件事
    2. 可组合：Agent可以串联或并联
    3. 可测试：输入输出明确
    4. 可观测：记录日志和指标

    子类需要实现：
    - system_prompt: 系统提示词
    - build_user_prompt: 构建用户提示词
    - parse_response: 解析AI响应
    """

    def __init__(self, config: AgentConfig) -> None:
        """
        初始化Agent

        Args:
            config: Agent配置
        """
        self.config = config
        self.llm = qwen_client
        self.logger = get_logger(f"agent.{config.name}")

        # 从模型路由器获取推荐参数
        self.model = model_router.select_model(config.task_type)
        self.temperature = config.temperature or model_router.get_recommended_temperature(config.task_type)
        self.max_tokens = config.max_tokens or model_router.get_recommended_max_tokens(config.task_type)

        self.logger.info(
            f"Agent初始化: {config.name}, model={self.model}, "
            f"temp={self.temperature}, max_tokens={self.max_tokens}"
        )

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """
        系统提示词
        定义Agent的角色和能力
        """
        pass

    @abstractmethod
    def build_user_prompt(self, **kwargs: Any) -> str:
        """
        构建用户提示词
        根据输入动态生成提示词

        Args:
            **kwargs: 输入参数

        Returns:
            用户提示词
        """
        pass

    @abstractmethod
    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        解析AI响应
        将AI返回的文本解析为结构化数据

        Args:
            response: AI响应文本

        Returns:
            解析后的结构化数据
        """
        pass

    def validate_inputs(self, **kwargs: Any) -> None:
        """
        验证输入参数
        子类可以覆盖以添加自定义验证

        Args:
            **kwargs: 输入参数

        Raises:
            ValueError: 参数验证失败
        """
        pass

    def generate_cache_key(self, **kwargs: Any) -> str:
        """
        生成缓存键

        Args:
            **kwargs: 输入参数

        Returns:
            缓存键
        """
        # 将输入参数序列化为JSON并计算哈希
        key_data = {
            "agent": self.config.name,
            "inputs": kwargs
        }
        key_json = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(key_json.encode()).hexdigest()

    async def get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        从缓存获取结果

        Args:
            cache_key: 缓存键

        Returns:
            缓存的结果，不存在返回None
        """
        if not self.config.enable_cache:
            return None

        try:
            # 从分析缓存获取
            cache_data = await analysis_cache.get_result(
                analysis_type=self.config.name,
                content=cache_key
            )
            if cache_data:
                self.logger.info(f"缓存命中: {self.config.name}")
                return cache_data.get("results")
        except Exception as e:
            self.logger.warning(f"获取缓存失败: {str(e)}")

        return None

    async def save_to_cache(self, cache_key: str, result: Dict[str, Any]) -> None:
        """
        保存结果到缓存

        Args:
            cache_key: 缓存键
            result: 结果数据
        """
        if not self.config.enable_cache:
            return

        try:
            await analysis_cache.set_result(
                analysis_type=self.config.name,
                content=cache_key,
                result=result,
                ttl=self.config.cache_ttl
            )
            self.logger.debug(f"结果已缓存: {self.config.name}")
        except Exception as e:
            self.logger.warning(f"保存缓存失败: {str(e)}")

    async def execute_llm(self, user_prompt: str) -> QwenResponse:
        """
        执行LLM调用

        Args:
            user_prompt: 用户提示词

        Returns:
            LLM响应

        Raises:
            AgentExecutionException: 执行失败
        """
        try:
            response = await self.llm.complete_with_retry(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                max_retries=self.config.retry_attempts
            )
            return response

        except Exception as e:
            self.logger.error(f"LLM调用失败: {str(e)}")
            raise AgentExecutionException(
                agent_name=self.config.name,
                reason=str(e)
            )

    async def run(self, **kwargs: Any) -> AgentResult:
        """
        执行Agent（模板方法）

        流程：
        1. 参数验证
        2. 检查缓存
        3. 构建提示词
        4. 执行LLM调用
        5. 解析结果
        6. 缓存结果
        7. 记录日志和指标
        8. 返回结果

        Args:
            **kwargs: 输入参数

        Returns:
            Agent执行结果
        """
        start_time = time.time()

        try:
            # 1. 参数验证
            self.validate_inputs(**kwargs)

            # 2. 检查缓存
            cache_key = self.generate_cache_key(**kwargs)
            cached_result = await self.get_from_cache(cache_key)

            if cached_result:
                execution_time_ms = (time.time() - start_time) * 1000
                return AgentResult(
                    success=True,
                    data=cached_result,
                    metadata={
                        "from_cache": True,
                        "execution_time_ms": execution_time_ms,
                        "agent": self.config.name
                    }
                )

            # 3. 构建提示词
            user_prompt = self.build_user_prompt(**kwargs)

            # 4. 执行LLM调用
            llm_response = await self.execute_llm(user_prompt)

            # 5. 解析结果
            parsed_result = self.parse_response(llm_response.content)

            # 6. 缓存结果
            await self.save_to_cache(cache_key, parsed_result)

            # 7. 记录指标
            execution_time_ms = (time.time() - start_time) * 1000
            metrics_collector.record_agent_call(
                agent_name=self.config.name,
                success=True,
                execution_time_ms=execution_time_ms,
                tokens_used=llm_response.tokens_used
            )

            self.logger.info(
                f"Agent执行成功: {self.config.name}, "
                f"time={execution_time_ms:.2f}ms, tokens={llm_response.tokens_used}"
            )

            # 8. 返回结果
            return AgentResult(
                success=True,
                data=parsed_result,
                metadata={
                    "from_cache": False,
                    "execution_time_ms": execution_time_ms,
                    "tokens_used": llm_response.tokens_used,
                    "model": llm_response.model,
                    "agent": self.config.name
                }
            )

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000

            # 记录失败指标
            metrics_collector.record_agent_call(
                agent_name=self.config.name,
                success=False,
                execution_time_ms=execution_time_ms,
                tokens_used=0
            )

            self.logger.error(f"Agent执行失败: {self.config.name}, error={str(e)}")

            return AgentResult(
                success=False,
                data=None,
                error=str(e),
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "agent": self.config.name
                }
            )
