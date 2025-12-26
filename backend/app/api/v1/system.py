"""
系统API路由
提供系统级别的查询接口
"""

from typing import Dict, Any, List
from fastapi import APIRouter
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/system", tags=["系统"])


@router.get(
    "/models",
    summary="获取可用的AI模型信息",
    description="返回系统支持的所有AI模型及其特性"
)
async def get_models() -> Dict[str, Any]:
    """
    获取可用的AI模型信息

    返回：
    - 模型列表
    - 每个模型的特性（速度、成本、推荐用途）
    - 模型能力说明
    """
    try:
        # 定义系统支持的模型信息
        models = [
            {
                "id": "qwen3-max",
                "name": "Qwen3 Max",
                "provider": "Alibaba Cloud",
                "type": "text",
                "speed": "fast",
                "cost": "low",
                "max_tokens": 8000,
                "recommended_for": [
                    "grammar_check",
                    "quick_response",
                    "chat",
                    "polish"
                ],
                "description": "通用文本生成模型，速度快，成本低，适合大多数场景",
                "capabilities": [
                    "文本生成",
                    "语法检查",
                    "文本润色",
                    "对话交互"
                ]
            },
            {
                "id": "qwen-vl-max",
                "name": "Qwen VL Max",
                "provider": "Alibaba Cloud",
                "type": "vision",
                "speed": "medium",
                "cost": "medium",
                "max_tokens": 4000,
                "recommended_for": [
                    "ocr",
                    "image_analysis",
                    "handwriting_recognition"
                ],
                "description": "视觉语言模型，支持图片理解和OCR识别",
                "capabilities": [
                    "图片文字识别",
                    "手写识别",
                    "图片理解",
                    "多模态分析"
                ]
            },
            {
                "id": "text-embedding-v3",
                "name": "Text Embedding V3",
                "provider": "Alibaba Cloud",
                "type": "embedding",
                "speed": "very_fast",
                "cost": "very_low",
                "max_tokens": 8192,
                "recommended_for": [
                    "semantic_search",
                    "similarity",
                    "clustering"
                ],
                "description": "文本嵌入模型，用于语义搜索和相似度计算",
                "capabilities": [
                    "文本向量化",
                    "语义搜索",
                    "相似度计算",
                    "文本聚类"
                ]
            }
        ]

        # 模型使用统计（可以从数据库或缓存中获取实际数据）
        usage_stats = {
            "qwen3-max": {
                "total_calls": 0,
                "avg_response_time_ms": 850,
                "success_rate": 0.99
            },
            "qwen-vl-max": {
                "total_calls": 0,
                "avg_response_time_ms": 1200,
                "success_rate": 0.98
            },
            "text-embedding-v3": {
                "total_calls": 0,
                "avg_response_time_ms": 150,
                "success_rate": 0.99
            }
        }

        # 模型选择建议
        recommendations = {
            "grammar_check": {
                "primary": "qwen3-max",
                "fallback": "qwen3-max",
                "reason": "快速准确的文本分析能力"
            },
            "structure_analysis": {
                "primary": "qwen3-max",
                "fallback": "qwen3-max",
                "reason": "强大的文本理解和结构分析能力"
            },
            "math_validation": {
                "primary": "qwen3-max",
                "fallback": "qwen3-max",
                "reason": "优秀的数学推理能力"
            },
            "ocr": {
                "primary": "qwen-vl-max",
                "fallback": "qwen-vl-max",
                "reason": "专业的视觉识别能力"
            },
            "chat": {
                "primary": "qwen3-max",
                "fallback": "qwen3-max",
                "reason": "自然流畅的对话能力"
            }
        }

        logger.info("获取模型信息成功")

        return {
            "models": models,
            "usage_stats": usage_stats,
            "recommendations": recommendations,
            "total_models": len(models)
        }

    except Exception as e:
        logger.error(f"获取模型信息失败: {str(e)}")
        # 即使出错也返回基本信息
        return {
            "models": [],
            "usage_stats": {},
            "recommendations": {},
            "total_models": 0,
            "error": str(e)
        }
