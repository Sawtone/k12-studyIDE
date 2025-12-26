"""
Redis客户端管理
提供Redis连接和基础操作
"""

import json
from typing import Any, Optional, List
from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import RedisError

from app.config import settings
from app.core.logging import get_logger
from app.core.exceptions import CacheException

logger = get_logger(__name__)

# 全局Redis客户端
_redis_client: Optional[Redis] = None
_connection_pool: Optional[ConnectionPool] = None


def get_redis_client() -> Redis:
    """
    获取Redis客户端

    Returns:
        Redis客户端实例
    """
    global _redis_client, _connection_pool

    if _redis_client is None:
        # 创建连接池
        _connection_pool = ConnectionPool.from_url(
            settings.redis_url,
            max_connections=settings.redis_max_connections,
            decode_responses=True,
            encoding='utf-8'
        )

        # 创建Redis客户端
        _redis_client = Redis(connection_pool=_connection_pool)

        logger.info(f"Redis客户端已创建: {settings.redis_url}")

    return _redis_client


async def close_redis() -> None:
    """关闭Redis连接"""
    global _redis_client, _connection_pool

    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None

    if _connection_pool is not None:
        await _connection_pool.disconnect()
        _connection_pool = None

    logger.info("Redis连接已关闭")


async def check_redis_connection() -> bool:
    """
    检查Redis连接

    Returns:
        连接是否正常
    """
    try:
        client = get_redis_client()
        await client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis连接检查失败: {str(e)}")
        return False


