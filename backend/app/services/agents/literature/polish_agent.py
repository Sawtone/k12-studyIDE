"""
文本润色Agent
使用ReAct模式进行文本润色
"""

import json
from typing import Any, Dict, List

from app.services.agents.base import BaseAgent, AgentConfig
from app.services.llm.model_router import TaskType
from app.services.llm.prompt_manager import prompt_manager


class PolishAgent(BaseAgent):
    """
    文本润色Agent

    功能：
    1. 优化句式结构
    2. 丰富词汇运用
    3. 增强文采
    4. 保持学生原有风格
    """

    def __init__(self) -> None:
        """初始化文本润色Agent"""
        config = AgentConfig(
            name="polish_agent",
            task_type=TaskType.POLISH,
            temperature=0.7,  # 润色需要创造性
            enable_cache=True
        )
        super().__init__(config)

    @property
    def system_prompt(self) -> str:
        """系统提示词"""
        return """你是一位经验丰富的写作指导老师，擅长帮助学生提升文章质量。

## 你的专长
- 优化句式结构，使表达更流畅
- 丰富词汇运用，避免重复单调
- 增强文采，使用恰当的修辞手法
- 保持学生原有的写作风格和个性

## 润色原则
1. 保留学生的核心思想和观点
2. 适度优化，不要过度修饰
3. 符合学生的年级水平
4. 提供多个版本供选择

## 输出格式
请以JSON格式返回结果：
```json
{
  "versions": [
    {
      "version": 版本号(整数),
      "polished_text": "润色后的文本",
      "style": "风格标签",
      "changes": ["变更说明1", "变更说明2"],
      "reasoning": "润色理由"
    }
  ],
  "recommended": 推荐版本号(整数),
  "recommendation_reason": "推荐理由"
}
```
"""

    def build_user_prompt(self, **kwargs: Any) -> str:
        """
        构建用户提示词

        Args:
            text: 要润色的文本
            polish_direction: 润色方向
            target_style: 目标风格
            context: 上下文（前文、后文）
            grade_level: 年级水平

        Returns:
            用户提示词
        """
        text = kwargs.get("text", "")
        polish_direction = kwargs.get("polish_direction", "enhance_fluency")
        target_style = kwargs.get("target_style", "formal")
        context = kwargs.get("context") or {}  # 确保context不是None
        grade_level = kwargs.get("grade_level", "middle")

        # 润色方向映射
        direction_map = {
            "enhance_fluency": "增强流畅度",
            "add_vividness": "增加生动性",
            "simplify": "简化表达",
            "formalize": "正式化表达"
        }

        # 风格映射
        style_map = {
            "formal": "正式",
            "casual": "随意",
            "literary": "文学性"
        }

        prompt = f"""## 当前任务
请对以下{grade_level}年级学生的文本进行润色。

### 原文本
```
{text}
```

### 润色方向
{direction_map.get(polish_direction, polish_direction)}

### 目标风格
{style_map.get(target_style, target_style)}

"""

        # 添加上下文
        if context.get("before"):
            prompt += f"""### 前文
```
{context['before']}
```

"""

        if context.get("after"):
            prompt += f"""### 后文
```
{context['after']}
```

"""

        prompt += """### 润色要求
1. 提供2-3个不同的润色版本
2. 每个版本都要说明具体的改动
3. 解释为什么这样改动
4. 推荐最合适的版本

### 注意事项
- 保持学生的核心思想不变
- 不要过度修饰，保持自然
- 符合学生的年级水平
- 考虑上下文的连贯性

请开始润色。
"""
        return prompt

    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        解析AI响应

        Args:
            response: AI响应文本

        Returns:
            解析后的结构化数据
        """
        try:
            # 提取JSON内容
            response = response.strip()

            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()

            # 解析JSON
            result = json.loads(response)

            # 验证必需字段
            if "versions" not in result:
                result["versions"] = []

            if "recommended" not in result and result["versions"]:
                result["recommended"] = 1

            if "recommendation_reason" not in result:
                result["recommendation_reason"] = "默认推荐第一个版本"

            # 确保每个版本都有必需字段
            for i, version in enumerate(result["versions"], 1):
                if "version" not in version:
                    version["version"] = i
                if "polished_text" not in version:
                    version["polished_text"] = ""
                if "style" not in version:
                    version["style"] = "standard"
                if "changes" not in version:
                    version["changes"] = []
                if "reasoning" not in version:
                    version["reasoning"] = ""

            return result

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {str(e)}, 响应: {response[:200]}")
            return {
                "versions": [],
                "recommended": 1,
                "recommendation_reason": "解析失败"
            }

    @staticmethod
    def validate_inputs(**kwargs: Any) -> None:
        """
        验证输入参数

        Args:
            **kwargs: 输入参数

        Raises:
            ValueError: 参数验证失败
        """
        text = kwargs.get("text")
        if not text:
            raise ValueError("text参数不能为空")

        if not isinstance(text, str):
            raise ValueError("text必须是字符串类型")

        # 检查文本长度
        if len(text) > 5000:
            raise ValueError(f"文本过长，最大支持5000字符，当前{len(text)}字符")

        if len(text) < 10:
            raise ValueError("文本过短，至少需要10个字符")
