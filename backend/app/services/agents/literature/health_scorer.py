"""
健康度评分Agent
使用Multi-dimensional CoT模式进行多维度评分
"""

import json
from typing import Any, Dict

from app.services.agents.base import BaseAgent, AgentConfig
from app.services.llm.model_router import TaskType


class HealthScorerAgent(BaseAgent):
    """
    健康度评分Agent

    功能：
    1. 多维度评估文章质量
    2. 给出具体的改进建议
    3. 识别优势和不足
    """

    def __init__(self) -> None:
        """初始化健康度评分Agent"""
        config = AgentConfig(
            name="health_scorer",
            task_type=TaskType.HEALTH_SCORE,
            temperature=0.5,
            enable_cache=True
        )
        super().__init__(config)

    @property
    def system_prompt(self) -> str:
        """系统提示词"""
        return """你是一位专业的作文评分专家，擅长从多个维度评估文章质量。

## 评分维度
1. **结构** (structure): 文章组织是否清晰、层次是否分明
2. **连贯性** (coherence): 段落间逻辑是否连贯、过渡是否自然
3. **清晰度** (clarity): 表达是否清楚、是否易于理解
4. **语法** (grammar): 语法是否正确、标点是否恰当
5. **丰富度** (richness): 词汇是否丰富、表达是否多样

## 评分标准
- 每个维度评分范围: 0.0 - 1.0
- 0.0-0.4: 需要大幅改进
- 0.4-0.6: 有待提高
- 0.6-0.8: 良好
- 0.8-1.0: 优秀

## 输出格式
请以JSON格式返回结果：
```json
{
  "overall_score": 总分(0-1),
  "grade": "等级(A/B/C/D)",
  "dimensions": {
    "structure": {
      "score": 分数(0-1),
      "reasoning": "评分理由",
      "issues": ["问题1", "问题2"],
      "suggestions": ["建议1", "建议2"]
    },
    "coherence": {...},
    "clarity": {...},
    "grammar": {...},
    "richness": {...}
  },
  "top_priorities": ["优先改进项1", "优先改进项2", "优先改进项3"],
  "strengths": ["优势1", "优势2", "优势3"]
}
```
"""

    @staticmethod
    def build_user_prompt(**kwargs: Any) -> str:
        """
        构建用户提示词

        Args:
            content: 文章内容
            grade_level: 年级水平

        Returns:
            用户提示词
        """
        content = kwargs.get("content", "")
        grade_level = kwargs.get("grade_level", "middle")

        prompt = f"""## 当前任务
请评估以下{grade_level}年级学生的文章健康度。

### 文章内容
```
{content}
```

### 评估要求
1. 从5个维度进行评分：结构、连贯性、清晰度、语法、丰富度
2. 每个维度给出具体的评分理由
3. 指出存在的问题和改进建议
4. 识别文章的优势
5. 给出优先改进的3个方面

### 评估步骤
1. **整体阅读**: 理解文章主题和内容
2. **维度分析**: 逐个维度进行评估
3. **问题识别**: 找出每个维度的具体问题
4. **建议生成**: 提供可操作的改进建议
5. **综合评分**: 计算总分并给出等级

### 注意事项
- 评分要客观公正
- 建议要具体可行
- 考虑学生的年级水平
- 鼓励为主，指出不足时注意方式

请开始评估。
"""
        return prompt

    def parse_response(self, response: str) -> Dict[str, Any]:
        """解析AI响应"""
        try:
            response = response.strip()

            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()

            result = json.loads(response)

            # 验证必需字段
            if "overall_score" not in result:
                result["overall_score"] = 0.5

            if "grade" not in result:
                score = result["overall_score"]
                if score >= 0.9:
                    result["grade"] = "A"
                elif score >= 0.8:
                    result["grade"] = "B"
                elif score >= 0.6:
                    result["grade"] = "C"
                else:
                    result["grade"] = "D"

            if "dimensions" not in result:
                result["dimensions"] = {}

            # 确保所有维度都存在
            dimensions = ["structure", "coherence", "clarity", "grammar", "richness"]
            for dim in dimensions:
                if dim not in result["dimensions"]:
                    result["dimensions"][dim] = {
                        "score": 0.5,
                        "reasoning": "未评估",
                        "issues": [],
                        "suggestions": []
                    }

            if "top_priorities" not in result:
                result["top_priorities"] = []

            if "strengths" not in result:
                result["strengths"] = []

            return result

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {str(e)}")
            return {
                "overall_score": 0.0,
                "grade": "D",
                "dimensions": {
                    "structure": {"score": 0.0, "reasoning": "解析失败", "issues": [], "suggestions": []},
                    "coherence": {"score": 0.0, "reasoning": "解析失败", "issues": [], "suggestions": []},
                    "clarity": {"score": 0.0, "reasoning": "解析失败", "issues": [], "suggestions": []},
                    "grammar": {"score": 0.0, "reasoning": "解析失败", "issues": [], "suggestions": []},
                    "richness": {"score": 0.0, "reasoning": "解析失败", "issues": [], "suggestions": []}
                },
                "top_priorities": ["解析失败"],
                "strengths": []
            }

    @staticmethod
    def validate_inputs(**kwargs: Any) -> None:
        """验证输入参数"""
        content = kwargs.get("content")
        if not content:
            raise ValueError("content参数不能为空")

        if len(content) < 100:
            raise ValueError("文章过短，至少需要100个字符才能进行健康度评估")

        if len(content) > 50000:
            raise ValueError(f"文章过长，最大支持50000字符")
