"""
FastAPI主应用
应用入口和配置
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.logging import logger
from app.core.exceptions import BaseAppException
from app.database.connection import init_db, close_db, check_db_connection
from app.cache.redis_client import check_redis_connection, close_redis

# 导入路由
from app.api.v1 import session, literature, science, chat, ocr, feedback, system
from app.api.websocket import websocket_endpoint


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info(f"启动 {settings.app_name} v{settings.app_version}")
    logger.info(f"环境: {settings.environment}")

    # 检查数据库连接
    db_ok = await check_db_connection()
    if db_ok:
        logger.info("✓ 数据库连接正常")
    else:
        logger.error("✗ 数据库连接失败")

    # 检查Redis连接
    redis_ok = await check_redis_connection()
    if redis_ok:
        logger.info("✓ Redis连接正常")
    else:
        logger.error("✗ Redis连接失败")

    logger.info("=" * 60)
    logger.info("智能学习助手系统已启动")
    logger.info(f"API文档: http://{settings.host}:{settings.port}/docs")
    logger.info(f"健康检查: http://{settings.host}:{settings.port}/health")
    logger.info("=" * 60)

    yield

    # 关闭时执行
    logger.info("关闭应用...")
    await close_db()
    await close_redis()
    logger.info("应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    description="""
    ## 智能学习助手API

    面向K12学生的AI学习辅助系统，提供：
    - **文科模式**：语法检查、文本润色、结构分析、健康度评分
    - **理科模式**：步骤验证、逻辑推导、断点调试
    - **智能对话**：上下文感知的学习助手
    - **OCR识别**：图片文字识别

    ## 认证方式
    使用Bearer Token认证

    ## 速率限制
    - 普通用户：60请求/分钟
    - 付费用户：300请求/分钟

    ## WebSocket连接
    实时功能使用WebSocket：
    ```
    ws://localhost:8000/ws/session/{session_id}
    ```
    """,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(BaseAppException)
async def app_exception_handler(request, exc: BaseAppException):
    """处理应用自定义异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """处理未捕获的异常"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误",
                "details": {}
            }
        }
    )


# 健康检查端点
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""
    db_ok = await check_db_connection()
    redis_ok = await check_redis_connection()

    return {
        "status": "healthy" if (db_ok and redis_ok) else "unhealthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "services": {
            "database": "up" if db_ok else "down",
            "redis": "up" if redis_ok else "down",
        }
    }


@app.get("/", tags=["系统"])
async def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "description": "智能学习助手API - K12教育AI辅助平台"
    }


@app.get("/api/v1/system/capabilities", tags=["系统"])
async def get_capabilities():
    """获取系统能力"""
    return {
        "modes": ["literature", "science"],
        "literature_capabilities": [
            {
                "id": "grammar_check",
                "name": "语法检查",
                "description": "识别错别字、语法错误和病句",
                "icon": "spell-check"
            },
            {
                "id": "polish",
                "name": "文本润色",
                "description": "优化表达、丰富词汇",
                "icon": "edit"
            },
            {
                "id": "structure_analysis",
                "name": "结构分析",
                "description": "分析文章组织结构",
                "icon": "tree"
            },
            {
                "id": "health_score",
                "name": "健康度评分",
                "description": "多维度评估文章质量",
                "icon": "chart"
            }
        ],
        "science_capabilities": [
            {
                "id": "math_validation",
                "name": "步骤验证",
                "description": "验证数学解题步骤",
                "icon": "check"
            },
            {
                "id": "logic_tree",
                "name": "逻辑树",
                "description": "构建推导逻辑树",
                "icon": "tree"
            }
        ],
        "limits": {
            "max_content_length": 50000,
            "max_file_size_mb": 10,
            "rate_limit_per_minute": settings.rate_limit_per_minute
        }
    }


# 注册API路由
app.include_router(session.router, prefix=settings.api_prefix, tags=["会话管理"])
app.include_router(literature.router, prefix=settings.api_prefix, tags=["文科模式"])
app.include_router(science.router, prefix=settings.api_prefix, tags=["理科模式"])
app.include_router(chat.router, prefix=settings.api_prefix, tags=["智能对话"])
app.include_router(ocr.router, prefix=settings.api_prefix, tags=["OCR"])
app.include_router(feedback.router, prefix=settings.api_prefix, tags=["用户反馈"])
app.include_router(system.router, prefix=settings.api_prefix, tags=["系统"])


# WebSocket路由
@app.websocket("/ws/session/{session_id}")
async def websocket_route(websocket: WebSocket, session_id: str):
    """WebSocket连接端点"""
    await websocket_endpoint(websocket, session_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
