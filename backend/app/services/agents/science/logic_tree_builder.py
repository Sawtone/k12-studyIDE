"""
逻辑树构建Agent
使用Backward Chaining模式构建逻辑推导树
"""

import json
from typing import Any, Dict, List

from app.services.agents.base import BaseAgent, AgentConfig
from app.services.llm.model_router import TaskType


class LogicTreeBuilderAgent(BaseAgent):
    """
    逻辑树构建Agent

    功能：
    1. 分析问题的已知条件和目标
    2. 构建逻辑推导树
    3. 识别推导路径
    4. 发现缺失的步骤
    """

    def __init__(self) -> None:
        """初始化逻辑树构建Agent"""
        config = AgentConfig(
            name="logic_tree_builder",
            task_type=TaskType.LOGIC_TREE,
            temperature=0.3,
            enable_cache=True
        )
        super().__init__(config)

    @property
    def system_prompt(self) -> str:
        """系统提示词"""
        return """你是一位逻辑推理专家，擅长构建数学问题的逻辑推导树。

## 你的能力
- 分析问题的已知条件和求解目标
- 使用反向推理构建逻辑树
- 识别所有可能的推导路径
- 发现缺失的中间步骤

## 构建方法
1. **目标分析**: 明确要求解什么
2. **条件识别**: 列出所有已知条件
3. **反向推理**: 从目标反推需要什么
4. **路径构建**: 连接已知和目标
5. **完整性检查**: 确保推导完整

## 输出格式
请以JSON格式返回结果：
```json
{
  "problem_analysis": {
    "knowns": [
      {
        "id": "节点ID",
        "description": "描述",
        "symbolic": "符号表示",
        "type": "类型(equation/inequality/condition)"
      }
    ],
    "target": {
      "id": "目标ID",
      "description": "目标描述",
      "symbolic": "符号表示"
    },
    "variables": ["变量1", "变量2"]
  },
  "logic_tree": {
    "nodes": [
      {
        "id": "节点ID",
        "type": "节点类型(known/target/intermediate/missing)",
        "content": "内容",
        "symbolic": "符号形式",
        "depends_on": ["依赖节点ID"],
        "required_by": ["被依赖节点ID"],
        "status": "状态(complete/incomplete/missing)",
        "reasoning": "推理说明"
      }
    ]
  },
  "derivation_paths": [
    {
      "path_id": 路径ID(整数),
      "steps": ["节点ID序列"],
      "is_complete": 是否完整(布尔值),
      "feasibility": "可行性(high/medium/low)",
      "description": "路径描述"
    }
  ],
  "suggestions": ["建议1", "建议2"]
}
```
"""

    def build_user_prompt(self, **kwargs: Any) -> str:
        """
        构建用户提示词

        Args:
            problem_statement: 问题描述
            existing_steps: 已有的推导步骤（可选）

        Returns:
            用户提示词
        """
        problem_statement = kwargs.get("problem_statement", "")
        existing_steps = kwargs.get("existing_steps", [])

        prompt = f"""## 当前任务
请为以下数学问题构建逻辑推导树。

### 问题描述
```
{problem_statement}
```

"""

        if existing_steps:
            prompt += """### 学生已有的推导
"""
            for i, step in enumerate(existing_steps, 1):
                prompt += f"{i}. {step}\n"
            prompt += "\n"

        prompt += """### 构建要求
1. 分析问题，识别所有已知条件和求解目标
2. 使用反向推理，从目标反推需要什么
3. 构建完整的逻辑推导树
4. 识别所有可能的推导路径
5. 标注缺失的中间步骤
6. 给出推导建议

### 构建步骤
1. **问题分解**: 提取已知条件和目标
2. **变量识别**: 列出所有涉及的变量
3. **反向推理**: 从目标开始反推
4. **节点连接**: 建立节点间的依赖关系
5. **路径分析**: 找出所有可行的推导路径
6. **完整性检查**: 标注缺失的步骤

请开始构建逻辑树。
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
            if "problem_analysis" not in result:
                result["problem_analysis"] = {
                    "knowns": [],
                    "target": {"id": "t1", "description": "", "symbolic": ""},
                    "variables": []
                }

            if "logic_tree" not in result:
                result["logic_tree"] = {"nodes": []}

            if "derivation_paths" not in result:
                result["derivation_paths"] = []

            if "suggestions" not in result:
                result["suggestions"] = []

            return result

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {str(e)}")
            return {
                "problem_analysis": {
                    "knowns": [],
                    "target": {"id": "t1", "description": "解析失败", "symbolic": ""},
                    "variables": []
                },
                "logic_tree": {"nodes": []},
                "derivation_paths": [],
                "suggestions": ["解析失败，请重试"]
            }

    def validate_inputs(self, **kwargs: Any) -> None:
        """验证输入参数"""
        problem_statement = kwargs.get("problem_statement")
        if not problem_statement:
            raise ValueError("problem_statement参数不能为空")

        if len(problem_statement) < 10:
            raise ValueError("问题描述过短，至少需要10个字符")