class RedisCache:
    """Redis缓存操作类"""

    def __init__(self) -> None:
        self.client = get_redis_client()

    async def get(self, key: str) -> Optional[str]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，不存在返回None
        """
        try:
            value = await self.client.get(key)
            if value:
                logger.debug(f"缓存命中: {key}")
            return value
        except RedisError as e:
            logger.error(f"获取缓存失败 {key}: {str(e)}")
            raise CacheException(f"获取缓存失败: {str(e)}")

    async def get_json(self, key: str) -> Optional[Any]:
        """
        获取JSON格式的缓存值

        Args:
            key: 缓存键

        Returns:
            解析后的JSON对象，不存在返回None
        """
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败 {key}: {str(e)}")
                return None
        return None

    async def set(
        self,
        key: str,
        value: str,
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None表示永不过期

        Returns:
            是否设置成功
        """
        try:
            if ttl:
                await self.client.setex(key, ttl, value)
            else:
                await self.client.set(key, value)
            logger.debug(f"缓存已设置: {key} (TTL: {ttl})")
            return True
        except RedisError as e:
            logger.error(f"设置缓存失败 {key}: {str(e)}")
            raise CacheException(f"设置缓存失败: {str(e)}")

    async def set_json(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置JSON格式的缓存值

        Args:
            key: 缓存键
            value: 要缓存的对象
            ttl: 过期时间（秒）

        Returns:
            是否设置成功
        """
        try:
            json_value = json.dumps(value, ensure_ascii=False)
            return await self.set(key, json_value, ttl)
        except (TypeError, ValueError) as e:
            logger.error(f"JSON序列化失败 {key}: {str(e)}")
            raise CacheException(f"JSON序列化失败: {str(e)}")

    async def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        try:
            result = await self.client.delete(key)
            logger.debug(f"缓存已删除: {key}")
            return result > 0
        except RedisError as e:
            logger.error(f"删除缓存失败 {key}: {str(e)}")
            raise CacheException(f"删除缓存失败: {str(e)}")

    async def delete_pattern(self, pattern: str) -> int:
        """
        删除匹配模式的所有缓存

        Args:
            pattern: 键模式（支持通配符*）

        Returns:
            删除的键数量
        """
        try:
            keys = await self.client.keys(pattern)
            if keys:
                deleted = await self.client.delete(*keys)
                logger.debug(f"批量删除缓存: {pattern} ({deleted}个)")
                return deleted
            return 0
        except RedisError as e:
            logger.error(f"批量删除缓存失败 {pattern}: {str(e)}")
            raise CacheException(f"批量删除缓存失败: {str(e)}")

    async def exists(self, key: str) -> bool:
        """
        检查缓存是否存在

        Args:
            key: 缓存键

        Returns:
            是否存在
        """
        try:
            return await self.client.exists(key) > 0
        except RedisError as e:
            logger.error(f"检查缓存存在失败 {key}: {str(e)}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """
        设置缓存过期时间

        Args:
            key: 缓存键
            ttl: 过期时间（秒）

        Returns:
            是否设置成功
        """
        try:
            return await self.client.expire(key, ttl)
        except RedisError as e:
            logger.error(f"设置过期时间失败 {key}: {str(e)}")
            return False

    async def ttl(self, key: str) -> int:
        """
        获取缓存剩余过期时间

        Args:
            key: 缓存键

        Returns:
            剩余秒数，-1表示永不过期，-2表示不存在
        """
        try:
            return await self.client.ttl(key)
        except RedisError as e:
            logger.error(f"获取TTL失败 {key}: {str(e)}")
            return -2

    async def incr(self, key: str, amount: int = 1) -> int:
        """
        递增计数器

        Args:
            key: 缓存键
            amount: 递增量

        Returns:
            递增后的值
        """
        try:
            return await self.client.incrby(key, amount)
        except RedisError as e:
            logger.error(f"递增失败 {key}: {str(e)}")
            raise CacheException(f"递增失败: {str(e)}")

    async def decr(self, key: str, amount: int = 1) -> int:
        """
        递减计数器

        Args:
            key: 缓存键
            amount: 递减量

        Returns:
            递减后的值
        """
        try:
            return await self.client.decrby(key, amount)
        except RedisError as e:
            logger.error(f"递减失败 {key}: {str(e)}")
            raise CacheException(f"递减失败: {str(e)}")

    # Hash操作
    async def hget(self, name: str, key: str) -> Optional[str]:
        """获取Hash字段值"""
        try:
            return await self.client.hget(name, key)
        except RedisError as e:
            logger.error(f"获取Hash失败 {name}.{key}: {str(e)}")
            return None

    async def hset(self, name: str, key: str, value: str) -> bool:
        """设置Hash字段值"""
        try:
            await self.client.hset(name, key, value)
            return True
        except RedisError as e:
            logger.error(f"设置Hash失败 {name}.{key}: {str(e)}")
            return False

    async def hgetall(self, name: str) -> dict:
        """获取Hash所有字段"""
        try:
            return await self.client.hgetall(name)
        except RedisError as e:
            logger.error(f"获取Hash全部失败 {name}: {str(e)}")
            return {}

    async def hdel(self, name: str, *keys: str) -> int:
        """删除Hash字段"""
        try:
            return await self.client.hdel(name, *keys)
        except RedisError as e:
            logger.error(f"删除Hash字段失败 {name}: {str(e)}")
            return 0

    # List操作
    async def lpush(self, key: str, *values: str) -> int:
        """从左侧推入列表"""
        try:
            return await self.client.lpush(key, *values)
        except RedisError as e:
            logger.error(f"列表推入失败 {key}: {str(e)}")
            raise CacheException(f"列表推入失败: {str(e)}")

    async def rpush(self, key: str, *values: str) -> int:
        """从右侧推入列表"""
        try:
            return await self.client.rpush(key, *values)
        except RedisError as e:
            logger.error(f"列表推入失败 {key}: {str(e)}")
            raise CacheException(f"列表推入失败: {str(e)}")

    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        """获取列表范围"""
        try:
            return await self.client.lrange(key, start, end)
        except RedisError as e:
            logger.error(f"获取列表范围失败 {key}: {str(e)}")
            return []

    async def ltrim(self, key: str, start: int, end: int) -> bool:
        """修剪列表"""
        try:
            await self.client.ltrim(key, start, end)
            return True
        except RedisError as e:
            logger.error(f"修剪列表失败 {key}: {str(e)}")
            return False

    # Set操作
    async def sadd(self, key: str, *members: str) -> int:
        """添加集合成员"""
        try:
            return await self.client.sadd(key, *members)
        except RedisError as e:
            logger.error(f"添加集合成员失败 {key}: {str(e)}")
            raise CacheException(f"添加集合成员失败: {str(e)}")

    async def srem(self, key: str, *members: str) -> int:
        """移除集合成员"""
        try:
            return await self.client.srem(key, *members)
        except RedisError as e:
            logger.error(f"移除集合成员失败 {key}: {str(e)}")
            return 0

    async def smembers(self, key: str) -> set:
        """获取集合所有成员"""
        try:
            return await self.client.smembers(key)
        except RedisError as e:
            logger.error(f"获取集合成员失败 {key}: {str(e)}")
            return set()

    async def sismember(self, key: str, member: str) -> bool:
        """检查是否为集合成员"""
        try:
            return await self.client.sismember(key, member)
        except RedisError as e:
            logger.error(f"检查集合成员失败 {key}: {str(e)}")
            return False


# 创建全局缓存实例
redis_cache = RedisCache()
