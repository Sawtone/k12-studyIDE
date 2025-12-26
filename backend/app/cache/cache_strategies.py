"""
缓存策略模块
定义不同类型数据的缓存策略和键命名规范
"""

import hashlib
import json
from typing import Any, Optional, Dict
from datetime import datetime

from app.config import settings
from app.cache.redis_client import redis_cache
from app.core.logging import get_logger

logger = get_logger(__name__)


class CacheKeyBuilder:
    """缓存键构建器"""

    @staticmethod
    def session_runtime(session_id: str) -> str:
        """会话运行时状态键"""
        return f"session:{session_id}:runtime"

    @staticmethod
    def session_content(session_id: str) -> str:
        """会话内容缓存键"""
        return f"session:{session_id}:content"

    @staticmethod
    def chat_context(session_id: str) -> str:
        """对话上下文键"""
        return f"session:{session_id}:chat:context"

    @staticmethod
    def analysis_result(analysis_type: str, content_hash: str) -> str:
        """分析结果缓存键"""
        return f"analysis:{analysis_type}:{content_hash}"

    @staticmethod
    def session_annotations(session_id: str) -> str:
        """会话错误标注键"""
        return f"session:{session_id}:annotations"

    @staticmethod
    def agent_lock(session_id: str, agent_name: str) -> str:
        """Agent执行锁键"""
        return f"lock:agent:{session_id}:{agent_name}"

    @staticmethod
    def rate_limit(user_id: str, endpoint: str) -> str:
        """限流键"""
        return f"ratelimit:{user_id}:{endpoint}"

    @staticmethod
    def websocket_connections(session_id: str) -> str:
        """WebSocket连接集合键"""
        return f"ws:session:{session_id}"

    @staticmethod
    def daily_stats(date: str) -> str:
        """每日统计键"""
        return f"stats:daily:{date}"

    @staticmethod
    def generate_content_hash(content: str) -> str:
        """
        生成内容哈希

        Args:
            content: 内容文本

        Returns:
            SHA256哈希值
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()


class SessionCache:
    """会话缓存管理"""

    def __init__(self) -> None:
        self.cache = redis_cache
        self.key_builder = CacheKeyBuilder()

    async def set_runtime_state(
        self,
        session_id: str,
        state: Dict[str, Any]
    ) -> bool:
        """
        设置会话运行时状态

        Args:
            session_id: 会话ID
            state: 状态数据

        Returns:
            是否设置成功
        """
        key = self.key_builder.session_runtime(session_id)
        return await self.cache.set_json(key, state, ttl=86400)  # 24小时

    async def get_runtime_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话运行时状态"""
        key = self.key_builder.session_runtime(session_id)
        return await self.cache.get_json(key)

    async def update_runtime_field(
        self,
        session_id: str,
        field: str,
        value: Any
    ) -> bool:
        """
        更新运行时状态的单个字段

        Args:
            session_id: 会话ID
            field: 字段名
            value: 字段值

        Returns:
            是否更新成功
        """
        key = self.key_builder.session_runtime(session_id)
        return await self.cache.hset(key, field, json.dumps(value))

    async def set_content(
        self,
        session_id: str,
        content: str,
        version: int,
        word_count: int
    ) -> bool:
        """
        缓存编辑器内容

        Args:
            session_id: 会话ID
            content: 内容文本
            version: 版本号
            word_count: 字数

        Returns:
            是否设置成功
        """
        key = self.key_builder.session_content(session_id)
        content_hash = self.key_builder.generate_content_hash(content)

        data = {
            "content": content,
            "version": version,
            "hash": content_hash,
            "word_count": word_count,
            "timestamp": datetime.utcnow().isoformat()
        }

        return await self.cache.set_json(key, data, ttl=3600)  # 1小时

    async def get_content(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取缓存的编辑器内容"""
        key = self.key_builder.session_content(session_id)
        return await self.cache.get_json(key)

    async def delete_content(self, session_id: str) -> bool:
        """
        删除会话内容缓存

        Args:
            session_id: 会话ID

        Returns:
            是否删除成功
        """
        key = self.key_builder.session_content(session_id)
        result = await self.cache.delete(key)
        logger.debug(f"删除会话内容缓存: session={session_id}, success={result}")
        return result > 0

    async def delete_session_cache(self, session_id: str) -> int:
        """
        删除会话相关的所有缓存

        Args:
            session_id: 会话ID

        Returns:
            删除的键数量
        """
        pattern = f"session:{session_id}:*"
        return await self.cache.delete_pattern(pattern)


class AnalysisCache:
    """分析结果缓存管理"""

    def __init__(self) -> None:
        self.cache = redis_cache
        self.key_builder = CacheKeyBuilder()

    async def set_result(
        self,
        analysis_type: str,
        content: str,
        result: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        缓存分析结果

        Args:
            analysis_type: 分析类型
            content: 内容文本
            result: 分析结果
            ttl: 过期时间（秒）

        Returns:
            是否设置成功
        """
        content_hash = self.key_builder.generate_content_hash(content)
        key = self.key_builder.analysis_result(analysis_type, content_hash)

        cache_data = {
            "results": result,
            "created_at": datetime.utcnow().isoformat(),
            "hit_count": 0
        }

        ttl = ttl or settings.analysis_cache_ttl
        return await self.cache.set_json(key, cache_data, ttl=ttl)

    async def get_result(
        self,
        analysis_type: str,
        content: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取缓存的分析结果

        Args:
            analysis_type: 分析类型
            content: 内容文本

        Returns:
            分析结果，不存在返回None
        """
        content_hash = self.key_builder.generate_content_hash(content)
        key = self.key_builder.analysis_result(analysis_type, content_hash)

        cache_data = await self.cache.get_json(key)
        if cache_data:
            # 增加命中计数
            cache_data["hit_count"] = cache_data.get("hit_count", 0) + 1
            await self.cache.set_json(key, cache_data, ttl=settings.analysis_cache_ttl)
            logger.info(f"分析结果缓存命中: {analysis_type}")

        return cache_data


class ChatContextCache:
    """对话上下文缓存管理"""

    def __init__(self) -> None:
        self.cache = redis_cache
        self.key_builder = CacheKeyBuilder()
        self.max_messages = 20  # 保留最近20条消息

    async def add_message(
        self,
        session_id: str,
        message: Dict[str, Any]
    ) -> bool:
        """
        添加对话消息到上下文

        Args:
            session_id: 会话ID
            message: 消息数据

        Returns:
            是否添加成功
        """
        key = self.key_builder.chat_context(session_id)
        message_json = json.dumps(message, ensure_ascii=False)

        # 添加到列表右侧（最新）
        await self.cache.rpush(key, message_json)

        # 保持列表长度
        await self.cache.ltrim(key, -self.max_messages, -1)

        # 设置过期时间
        await self.cache.expire(key, 7200)  # 2小时

        return True

    async def get_context(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> list[Dict[str, Any]]:
        """
        获取对话上下文

        Args:
            session_id: 会话ID
            limit: 限制消息数量

        Returns:
            消息列表
        """
        key = self.key_builder.chat_context(session_id)
        limit = limit or self.max_messages

        messages_json = await self.cache.lrange(key, -limit, -1)
        messages = []

        for msg_json in messages_json:
            try:
                messages.append(json.loads(msg_json))
            except json.JSONDecodeError:
                logger.warning(f"解析对话消息失败: {msg_json}")

        return messages

    async def clear_context(self, session_id: str) -> bool:
        """清空对话上下文"""
        key = self.key_builder.chat_context(session_id)
        return await self.cache.delete(key)


class AgentLockManager:
    """Agent执行锁管理"""

    def __init__(self) -> None:
        self.cache = redis_cache
        self.key_builder = CacheKeyBuilder()
        self.lock_ttl = 30  # 锁超时时间30秒

    async def acquire_lock(
        self,
        session_id: str,
        agent_name: str,
        request_id: str
    ) -> bool:
        """
        获取Agent执行锁

        Args:
            session_id: 会话ID
            agent_name: Agent名称
            request_id: 请求ID

        Returns:
            是否获取成功
        """
        key = self.key_builder.agent_lock(session_id, agent_name)

        # 使用SET NX（不存在时设置）
        result = await self.cache.client.set(
            key,
            request_id,
            nx=True,
            ex=self.lock_ttl
        )

        if result:
            logger.debug(f"获取Agent锁成功: {agent_name} ({request_id})")
        else:
            logger.warning(f"获取Agent锁失败: {agent_name} (已被锁定)")

        return bool(result)

    async def release_lock(
        self,
        session_id: str,
        agent_name: str,
        request_id: str
    ) -> bool:
        """
        释放Agent执行锁

        Args:
            session_id: 会话ID
            agent_name: Agent名称
            request_id: 请求ID

        Returns:
            是否释放成功
        """
        key = self.key_builder.agent_lock(session_id, agent_name)

        # 只有持有锁的请求才能释放
        current_holder = await self.cache.get(key)
        if current_holder == request_id:
            await self.cache.delete(key)
            logger.debug(f"释放Agent锁成功: {agent_name} ({request_id})")
            return True

        logger.warning(f"释放Agent锁失败: {agent_name} (不是锁持有者)")
        return False


class RateLimiter:
    """限流器"""

    def __init__(self) -> None:
        self.cache = redis_cache
        self.key_builder = CacheKeyBuilder()

    async def check_rate_limit(
        self,
        user_id: str,
        endpoint: str,
        limit: int,
        window: int = 60
    ) -> tuple[bool, int]:
        """
        检查是否超过限流

        Args:
            user_id: 用户ID
            endpoint: 端点
            limit: 限制次数
            window: 时间窗口（秒）

        Returns:
            (是否允许, 剩余次数)
        """
        key = self.key_builder.rate_limit(user_id, endpoint)

        # 获取当前计数
        current = await self.cache.get(key)

        if current is None:
            # 首次请求
            await self.cache.set(key, "1", ttl=window)
            return True, limit - 1

        count = int(current)
        if count >= limit:
            # 超过限制
            ttl = await self.cache.ttl(key)
            logger.warning(f"用户 {user_id} 超过限流: {endpoint} ({count}/{limit})")
            return False, 0

        # 增加计数
        new_count = await self.cache.incr(key)
        remaining = max(0, limit - new_count)

        return True, remaining


# 创建全局缓存管理器实例
session_cache = SessionCache()
analysis_cache = AnalysisCache()
chat_context_cache = ChatContextCache()
agent_lock_manager = AgentLockManager()
rate_limiter = RateLimiter()
