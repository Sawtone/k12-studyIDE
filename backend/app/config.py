"""
应用配置管理
使用 Pydantic Settings 进行配置管理和验证
"""

from typing import List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # 应用配置
    app_name: str = Field(default="智能学习助手", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=False, description="调试模式")
    api_prefix: str = Field(default="/api/v1", description="API前缀")

    # 服务器配置
    host: str = Field(default="0.0.0.0", description="服务器地址")
    port: int = Field(default=8000, description="服务器端口")

    # 数据库配置
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/learning_assistant",
        description="数据库连接URL"
    )
    database_pool_size: int = Field(default=20, description="数据库连接池大小")
    database_max_overflow: int = Field(default=10, description="数据库连接池最大溢出")

    # Redis配置
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis连接URL")
    redis_max_connections: int = Field(default=50, description="Redis最大连接数")

    # Qwen API配置
    qwen_api_key: str = Field(
        default="",
        description="Qwen API密钥（必须通过环境变量QWEN_API_KEY设置）"
    )

    @field_validator("qwen_api_key")
    @classmethod
    def validate_qwen_api_key(cls, v: str) -> str:
        """验证Qwen API密钥

        注意：在生产环境中，如果未设置会发出警告但不会阻止启动
        这样可以让应用先启动，然后在实际调用 API 时再检查
        """
        if not v or v == "":
            # 在生产环境中只警告，不阻止启动
            import os
            if os.getenv("ENVIRONMENT") == "production":
                import warnings
                warnings.warn(
                    "QWEN_API_KEY 未设置。API 调用将会失败。"
                    "请在 Railway 环境变量中设置 QWEN_API_KEY"
                )
                return ""  # 返回空字符串，允许启动
            else:
                raise ValueError(
                    "QWEN_API_KEY环境变量未设置。"
                    "请在.env文件中设置: QWEN_API_KEY=your-api-key"
                )
        if v and not v.startswith("sk-"):
            raise ValueError("Qwen API密钥格式不正确，应以'sk-'开头")
        return v
    qwen_api_base: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="Qwen API基础URL"
    )
    qwen_text_model: str = Field(default="qwen-max", description="文本模型")
    qwen_ocr_model: str = Field(default="qwen-vl-max", description="OCR模型")
    qwen_embedding_model: str = Field(
        default="text-embedding-v3",
        description="Embedding模型"
    )

    # 安全配置
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT密钥"
    )
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间(分钟)")

    # CORS配置
    # 使用 Union[str, List[str]] 来接受字符串或列表
    cors_origins: Union[str, List[str]] = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="允许的CORS源（可以是逗号分隔的字符串或列表）"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v) -> List[str]:
        """解析CORS源配置

        支持以下格式：
        - 字符串 "*" -> ["*"]
        - 逗号分隔字符串 "http://a.com,http://b.com" -> ["http://a.com", "http://b.com"]
        - 列表 ["http://a.com"] -> ["http://a.com"]
        """
        if isinstance(v, str):
            # 处理 "*" 的情况
            if v.strip() == "*":
                return ["*"]
            # 处理逗号分隔的情况
            if "," in v:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
            # 处理单个URL的情况
            if v.strip():
                return [v.strip()]
            # 空字符串使用默认值
            return ["http://localhost:3000", "http://localhost:5173"]
        # 已经是列表，直接返回
        if isinstance(v, list):
            return v
        # 其他情况使用默认值
        return ["http://localhost:3000", "http://localhost:5173"]

    # 限流配置
    rate_limit_per_minute: int = Field(default=60, description="每分钟请求限制")
    rate_limit_burst: int = Field(default=10, description="突发请求限制")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: str = Field(default="logs/app.log", description="日志文件路径")

    # 缓存配置
    cache_ttl_seconds: int = Field(default=3600, description="缓存TTL(秒)")
    analysis_cache_ttl: int = Field(default=3600, description="分析结果缓存TTL(秒)")

    # Agent配置
    agent_timeout_seconds: int = Field(default=30, description="Agent超时时间(秒)")
    agent_retry_attempts: int = Field(default=3, description="Agent重试次数")
    agent_max_tokens: int = Field(default=4000, description="Agent最大Token数")

    # 文件上传配置
    max_upload_size_mb: int = Field(default=10, description="最大上传文件大小(MB)")
    allowed_image_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/jpg"],
        description="允许的图片类型"
    )

    # 会话配置
    session_cleanup_days: int = Field(default=30, description="会话清理天数")
    max_editor_versions: int = Field(default=50, description="编辑器最大版本数")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """验证环境配置"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"environment must be one of {allowed}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """验证日志级别"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v_upper

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == "production"

    @property
    def max_upload_size_bytes(self) -> int:
        """最大上传文件大小(字节)"""
        return self.max_upload_size_mb * 1024 * 1024


# 创建全局配置实例
settings = Settings()
