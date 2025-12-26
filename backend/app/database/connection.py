"""
数据库连接管理
提供异步数据库连接和会话管理
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from sqlalchemy import text

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# 创建基类
Base = declarative_base()

# 全局引擎和会话工厂
_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """
    获取数据库引擎

    Returns:
        数据库引擎
    """
    global _engine

    if _engine is None:
        # 确保使用 asyncpg 驱动
        database_url = settings.database_url
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)

        # 根据环境选择连接池策略
        engine_kwargs = {
            "echo": settings.debug,
            "pool_pre_ping": True,  # 连接前检查连接是否有效
        }

        if settings.is_development:
            # 开发环境不使用连接池
            engine_kwargs["poolclass"] = NullPool
        else:
            # 生产环境使用异步连接池
            engine_kwargs["poolclass"] = AsyncAdaptedQueuePool
            engine_kwargs["pool_size"] = settings.database_pool_size
            engine_kwargs["max_overflow"] = settings.database_max_overflow
            engine_kwargs["pool_recycle"] = 3600  # 1小时回收连接

        _engine = create_async_engine(database_url, **engine_kwargs)

        logger.info(f"数据库引擎已创建: {database_url.split('@')[1] if '@' in database_url else 'local'}")

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    获取会话工厂

    Returns:
        会话工厂
    """
    global _async_session_factory

    if _async_session_factory is None:
        engine = get_engine()
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        logger.info("数据库会话工厂已创建")

    return _async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话（依赖注入）

    Yields:
        数据库会话
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    初始化数据库
    创建所有表
    """
    engine = get_engine()

    async with engine.begin() as conn:
        # 导入所有模型以确保它们被注册
        from app.database import models  # noqa: F401

        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)

    logger.info("数据库表已创建")


async def close_db() -> None:
    """
    关闭数据库连接
    """
    global _engine, _async_session_factory

    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None
        logger.info("数据库连接已关闭")


async def check_db_connection() -> bool:
    """
    检查数据库连接

    Returns:
        连接是否正常
    """
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"数据库连接检查失败: {str(e)}")
        return False
