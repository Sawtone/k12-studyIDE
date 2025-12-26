"""
语法检查Agent
使用Chain of Thought模式进行语法检查
"""

import json
from typing import Any, Dict, List

from app.services.agents.base import BaseAgent, AgentConfig
from app.services.llm.model_router import TaskType
from app.services.llm.prompt_manager import prompt_manager


class GrammarCheckerAgent(BaseAgent):
    """
    语法检查Agent

    功能：
    1. 识别错别字和拼写错误
    2. 检测语法问题
    3. 发现病句
    4. 标注标点符号误用
    """

    def __init__(self, grade_level: str = "middle") -> None:
        """
        初始化语法检查Agent

        Args:
            grade_level: 年级水平 (primary/middle/high)
        """
        config = AgentConfig(
            name="grammar_checker",
            task_type=TaskType.GRAMMAR_CHECK,
            temperature=0.3,  # 语法检查需要精确
            enable_cache=True
        )
        super().__init__(config)
        self.grade_level = grade_level

    @property
    def system_prompt(self) -> str:
        """系统提示词"""
        return prompt_manager.render_prompt(
            "grammar_checker_system",
            grade_level=self.grade_level
        )

    def build_user_prompt(self, **kwargs: Any) -> str:
        """
        构建用户提示词

        Args:
            content: 要检查的文本内容
            language: 语言 (zh/en)
            check_types: 检查类型列表
            context: 上下文信息（可选）

        Returns:
            用户提示词
        """
        content = kwargs.get("content", "")
        language = kwargs.get("language", "zh")
        check_types = kwargs.get("check_types", ["typo", "grammar", "syntax", "style"])
        context = kwargs.get("context") or {}  # 确保context不是None

        # 构建检查重点说明
        check_focus = "、".join({
            "typo": "错别字",
            "grammar": "语法错误",
            "syntax": "病句",
            "style": "表达风格"
        }.get(t, t) for t in check_types)

        prompt = f"""## 当前任务
请检查以下{self.grade_level}年级学生的作文：

### 作文内容
```
{content}
```

### 检查重点
{check_focus}

### 语言
{language}

"""

        # 如果有上下文信息，添加光标位置
        if context.get("cursor_position"):
            cursor = context["cursor_position"]
            prompt += f"""### 学生当前编辑位置
- 光标在第 {cursor.get('line', 0)} 行，第 {cursor.get('column', 0)} 列
- 请优先检查光标附近的内容

"""

        prompt += """### 检查要求
1. 使用Chain of Thought方式逐步思考
2. 对每个问题评估置信度（0-1）
3. 只输出置信度 ≥ 0.7 的错误
4. 解释要简单易懂，适合学生理解

### 输出格式
请严格按照以下JSON格式返回结果：
```json
{
  "errors": [
    {
      "type": "错误类型(typo/grammar/syntax/style)",
      "severity": "严重程度(low/medium/high)",
      "start_pos": 起始位置(整数),
      "end_pos": 结束位置(整数),
      "line_number": 行号(整数),
      "original_text": "原文本",
      "suggestion": "建议修改",
      "explanation": "错误说明",
      "confidence": 置信度(0-1的浮点数)
    }
  ],
  "summary": {
    "total_errors": 总错误数,
    "by_type": {
      "typo": 错别字数量,
      "grammar": 语法错误数量,
      "syntax": 病句数量,
      "style": 风格问题数量
    }
  }
}
```

请开始检查。
"""
        return prompt

    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        解析AI响应

        自动为每个错误生成唯一ID

        Args:
            response: AI响应文本

        Returns:
            解析后的结构化数据
        """
        try:
            # 尝试提取JSON内容
            response = response.strip()

            # 如果响应包含```json标记，提取其中的JSON
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
            if "errors" not in result:
                result["errors"] = []

            if "summary" not in result:
                result["summary"] = {
                    "total_errors": len(result["errors"]),
                    "by_type": {}
                }

            # 确保每个错误都有必需字段，并生成唯一ID
            import uuid
            for i, error in enumerate(result["errors"]):
                # 生成唯一ID（如果没有）
                if "id" not in error:
                    error["id"] = f"err_{uuid.uuid4().hex[:8]}_{i}"

                if "type" not in error:
                    error["type"] = "unknown"
                if "severity" not in error:
                    error["severity"] = "medium"
                if "confidence" not in error:
                    error["confidence"] = 0.8

            return result

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {str(e)}, 响应: {response[:200]}")
            # 返回空结果
            return {
                "errors": [],
                "summary": {
                    "total_errors": 0,
                    "by_type": {}
                }
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
        content = kwargs.get("content")
        if not content:
            raise ValueError("content参数不能为空")

        if not isinstance(content, str):
            raise ValueError("content必须是字符串类型")

        # 检查内容长度
        if len(content) > 50000:
            raise ValueError(f"内容过长，最大支持50000字符，当前{len(content)}字符")

        # 验证语言参数
        language = kwargs.get("language", "zh")
        if language not in ["zh", "en"]:
            raise ValueError(f"不支持的语言: {language}，仅支持zh和en")
