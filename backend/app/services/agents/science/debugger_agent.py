"""
Debugger Agent - 断点调试Agent
使用State Tracking模式，追踪数学解题过程中的状态变化
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.services.agents.base import BaseAgent, AgentConfig, AgentResult
from app.services.llm.qwen_client import QwenClient
from app.core.logging import get_logger

logger = get_logger(__name__)


class VariableState(BaseModel):
    """变量状态"""
    name: str
    value: str
    type: str  # 'known', 'unknown', 'derived'
    how_derived: Optional[str] = None
    constraints: Optional[str] = None


class ExecutionStep(BaseModel):
    """执行步骤"""
    step_number: int
    content: str
    formula: Optional[str] = None
    variables_before: Dict[str, VariableState]
    variables_after: Dict[str, VariableState]
    operation: str
    is_valid: bool
    notes: Optional[str] = None


class DebugInsight(BaseModel):
    """调试洞察"""
    type: str  # 'warning', 'suggestion', 'error', 'info'
    message: str
    related_step: Optional[int] = None
    severity: str = 'medium'


class DebuggerAgent(BaseAgent):
    """
    断点调试Agent

    职责：
    1. 在指定步骤设置断点
    2. 追踪变量状态变化
    3. 检查已用和未用条件
    4. 提供调试洞察和建议
    5. 验证当前状态的正确性

    使用State Tracking模式：
    - 维护完整的状态历史
    - 追踪每个变量的来源
    - 识别未使用的条件
    - 提供下一步可能的操作
    """

    def __init__(self, **kwargs) -> None:
        """初始化调试Agent"""
        config = AgentConfig(
            name="debugger",
            task_type="debug",
            temperature=0.3,
            enable_cache=False
        )
        super().__init__(config)
        self.logger = logger

    @property
    def system_prompt(self) -> str:
        """系统提示词"""
        return """你是一个专业的数学解题调试助手，帮助学生理解解题过程中的每一步。

## 你的角色
- 像调试器一样，追踪解题过程中的状态变化
- 帮助学生理解"为什么这样做"
- 发现潜在的错误和遗漏
- 提供清晰的调试信息

## 核心能力
1. **状态追踪**：记录每个变量在每一步的值和来源
2. **条件检查**：识别哪些已知条件被使用了，哪些还没用
3. **错误检测**：发现逻辑错误、计算错误、遗漏步骤
4. **建议生成**：提供下一步可能的操作

## 调试步骤（State Tracking模式）
1. **初始化状态**
   - 列出所有已知条件
   - 标记目标（要求什么）
   - 初始化变量表

2. **逐步追踪**
   - 对于每一步：
     * 记录步骤前的变量状态
     * 分析这一步做了什么操作
     * 记录步骤后的变量状态
     * 标记使用了哪些条件

3. **断点分析**
   - 在断点处：
     * 显示当前所有变量的值
     * 列出已使用的条件
     * 列出未使用的条件
     * 检查是否有矛盾

4. **洞察生成**
   - 发现问题：
     * 变量值不合理
     * 有未使用的重要条件
     * 推导路径可能有误
   - 提供建议：
     * 下一步可以做什么
     * 可能的替代方法

## 输出格式（JSON）
{
  "execution_trace": [
    {
      "step_number": 1,
      "content": "步骤描述",
      "formula": "LaTeX公式",
      "variables_before": {"x": {"value": "unknown", "type": "unknown"}},
      "variables_after": {"x": {"value": "2", "type": "derived", "how_derived": "从方程求解"}},
      "operation": "求解方程",
      "is_valid": true,
      "notes": "备注"
    }
  ],
  "current_state": {
    "variables": {
      "x": {
        "value": "2",
        "type": "derived",
        "how_derived": "从x+3=5求解",
        "constraints": "x ∈ ℝ"
      }
    },
    "used_conditions": ["x + 3 = 5"],
    "unused_conditions": ["x > 0"],
    "target_status": "partially_achieved"
  },
  "insights": [
    {
      "type": "warning",
      "message": "还有一个条件'x > 0'没有使用，需要验证x=2是否满足",
      "related_step": 1,
      "severity": "medium"
    }
  ],
  "next_possible_actions": [
    "验证x=2是否满足x>0的条件",
    "将x=2代入原方程检验"
  ],
  "validation": {
    "is_correct_so_far": true,
    "issues": [],
    "suggestions": ["建议验证所有条件"]
  }
}

