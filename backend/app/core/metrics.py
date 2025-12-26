"""
指标监控模块
用于收集和记录系统运行指标
"""

import time
from typing import Optional, Dict, Any
from functools import wraps
from contextlib import contextmanager

from app.core.logging import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """指标收集器"""

    def __init__(self) -> None:
        self.metrics: Dict[str, Any] = {
            "api_calls": {},
            "agent_calls": {},
            "llm_calls": {},
            "errors": {},
            "response_times": {},
            "issue_reports": {},
        }

    def record_api_call(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float
    ) -> None:
        """记录API调用"""
        key = f"{method}:{endpoint}"
        if key not in self.metrics["api_calls"]:
            self.metrics["api_calls"][key] = {
                "count": 0,
                "success": 0,
                "error": 0,
                "total_time_ms": 0,
            }

        self.metrics["api_calls"][key]["count"] += 1
        self.metrics["api_calls"][key]["total_time_ms"] += response_time_ms

        if 200 <= status_code < 300:
            self.metrics["api_calls"][key]["success"] += 1
        else:
            self.metrics["api_calls"][key]["error"] += 1

    def record_agent_call(
        self,
        agent_name: str,
        success: bool,
        execution_time_ms: float,
        tokens_used: int = 0
    ) -> None:
        """记录Agent调用"""
        if agent_name not in self.metrics["agent_calls"]:
            self.metrics["agent_calls"][agent_name] = {
                "count": 0,
                "success": 0,
                "error": 0,
                "total_time_ms": 0,
                "total_tokens": 0,
            }

        self.metrics["agent_calls"][agent_name]["count"] += 1
        self.metrics["agent_calls"][agent_name]["total_time_ms"] += execution_time_ms
        self.metrics["agent_calls"][agent_name]["total_tokens"] += tokens_used

        if success:
            self.metrics["agent_calls"][agent_name]["success"] += 1
        else:
            self.metrics["agent_calls"][agent_name]["error"] += 1

    def record_llm_call(
        self,
        model: str,
        tokens_used: int,
        response_time_ms: float,
        success: bool = True
    ) -> None:
        """记录LLM调用"""
        if model not in self.metrics["llm_calls"]:
            self.metrics["llm_calls"][model] = {
                "count": 0,
                "success": 0,
                "error": 0,
                "total_tokens": 0,
                "total_time_ms": 0,
            }

        self.metrics["llm_calls"][model]["count"] += 1
        self.metrics["llm_calls"][model]["total_tokens"] += tokens_used
        self.metrics["llm_calls"][model]["total_time_ms"] += response_time_ms

        if success:
            self.metrics["llm_calls"][model]["success"] += 1
        else:
            self.metrics["llm_calls"][model]["error"] += 1

    def record_error(self, error_type: str, error_code: str) -> None:
        """记录错误"""
        key = f"{error_type}:{error_code}"
        if key not in self.metrics["errors"]:
            self.metrics["errors"][key] = 0
        self.metrics["errors"][key] += 1

    def record_issue_report(self, issue_type: str, session_id: str) -> None:
        """
        记录用户问题报告

        Args:
            issue_type: 问题类型（如system_error, data_loss, security等）
            session_id: 会话ID
        """
        if issue_type not in self.metrics["issue_reports"]:
            self.metrics["issue_reports"][issue_type] = {
                "count": 0,
                "sessions": []
            }

        self.metrics["issue_reports"][issue_type]["count"] += 1

        # 保留最近10个会话ID用于追踪
        sessions = self.metrics["issue_reports"][issue_type]["sessions"]
        sessions.append(session_id)
        if len(sessions) > 10:
            sessions.pop(0)

        logger.info(f"记录问题报告: type={issue_type}, session={session_id}")

    def get_metrics(self) -> Dict[str, Any]:
        """获取所有指标"""
        return self.metrics.copy()

    def reset_metrics(self) -> None:
        """重置指标"""
        self.metrics = {
            "api_calls": {},
            "agent_calls": {},
            "llm_calls": {},
            "errors": {},
            "response_times": {},
            "issue_reports": {},
        }


# 全局指标收集器实例
metrics_collector = MetricsCollector()


@contextmanager
def track_time(operation: str):
    """
    追踪操作执行时间的上下文管理器

    Args:
        operation: 操作名称

    Yields:
        执行时间（毫秒）
    """
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_ms = (time.time() - start_time) * 1000
        logger.info(f"{operation} 执行时间: {elapsed_ms:.2f}ms")


def track_execution_time(func):
    """
    追踪函数执行时间的装饰器

    Args:
        func: 要追踪的函数

    Returns:
        装饰后的函数
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.debug(f"{func.__name__} 执行时间: {elapsed_ms:.2f}ms")

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.debug(f"{func.__name__} 执行时间: {elapsed_ms:.2f}ms")

    # 判断是否为异步函数
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
