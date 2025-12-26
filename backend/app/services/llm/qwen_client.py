"""
Qwen API客户端
提供统一的Qwen模型调用接口
"""

import asyncio
import time
import json
from typing import Any, Dict, List, Optional, AsyncIterator, Type, Callable
from pydantic import BaseModel
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageToolCall

from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import (
    LLMAPIException,
    LLMRateLimitException,
    LLMTokenLimitException
)
from app.core.metrics import metrics_collector

logger = get_logger(__name__)


class QwenResponse(BaseModel):
    """Qwen响应模型"""
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    response_time_ms: float
    tool_calls: Optional[List[Dict[str, Any]]] = None


class QwenClient:
    """
    Qwen API客户端

    功能：
    1. 模型调用封装
    2. Token计数和成本控制
    3. 错误处理和重试
    4. 响应缓存
    5. 监控和日志
    """

    def __init__(self) -> None:
        """初始化Qwen客户端"""
        self.client = AsyncOpenAI(
            api_key=settings.qwen_api_key,
            base_url=settings.qwen_api_base
        )
        self.default_model = settings.qwen_text_model
        self.ocr_model = settings.qwen_ocr_model
        self.embedding_model = settings.qwen_embedding_model

        logger.info(f"Qwen客户端已初始化，默认模型: {self.default_model}")

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_schema: Optional[Type[BaseModel]] = None,
        **kwargs: Any
    ) -> QwenResponse:
        """
        执行文本补全请求

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            model: 模型名称，None使用默认模型
            temperature: 温度参数
            max_tokens: 最大token数
            response_schema: 响应schema（用于结构化输出）
            **kwargs: 其他参数

        Returns:
            Qwen响应对象

        Raises:
            LLMAPIException: API调用失败
            LLMRateLimitException: 速率限制
            LLMTokenLimitException: Token限制
        """
        model = model or self.default_model
        start_time = time.time()

        try:
            # 构建消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # 准备请求参数
            request_params: Dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }

            # 如果提供了schema，使用结构化输出
            if response_schema:
                request_params["response_format"] = {
                    "type": "json_object"
                }
                # 在system prompt中添加schema说明
                schema_instruction = f"\n\n请严格按照以下JSON schema返回结果：\n{response_schema.model_json_schema()}"
                messages[0]["content"] += schema_instruction

            logger.debug(f"调用Qwen API: model={model}, temp={temperature}, max_tokens={max_tokens}")

            # 调用API
            response: ChatCompletion = await self.client.chat.completions.create(**request_params)

            # 计算响应时间
            response_time_ms = (time.time() - start_time) * 1000

            # 提取响应内容
            content = response.choices[0].message.content or ""
            finish_reason = response.choices[0].finish_reason or "stop"

            # 获取token使用量
            tokens_used = 0
            if response.usage:
                tokens_used = response.usage.total_tokens

            # 记录指标
            metrics_collector.record_llm_call(
                model=model,
                tokens_used=tokens_used,
                response_time_ms=response_time_ms,
                success=True
            )

            logger.info(
                f"Qwen API调用成功: model={model}, tokens={tokens_used}, "
                f"time={response_time_ms:.2f}ms"
            )

            return QwenResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                finish_reason=finish_reason,
                response_time_ms=response_time_ms
            )

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000

            # 记录失败指标
            metrics_collector.record_llm_call(
                model=model,
                tokens_used=0,
                response_time_ms=response_time_ms,
                success=False
            )

            # 处理不同类型的错误
            error_message = str(e)

            if "rate_limit" in error_message.lower() or "429" in error_message:
                logger.warning(f"Qwen API速率限制: {error_message}")
                raise LLMRateLimitException()

            elif "token" in error_message.lower() and "limit" in error_message.lower():
                logger.error(f"Qwen API Token限制: {error_message}")
                raise LLMTokenLimitException(requested=max_tokens, limit=max_tokens)

            else:
                logger.error(f"Qwen API调用失败: {error_message}")
                raise LLMAPIException(reason=error_message)

    async def complete_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
        max_retries: int = 3,
        **kwargs: Any
    ) -> QwenResponse:
        """
        带重试的补全请求

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            max_retries: 最大重试次数
            **kwargs: 其他参数

        Returns:
            Qwen响应对象
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                return await self.complete(system_prompt, user_prompt, **kwargs)

            except LLMRateLimitException:
                # 速率限制不重试，直接抛出
                raise

            except Exception as e:
                last_exception = e

                if attempt < max_retries - 1:
                    # 指数退避
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Qwen API调用失败 (尝试 {attempt + 1}/{max_retries}), "
                        f"等待 {wait_time}秒后重试: {str(e)}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Qwen API调用失败，已达最大重试次数: {str(e)}")

        # 所有重试都失败
        if last_exception:
            raise last_exception
        else:
            raise LLMAPIException("未知错误")

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """
        流式补全请求

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Yields:
            响应文本片段
        """
        model = model or self.default_model
        start_time = time.time()

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            logger.debug(f"调用Qwen流式API: model={model}")

            # 调用流式API
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )

            total_tokens = 0
            full_content = ""

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    yield content

                # 尝试从chunk中获取usage信息
                if hasattr(chunk, 'usage') and chunk.usage:
                    total_tokens = chunk.usage.total_tokens

            # 如果没有usage信息，使用估算
            if total_tokens == 0:
                total_tokens = self.estimate_tokens(full_content)

            # 记录指标
            response_time_ms = (time.time() - start_time) * 1000
            metrics_collector.record_llm_call(
                model=model,
                tokens_used=total_tokens,
                response_time_ms=response_time_ms,
                success=True
            )

            logger.info(f"Qwen流式API调用完成: model={model}, time={response_time_ms:.2f}ms")

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            metrics_collector.record_llm_call(
                model=model,
                tokens_used=0,
                response_time_ms=response_time_ms,
                success=False
            )

            logger.error(f"Qwen流式API调用失败: {str(e)}")
            raise LLMAPIException(reason=str(e))

    async def create_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """
        创建文本嵌入

        Args:
            text: 文本内容
            model: 嵌入模型名称

        Returns:
            嵌入向量
        """
        model = model or self.embedding_model
        start_time = time.time()

        try:
            logger.debug(f"创建文本嵌入: model={model}, text_length={len(text)}")

            response = await self.client.embeddings.create(
                model=model,
                input=text
            )

            embedding = response.data[0].embedding
            response_time_ms = (time.time() - start_time) * 1000

            logger.info(
                f"文本嵌入创建成功: model={model}, "
                f"dim={len(embedding)}, time={response_time_ms:.2f}ms"
            )

            return embedding

        except Exception as e:
            logger.error(f"创建文本嵌入失败: {str(e)}")
            raise LLMAPIException(reason=str(e))

    async def analyze_image(
        self,
        image_url: str,
        prompt: str,
        model: Optional[str] = None
    ) -> str:
        """
        分析图片（OCR或视觉理解）

        Args:
            image_url: 图片URL或base64
            prompt: 分析提示词
            model: 视觉模型名称

        Returns:
            分析结果文本
        """
        model = model or self.ocr_model
        start_time = time.time()

        try:
            logger.debug(f"分析图片: model={model}")

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ]

            response: ChatCompletion = await self.client.chat.completions.create(
                model=model,
                messages=messages
            )

            content = response.choices[0].message.content or ""
            response_time_ms = (time.time() - start_time) * 1000

            logger.info(f"图片分析完成: model={model}, time={response_time_ms:.2f}ms")

            return content

        except Exception as e:
            logger.error(f"图片分析失败: {str(e)}")
            raise LLMAPIException(reason=str(e))

    def estimate_tokens(self, text: str) -> int:
        """
        估算文本的token数量

        简单估算：中文约1.5字符/token，英文约4字符/token

        Args:
            text: 文本内容

        Returns:
            估算的token数
        """
        # 统计中英文字符
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars

        # 估算token数
        tokens = int(chinese_chars / 1.5 + other_chars / 4)

        return max(tokens, 1)

    async def complete_with_tools(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: List[Dict[str, Any]],
        tool_functions: Dict[str, Callable],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        max_iterations: int = 5,
        **kwargs: Any
    ) -> QwenResponse:
        """
        执行带工具调用的补全请求（Function Calling）

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            tools: 工具定义列表，格式参考OpenAI Function Calling API
            tool_functions: 工具名称到实际函数的映射
            model: 模型名称，None使用默认模型
            temperature: 温度参数
            max_tokens: 最大token数
            max_iterations: 最大迭代次数（防止无限循环）
            **kwargs: 其他参数

        Returns:
            Qwen响应对象

        Raises:
            LLMAPIException: API调用失败
            LLMRateLimitException: 速率限制
            LLMTokenLimitException: Token限制

        示例工具定义:
            tools = [{
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "获取指定城市的天气信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "城市名称"
                            }
                        },
                        "required": ["city"]
                    }
                }
            }]
        """
        model = model or self.default_model
        start_time = time.time()
        total_tokens = 0

        try:
            # 构建初始消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            logger.debug(
                f"调用Qwen API with tools: model={model}, "
                f"tools_count={len(tools)}, max_iterations={max_iterations}"
            )

            # 迭代处理工具调用
            for iteration in range(max_iterations):
                # 准备请求参数
                request_params: Dict[str, Any] = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "tools": tools,
                    "tool_choice": "auto",  # 让模型自动决定是否调用工具
                    **kwargs
                }

                # 调用API
                response: ChatCompletion = await self.client.chat.completions.create(**request_params)

                # 累计token使用量
                if response.usage:
                    total_tokens += response.usage.total_tokens

                # 获取响应消息
                message = response.choices[0].message
                finish_reason = response.choices[0].finish_reason

                # 将助手的响应添加到消息历史
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in (message.tool_calls or [])
                    ] if message.tool_calls else None
                })

                # 检查是否需要调用工具
                if finish_reason == "tool_calls" and message.tool_calls:
                    logger.info(f"模型请求调用 {len(message.tool_calls)} 个工具")

                    # 执行所有工具调用
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        function_args_str = tool_call.function.arguments

                        try:
                            # 解析参数
                            function_args = json.loads(function_args_str)

                            logger.debug(
                                f"执行工具: {function_name}, "
                                f"参数: {function_args}"
                            )

                            # 检查工具是否存在
                            if function_name not in tool_functions:
                                error_msg = f"工具 '{function_name}' 未找到"
                                logger.error(error_msg)
                                tool_result = {"error": error_msg}
                            else:
                                # 执行工具函数
                                tool_function = tool_functions[function_name]

                                # 支持同步和异步函数
                                if asyncio.iscoroutinefunction(tool_function):
                                    tool_result = await tool_function(**function_args)
                                else:
                                    tool_result = tool_function(**function_args)

                                logger.info(f"工具 {function_name} 执行成功")

                        except json.JSONDecodeError as e:
                            error_msg = f"解析工具参数失败: {str(e)}"
                            logger.error(error_msg)
                            tool_result = {"error": error_msg}
                        except Exception as e:
                            error_msg = f"执行工具 {function_name} 失败: {str(e)}"
                            logger.error(error_msg)
                            tool_result = {"error": error_msg}

                        # 将工具结果添加到消息历史
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": json.dumps(tool_result, ensure_ascii=False)
                        })

                    # 继续下一轮迭代，让模型处理工具结果
                    continue

                # 如果不需要调用工具，返回最终结果
                else:
                    response_time_ms = (time.time() - start_time) * 1000

                    # 记录指标
                    metrics_collector.record_llm_call(
                        model=model,
                        tokens_used=total_tokens,
                        response_time_ms=response_time_ms,
                        success=True
                    )

                    logger.info(
                        f"Qwen API with tools调用成功: model={model}, "
                        f"tokens={total_tokens}, iterations={iteration + 1}, "
                        f"time={response_time_ms:.2f}ms"
                    )

                    # 提取工具调用信息（如果有）
                    tool_calls_info = None
                    if message.tool_calls:
                        tool_calls_info = [
                            {
                                "id": tc.id,
                                "name": tc.function.name,
                                "arguments": json.loads(tc.function.arguments)
                            }
                            for tc in message.tool_calls
                        ]

                    return QwenResponse(
                        content=message.content or "",
                        model=model,
                        tokens_used=total_tokens,
                        finish_reason=finish_reason,
                        response_time_ms=response_time_ms,
                        tool_calls=tool_calls_info
                    )

            # 达到最大迭代次数
            logger.warning(f"达到最大迭代次数 {max_iterations}，停止工具调用")
            response_time_ms = (time.time() - start_time) * 1000

            metrics_collector.record_llm_call(
                model=model,
                tokens_used=total_tokens,
                response_time_ms=response_time_ms,
                success=True
            )

            return QwenResponse(
                content=messages[-1].get("content", ""),
                model=model,
                tokens_used=total_tokens,
                finish_reason="max_iterations",
                response_time_ms=response_time_ms
            )

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000

            # 记录失败指标
            metrics_collector.record_llm_call(
                model=model,
                tokens_used=total_tokens,
                response_time_ms=response_time_ms,
                success=False
            )

            # 处理不同类型的错误
            error_message = str(e)

            if "rate_limit" in error_message.lower() or "429" in error_message:
                logger.warning(f"Qwen API速率限制: {error_message}")
                raise LLMRateLimitException()

            elif "token" in error_message.lower() and "limit" in error_message.lower():
                logger.error(f"Qwen API Token限制: {error_message}")
                raise LLMTokenLimitException(requested=max_tokens, limit=max_tokens)

            else:
                logger.error(f"Qwen API with tools调用失败: {error_message}")
                raise LLMAPIException(reason=error_message)


# 创建全局Qwen客户端实例
qwen_client = QwenClient()