## 重要原则
- 状态追踪要完整，不遗漏任何变量
- 清楚标注每个值的来源
- 用学生能理解的语言解释
- 发现问题时要指出具体位置
"""

    def build_user_prompt(self, **kwargs) -> str:
        """生成用户提示词（实现BaseAgent的抽象方法）"""
        problem_statement = kwargs.get('problem_statement', '')
        steps = kwargs.get('steps', [])
        breakpoint_step = kwargs.get('breakpoint_step_number', len(steps))
        grade_level = kwargs.get('grade_level', 'middle')

        # 构建步骤列表
        steps_text = ""
        for i, step in enumerate(steps, 1):
            steps_text += f"\n步骤 {i}:\n"
            steps_text += f"  内容: {step.get('content', '')}\n"
            if step.get('formula'):
                steps_text += f"  公式: {step.get('formula')}\n"

        prompt = f"""## 调试任务

### 题目
{problem_statement}

### 学生的解题步骤
{steps_text}

### 断点位置
在第 {breakpoint_step} 步设置断点，请分析到这一步为止的状态。

### 年级水平
{grade_level}（请用适合该年级的语言解释）

### 调试要求
1. **完整追踪**：从第1步到第{breakpoint_step}步，追踪所有变量的状态变化
2. **状态快照**：在断点处，给出当前所有变量的值和来源
3. **条件检查**：列出已使用和未使用的条件
4. **问题发现**：如果有错误或遗漏，明确指出
5. **建议生成**：提供接下来可以做什么

### 特别注意
- 每个变量的值都要说明是如何得到的
- 如果某个条件还没用到，要提醒学生
- 如果发现计算错误，要指出具体在哪一步
- 建议要具体可操作

请开始调试分析，输出JSON格式的结果。
"""
        return prompt

    def validate_inputs(self, **kwargs: Any) -> None:
        """验证输入参数"""
        if 'problem_statement' not in kwargs:
            raise ValueError("缺少problem_statement参数")
        if 'steps' not in kwargs or not kwargs['steps']:
            raise ValueError("缺少steps参数或steps为空")

    def parse_response(self, response: str) -> Dict[str, Any]:
        """解析AI响应（实现BaseAgent的抽象方法）"""
        try:
            import json

            # 清理响应字符串
            response = response.strip()

            # 提取JSON内容
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
            required_fields = ['execution_trace', 'current_state', 'insights', 'next_possible_actions']
            for field in required_fields:
                if field not in result:
                    self.logger.warning(f"缺少字段: {field}")
                    result[field] = [] if field in ['insights', 'next_possible_actions'] else {}

            return {
                'execution_trace': result.get('execution_trace', []),
                'current_state': result.get('current_state', {}),
                'insights': result.get('insights', []),
                'next_possible_actions': result.get('next_possible_actions', []),
                'validation': result.get('validation', {
                    'is_correct_so_far': True,
                    'issues': [],
                    'suggestions': []
                })
            }

        except Exception as e:
            self.logger.error(f"解析调试结果失败: {str(e)}")
            return {
                'execution_trace': [],
                'current_state': {},
                'insights': [{
                    'type': 'error',
                    'message': f'解析失败: {str(e)}',
                    'severity': 'high'
                }],
                'next_possible_actions': [],
                'validation': {
                    'is_correct_so_far': False,
                    'issues': ['解析失败'],
                    'suggestions': []
                }
            }
