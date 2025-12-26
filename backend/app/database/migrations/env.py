"""
数据库迁移脚本环境配置
"""

from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.database.connection import Base
from app.database.models import *  # 导入所有模型

# Alembic Config对象
config = context.config

# 设置数据库URL（确保使用asyncpg驱动）
database_url = settings.database_url
# 确保 URL 使用 postgresql+asyncpg:// 而不是 postgresql://
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)

config.set_main_option("sqlalchemy.url", database_url)

# 解释日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 目标元数据
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    离线模式运行迁移
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """执行迁移"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    在线模式运行迁移
    """
    # 确保使用 asyncpg 驱动
    database_url = settings.database_url
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)

    connectable = create_async_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
