"""
日志配置模块
提供统一的日志记录功能
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from pythonjsonlogger import jsonlogger

from app.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """自定义JSON格式化器"""

    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict) -> None:
        """添加自定义字段"""
        super().add_fields(log_record, record, message_dict)

        # 添加时间戳
        log_record['timestamp'] = self.formatTime(record, self.datefmt)

        # 添加日志级别
        log_record['level'] = record.levelname

        # 添加模块信息
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno

        # 添加环境信息
        log_record['environment'] = settings.environment


def setup_logging(
    name: Optional[str] = None,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        log_level: 日志级别
        log_file: 日志文件路径

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name or __name__)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 设置日志级别
    level = log_level or settings.log_level
    logger.setLevel(getattr(logging, level))

    # 控制台处理器（开发环境使用友好格式）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    if settings.is_development:
        # 开发环境：使用易读的格式
        console_format = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # 生产环境：使用JSON格式
        console_format = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )

    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # 文件处理器（始终使用JSON格式）
    file_path = log_file or settings.log_file
    if file_path:
        # 确保日志目录存在
        log_dir = Path(file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # 创建文件处理器（带轮转）
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            filename=file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)

        # 使用JSON格式
        file_format = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    # 错误日志单独文件
    if file_path:
        error_file = str(Path(file_path).parent / 'error.log')
        error_handler = RotatingFileHandler(
            filename=error_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        logger.addHandler(error_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器
    """
    return setup_logging(name)


# 创建默认日志记录器
logger = setup_logging('app')
