"""
智能对话Agent
使用Context-Aware ReAct模式进行对话
"""

import json
from typing import Any, Dict, List

from app.services.agents.base import BaseAgent, AgentConfig
from app.services.llm.model_router import TaskType


class ChatAgent(BaseAgent):
    """
    智能对话Agent

    功能：
    1. 上下文感知的对话
    2. 引导式学习
    3. 根据年级调整表达
    4. 提供可操作的建议
    """

    def __init__(self, grade_level: str = "middle", mode: str = "literature", subject: str = "") -> None:
        """
        初始化Chat Agent

        Args:
            grade_level: 年级水平
            mode: 学习模式
            subject: 科目
        """
        config = AgentConfig(
            name="chat_agent",
            task_type=TaskType.CHAT,
            temperature=0.8,  # 对话需要自然
            enable_cache=False  # 对话不缓存
        )
        super().__init__(config)
        self.grade_level = grade_level
        self.mode = mode
        self.subject = subject

    @property
    def system_prompt(self) -> str:
        """系统提示词"""
        return f"""你是一个友好、耐心的AI学习助手，专门帮助K12学生解决学习问题。

## 你的特点
- 语言亲切，像朋友一样交流
- 善于引导，而不是直接给答案
- 鼓励学生独立思考
- 根据学生年级调整表达方式

## 当前上下文
- 学生年级：{self.grade_level}
- 学习模式：{self.mode}
- 当前科目：{self.subject}

## 回答原则
1. 先理解学生的问题和困惑
2. 提供思路和方法，而非直接答案
3. 使用简单易懂的语言
4. 适当举例说明
5. 鼓励学生尝试

## 输出格式
请以JSON格式返回结果：
```json
{{
  "content": "回复内容",
  "message_type": "消息类型(suggestion/hint/explanation/encouragement)",
  "action_items": ["可操作建议1", "可操作建议2"],
  "follow_up_questions": ["后续问题1", "后续问题2"]
}}
```
"""

    def build_user_prompt(self, **kwargs: Any) -> str:
        """
        构建用户提示词

        Args:
            message: 用户消息
            context: 上下文信息
            chat_history: 对话历史

        Returns:
            用户提示词
        """
        message = kwargs.get("message", "")
        context = kwargs.get("context") or {}  # 确保context不是None
        chat_history = kwargs.get("chat_history", [])

        prompt = f"""## 学生的问题
{message}

"""

        # 添加上下文信息
        if context:
            prompt += "## 当前上下文\n"

            if context.get("cursor_position"):
                cursor = context["cursor_position"]
                prompt += f"- 学生正在编辑第 {cursor.get('line', 0)} 行\n"

            if context.get("selected_text"):
                prompt += f"- 选中的文本：\n```\n{context['selected_text']}\n```\n"

            if context.get("recent_analysis"):
                analysis = context["recent_analysis"]
                prompt += f"- 最近的分析结果：{analysis.get('type', '')} - {analysis.get('summary', '')}\n"

            prompt += "\n"

        # 添加对话历史
        if chat_history:
            prompt += "## 对话历史\n"
            for msg in chat_history[-5:]:  # 只保留最近5条
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    prompt += f"学生：{content}\n"
                elif role == "assistant":
                    prompt += f"助手：{content}\n"
            prompt += "\n"

        prompt += """## 回答要求
1. 理解学生的真实困惑
2. 提供引导性的建议，不要直接给答案
3. 使用适合学生年级的语言
4. 给出具体可操作的步骤
5. 提出后续问题，引导学生思考

请开始回答。
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
            if "content" not in result:
                result["content"] = "抱歉，我没有理解你的问题，能再说一遍吗？"

            if "message_type" not in result:
                result["message_type"] = "response"

            if "action_items" not in result:
                result["action_items"] = []

            if "follow_up_questions" not in result:
                result["follow_up_questions"] = []

            return result

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {str(e)}")
            # 如果解析失败，直接返回原始响应
            return {
                "content": response,
                "message_type": "response",
                "action_items": [],
                "follow_up_questions": []
            }

    def validate_inputs(self, **kwargs: Any) -> None:
        """验证输入参数"""
        message = kwargs.get("message")
        if not message:
            raise ValueError("message参数不能为空")

        if not isinstance(message, str):
            raise ValueError("message必须是字符串类型")

        if len(message) > 2000:
            raise ValueError(f"消息过长，最大支持2000字符，当前{len(message)}字符")
