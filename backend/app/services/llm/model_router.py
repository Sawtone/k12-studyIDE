"""
模型路由器
根据任务特征选择最合适的模型
"""

from typing import Optional
from enum import Enum

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TaskType(str, Enum):
    """任务类型枚举"""
    GRAMMAR_CHECK = "grammar_check"
    POLISH = "polish"
    STRUCTURE_ANALYSIS = "structure_analysis"
    HEALTH_SCORE = "health_score"
    MATH_VALIDATION = "math_validation"
    LOGIC_TREE = "logic_tree"
    DEBUG = "debug"
    CHAT = "chat"
    OCR = "ocr"
    QUICK_RESPONSE = "quick_response"


class ComplexityLevel(str, Enum):
    """复杂度级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ModelRouter:
    """
    模型路由器

    根据任务类型、内容长度、复杂度等因素选择最合适的模型
    """

    def __init__(self) -> None:
        """初始化模型路由器"""
        self.text_model = settings.qwen_text_model
        self.ocr_model = settings.qwen_ocr_model
        self.embedding_model = settings.qwen_embedding_model

        # 任务类型到模型的映射
        self.task_model_map = {
            TaskType.GRAMMAR_CHECK: self.text_model,
            TaskType.POLISH: self.text_model,
            TaskType.STRUCTURE_ANALYSIS: self.text_model,
            TaskType.HEALTH_SCORE: self.text_model,
            TaskType.MATH_VALIDATION: self.text_model,
            TaskType.LOGIC_TREE: self.text_model,
            TaskType.DEBUG: self.text_model,
            TaskType.CHAT: self.text_model,
            TaskType.OCR: self.ocr_model,
            TaskType.QUICK_RESPONSE: self.text_model,
        }

        logger.info(f"模型路由器已初始化: text={self.text_model}, ocr={self.ocr_model}")

    def select_model(
        self,
        task_type: TaskType,
        content_length: int = 0,
        complexity: ComplexityLevel = ComplexityLevel.MEDIUM,
        budget_constraint: Optional[float] = None
    ) -> str:
        """
        选择最合适的模型

        Args:
            task_type: 任务类型
            content_length: 内容长度（字符数）
            complexity: 复杂度级别
            budget_constraint: 预算约束（可选）

        Returns:
            模型名称
        """
        # 基础模型选择
        base_model = self.task_model_map.get(task_type, self.text_model)

        # OCR任务直接返回OCR模型
        if task_type == TaskType.OCR:
            logger.debug(f"任务类型: {task_type}, 选择模型: {base_model}")
            return base_model

        # 根据内容长度和复杂度调整
        # 注意：qwen3-max是统一的高性能模型，适合所有任务
        # 如果未来有更多模型选择，可以在这里添加逻辑

        selected_model = base_model

        logger.debug(
            f"任务类型: {task_type}, 内容长度: {content_length}, "
            f"复杂度: {complexity}, 选择模型: {selected_model}"
        )

        return selected_model

    def get_recommended_temperature(self, task_type: TaskType) -> float:
        """
        获取推荐的温度参数

        Args:
            task_type: 任务类型

        Returns:
            温度值
        """
        # 不同任务类型的推荐温度
        temperature_map = {
            TaskType.GRAMMAR_CHECK: 0.3,      # 语法检查需要精确
            TaskType.POLISH: 0.7,             # 润色需要创造性
            TaskType.STRUCTURE_ANALYSIS: 0.5, # 结构分析需要平衡
            TaskType.HEALTH_SCORE: 0.5,       # 评分需要客观
            TaskType.MATH_VALIDATION: 0.1,    # 数学验证需要极度精确
            TaskType.LOGIC_TREE: 0.3,         # 逻辑推导需要精确
            TaskType.DEBUG: 0.3,              # 调试需要精确
            TaskType.CHAT: 0.8,               # 对话需要自然
            TaskType.OCR: 0.1,                # OCR需要精确
            TaskType.QUICK_RESPONSE: 0.7,     # 快速响应可以灵活
        }

        return temperature_map.get(task_type, 0.7)

    def get_recommended_max_tokens(self, task_type: TaskType) -> int:
        """
        获取推荐的最大token数

        Args:
            task_type: 任务类型

        Returns:
            最大token数
        """
        # 不同任务类型的推荐最大token数
        max_tokens_map = {
            TaskType.GRAMMAR_CHECK: 2000,
            TaskType.POLISH: 3000,
            TaskType.STRUCTURE_ANALYSIS: 4000,
            TaskType.HEALTH_SCORE: 2000,
            TaskType.MATH_VALIDATION: 3000,
            TaskType.LOGIC_TREE: 4000,
            TaskType.DEBUG: 3000,
            TaskType.CHAT: 2000,
            TaskType.OCR: 2000,
            TaskType.QUICK_RESPONSE: 1000,
        }

        return max_tokens_map.get(task_type, 4000)


# 创建全局模型路由器实例
model_router = ModelRouter()
