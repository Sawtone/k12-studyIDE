"""
数学验证Agent
使用Symbolic CoT模式进行数学步骤验证
"""

import json
from typing import Any, Dict, List

from app.services.agents.base import BaseAgent, AgentConfig
from app.services.llm.model_router import TaskType


class MathValidatorAgent(BaseAgent):
    """
    数学验证Agent

    功能：
    1. 验证数学步骤的正确性
    2. 检查逻辑推导是否严密
    3. 识别常见错误
    4. 追踪变量状态变化
    """

    def __init__(self, mode: str = "validate", grade_level: str = "middle", **kwargs) -> None:
        """
        初始化数学验证Agent

        Args:
            mode: 模式 (validate: 验证模式, decompose: 分解模式)
            grade_level: 年级水平
        """
        config = AgentConfig(
            name="math_validator",
            task_type=TaskType.MATH_VALIDATION,
            temperature=0.1,  # 数学验证需要极度精确
            enable_cache=True
        )
        super().__init__(config)
        self.mode = mode
        self.grade_level = grade_level

    @property
    def system_prompt(self) -> str:
        """系统提示词"""
        return """你是一位严谨的数学老师，专门帮助学生检查数学解题步骤。

## 你的职责
- 验证每个步骤的数学正确性
- 检查逻辑推导是否严密
- 识别常见错误（符号错误、运算错误等）
- 追踪变量状态变化

## 验证方法
1. **符号化表示**: 将步骤转换为数学符号
2. **逻辑检查**: 验证推导是否合理
3. **运算验证**: 检查计算是否正确
4. **完整性检查**: 是否遗漏必要步骤

## 输出格式
请以JSON格式返回结果：
```json
{
  "validation_results": [
    {
      "step_number": 步骤号(整数),
      "is_valid": 是否有效(布尔值),
      "symbolic_form": "符号化形式",
      "variables_state": {
        "变量名": {
          "value": "值",
          "constraints": "约束条件"
        }
      },
      "errors": [
        {
          "type": "错误类型",
          "description": "错误描述",
          "correction": "正确做法"
        }
      ],
      "warnings": ["警告1", "警告2"],
      "next_step_hint": "下一步提示"
    }
  ],
  "overall_assessment": {
    "total_steps": 总步骤数(整数),
    "valid_steps": 有效步骤数(整数),
    "completion_status": "完成状态(complete/incomplete/invalid)"
  }
}
```
"""

    def build_user_prompt(self, **kwargs: Any) -> str:
        """
        构建用户提示词

        Args:
            problem_statement: 问题描述
            steps: 解题步骤列表

        Returns:
            用户提示词
        """
        problem_statement = kwargs.get("problem_statement", "")
        steps = kwargs.get("steps", [])

        prompt = f"""## 当前任务
请验证以下数学解题步骤的正确性。

### 问题描述
```
{problem_statement}
```

### 学生的解题步骤
"""

        for i, step in enumerate(steps, 1):
            step_content = step.get("content", "")
            formula = step.get("formula", "")
            prompt += f"""
**步骤 {i}**:
- 描述: {step_content}
- 公式: {formula}
"""

        prompt += """

### 验证要求
1. 逐步验证每个步骤的正确性
2. 将步骤转换为符号化形式
3. 追踪每个步骤后的变量状态
4. 识别错误并给出正确做法
5. 提供下一步的提示

### 验证步骤
1. **理解问题**: 明确已知条件和求解目标
2. **符号化**: 将每个步骤转换为数学符号
3. **逻辑验证**: 检查推导是否合理
4. **运算检查**: 验证计算是否正确
5. **状态追踪**: 记录变量的变化
6. **完整性**: 检查是否遗漏步骤

请开始验证。
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
            if "validation_results" not in result:
                result["validation_results"] = []

            # 确保每个验证结果都有必需字段
            for validation in result["validation_results"]:
                if "step_number" not in validation:
                    validation["step_number"] = 0
                if "is_valid" not in validation:
                    validation["is_valid"] = False
                if "symbolic_form" not in validation:
                    validation["symbolic_form"] = ""
                if "variables_state" not in validation:
                    validation["variables_state"] = {}
                if "errors" not in validation:
                    validation["errors"] = []
                if "warnings" not in validation:
                    validation["warnings"] = []
                if "next_step_hint" not in validation:
                    validation["next_step_hint"] = ""

            if "overall_assessment" not in result:
                total = len(result["validation_results"])
                valid = sum(1 for v in result["validation_results"] if v.get("is_valid", False))
                result["overall_assessment"] = {
                    "total_steps": total,
                    "valid_steps": valid,
                    "completion_status": "complete" if valid == total else "incomplete"
                }

            return result

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {str(e)}")
            return {
                "validation_results": [],
                "overall_assessment": {
                    "total_steps": 0,
                    "valid_steps": 0,
                    "completion_status": "invalid"
                }
            }

    def validate_inputs(self, **kwargs: Any) -> None:
        """验证输入参数"""
        problem_statement = kwargs.get("problem_statement")
        if not problem_statement:
            raise ValueError("problem_statement参数不能为空")

        steps = kwargs.get("steps")
        if steps is None:
            raise ValueError("steps参数不能为空")

        if not isinstance(steps, list):
            raise ValueError("steps必须是列表类型")

        # 在decompose模式下，允许空步骤列表
        if len(steps) == 0 and self.mode != "decompose":
            raise ValueError("至少需要提供一个解题步骤")
