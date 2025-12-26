"""
自定义异常类
定义系统中使用的所有自定义异常
"""

from typing import Any, Dict, Optional


class BaseAppException(Exception):
    """应用基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# ============================================
# 会话相关异常
# ============================================

class SessionNotFoundException(BaseAppException):
    """会话不存在异常"""

    def __init__(self, session_id: str) -> None:
        super().__init__(
            message=f"会话 {session_id} 不存在",
            error_code="SESSION_NOT_FOUND",
            status_code=404,
            details={"session_id": session_id}
        )


class SessionExpiredException(BaseAppException):
    """会话已过期异常"""

    def __init__(self, session_id: str) -> None:
        super().__init__(
            message=f"会话 {session_id} 已过期",
            error_code="SESSION_EXPIRED",
            status_code=410,
            details={"session_id": session_id}
        )


class SessionConflictException(BaseAppException):
    """会话冲突异常（版本冲突）"""

    def __init__(self, session_id: str, expected_version: int, actual_version: int) -> None:
        super().__init__(
            message=f"会话版本冲突：期望版本 {expected_version}，实际版本 {actual_version}",
            error_code="SESSION_VERSION_CONFLICT",
            status_code=409,
            details={
                "session_id": session_id,
                "expected_version": expected_version,
                "actual_version": actual_version
            }
        )


# ============================================
# Agent相关异常
# ============================================

class AgentExecutionException(BaseAppException):
    """Agent执行异常"""

    def __init__(self, agent_name: str, reason: str) -> None:
        super().__init__(
            message=f"Agent {agent_name} 执行失败: {reason}",
            error_code="AGENT_EXECUTION_FAILED",
            status_code=500,
            details={"agent_name": agent_name, "reason": reason}
        )


class AgentTimeoutException(BaseAppException):
    """Agent超时异常"""

    def __init__(self, agent_name: str, timeout_seconds: int) -> None:
        super().__init__(
            message=f"Agent {agent_name} 执行超时 ({timeout_seconds}秒)",
            error_code="AGENT_TIMEOUT",
            status_code=504,
            details={"agent_name": agent_name, "timeout_seconds": timeout_seconds}
        )


class AgentNotFoundException(BaseAppException):
    """Agent不存在异常"""

    def __init__(self, agent_name: str) -> None:
        super().__init__(
            message=f"Agent {agent_name} 不存在",
            error_code="AGENT_NOT_FOUND",
            status_code=404,
            details={"agent_name": agent_name}
        )


# ============================================
# LLM相关异常
# ============================================

class LLMAPIException(BaseAppException):
    """LLM API调用异常"""

    def __init__(self, reason: str, status_code: int = 503) -> None:
        super().__init__(
            message=f"AI服务暂时不可用: {reason}",
            error_code="LLM_API_ERROR",
            status_code=status_code,
            details={"reason": reason}
        )


class LLMRateLimitException(BaseAppException):
    """LLM速率限制异常"""

    def __init__(self, retry_after: Optional[int] = None) -> None:
        super().__init__(
            message="AI服务请求过于频繁，请稍后再试",
            error_code="LLM_RATE_LIMIT",
            status_code=429,
            details={"retry_after": retry_after}
        )


class LLMTokenLimitException(BaseAppException):
    """LLM Token限制异常"""

    def __init__(self, requested: int, limit: int) -> None:
        super().__init__(
            message=f"内容过长，超出限制 (请求: {requested}, 限制: {limit})",
            error_code="LLM_TOKEN_LIMIT",
            status_code=413,
            details={"requested": requested, "limit": limit}
        )


# ============================================
# 数据验证异常
# ============================================

class ValidationException(BaseAppException):
    """数据验证异常"""

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(
            message=f"字段 {field} 验证失败: {reason}",
            error_code="VALIDATION_ERROR",
            status_code=400,
            details={"field": field, "reason": reason}
        )


class ContentTooLongException(BaseAppException):
    """内容过长异常"""

    def __init__(self, max_length: int, actual_length: int) -> None:
        super().__init__(
            message=f"内容过长 (最大: {max_length}, 实际: {actual_length})",
            error_code="CONTENT_TOO_LONG",
            status_code=413,
            details={"max_length": max_length, "actual_length": actual_length}
        )


# ============================================
# 文件处理异常
# ============================================

class FileUploadException(BaseAppException):
    """文件上传异常"""

    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"文件上传失败: {reason}",
            error_code="FILE_UPLOAD_ERROR",
            status_code=400,
            details={"reason": reason}
        )


class UnsupportedFileTypeException(BaseAppException):
    """不支持的文件类型异常"""

    def __init__(self, file_type: str, allowed_types: list[str]) -> None:
        super().__init__(
            message=f"不支持的文件类型: {file_type}",
            error_code="UNSUPPORTED_FILE_TYPE",
            status_code=415,
            details={"file_type": file_type, "allowed_types": allowed_types}
        )


# ============================================
# 权限相关异常
# ============================================

class UnauthorizedException(BaseAppException):
    """未授权异常"""

    def __init__(self, reason: str = "未授权访问") -> None:
        super().__init__(
            message=reason,
            error_code="UNAUTHORIZED",
            status_code=401,
            details={"reason": reason}
        )


class ForbiddenException(BaseAppException):
    """禁止访问异常"""

    def __init__(self, reason: str = "无权限访问此资源") -> None:
        super().__init__(
            message=reason,
            error_code="FORBIDDEN",
            status_code=403,
            details={"reason": reason}
        )


# ============================================
# 缓存相关异常
# ============================================

class CacheException(BaseAppException):
    """缓存异常"""

    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"缓存操作失败: {reason}",
            error_code="CACHE_ERROR",
            status_code=500,
            details={"reason": reason}
        )


# ============================================
# 数据库相关异常
# ============================================

class DatabaseException(BaseAppException):
    """数据库异常"""

    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"数据库操作失败: {reason}",
            error_code="DATABASE_ERROR",
            status_code=500,
            details={"reason": reason}
        )


class ResourceNotFoundException(BaseAppException):
    """资源不存在异常"""

    def __init__(self, resource_type: str, resource_id: str) -> None:
        super().__init__(
            message=f"{resource_type} {resource_id} 不存在",
            error_code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


# ============================================
# 业务逻辑异常
# ============================================

class InvalidModeException(BaseAppException):
    """无效模式异常"""

    def __init__(self, mode: str, allowed_modes: list[str]) -> None:
        super().__init__(
            message=f"无效的模式: {mode}",
            error_code="INVALID_MODE",
            status_code=400,
            details={"mode": mode, "allowed_modes": allowed_modes}
        )


class OperationNotAllowedException(BaseAppException):
    """操作不允许异常"""

    def __init__(self, operation: str, reason: str) -> None:
        super().__init__(
            message=f"操作 {operation} 不允许: {reason}",
            error_code="OPERATION_NOT_ALLOWED",
            status_code=403,
            details={"operation": operation, "reason": reason}
        )
