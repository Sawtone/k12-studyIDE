"""
结构分析Agent
使用Tree of Thought模式分析文章结构
"""

import json
from typing import Any, Dict, List

from app.services.agents.base import BaseAgent, AgentConfig
from app.services.llm.model_router import TaskType


class StructureAnalyzerAgent(BaseAgent):
    """
    结构分析Agent

    功能：
    1. 分析文章整体结构
    2. 识别段落层次关系
    3. 分析逻辑连贯性
    4. 生成结构树
    """

    def __init__(self) -> None:
        """初始化结构分析Agent"""
        config = AgentConfig(
            name="structure_analyzer",
            task_type=TaskType.STRUCTURE_ANALYSIS,
            temperature=0.5,
            enable_cache=True
        )
        super().__init__(config)

    @property
    def system_prompt(self) -> str:
        """系统提示词"""
        return """你是一位专业的文章结构分析专家，擅长分析文章的组织结构和逻辑关系。

## 你的能力
- 识别文章的整体结构模式（总分总、并列式、递进式等）
- 分析段落之间的层次关系
- 评估逻辑连贯性
- 生成可视化的结构树

## 分析维度
1. **整体结构**: 识别文章的组织模式
2. **段落层次**: 分析段落的主次关系
3. **逻辑关系**: 识别段落间的连接方式（因果、转折、并列等）
4. **完整性**: 评估结构的完整性

## 输出格式
请以JSON格式返回结果：
```json
{
  "structure_type": "结构类型",
  "overall_pattern": "整体模式",
  "tree": {
    "id": "节点ID",
    "type": "节点类型(root/section/paragraph/sentence)",
    "title": "标题",
    "summary": "摘要",
    "start_pos": 起始位置,
    "end_pos": 结束位置,
    "children": [子节点数组]
  },
  "relationships": [
    {
      "from": "源节点ID",
      "to": "目标节点ID",
      "relation": "关系类型(sequence/cause/contrast/parallel)"
    }
  ],
  "analysis": {
    "coherence_score": 连贯性分数(0-1),
    "completeness_score": 完整性分数(0-1),
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"]
  }
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
请分析以下{grade_level}年级学生的文章结构。

### 文章内容
```
{content}
```

### 分析要求
1. 识别文章的整体结构类型（议论文、记叙文、说明文等）
2. 分析段落的层次关系，构建结构树
3. 识别段落之间的逻辑关系
4. 评估结构的连贯性和完整性
5. 提供改进建议

### 分析步骤
1. **整体阅读**: 理解文章主题和写作目的
2. **段落划分**: 识别自然段和逻辑段
3. **层次分析**: 确定段落的主次关系
4. **关系识别**: 分析段落间的逻辑连接
5. **评估总结**: 给出整体评价和建议

请开始分析。
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
            if "structure_type" not in result:
                result["structure_type"] = "unknown"

            if "overall_pattern" not in result:
                result["overall_pattern"] = "未识别"

            if "tree" not in result:
                result["tree"] = {
                    "id": "root",
                    "type": "root",
                    "title": "全文",
                    "summary": "",
                    "start_pos": 0,
                    "end_pos": 0,
                    "children": []
                }

            if "relationships" not in result:
                result["relationships"] = []

            if "analysis" not in result:
                result["analysis"] = {
                    "coherence_score": 0.5,
                    "completeness_score": 0.5,
                    "issues": [],
                    "suggestions": []
                }

            return result

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {str(e)}")
            return {
                "structure_type": "unknown",
                "overall_pattern": "解析失败",
                "tree": {
                    "id": "root",
                    "type": "root",
                    "title": "全文",
                    "summary": "",
                    "start_pos": 0,
                    "end_pos": 0,
                    "children": []
                },
                "relationships": [],
                "analysis": {
                    "coherence_score": 0.0,
                    "completeness_score": 0.0,
                    "issues": ["解析失败"],
                    "suggestions": []
                }
            }

    @staticmethod
    def validate_inputs(**kwargs: Any) -> None:
        """验证输入参数"""
        content = kwargs.get("content")
        if not content:
            raise ValueError("content参数不能为空")

        if len(content) < 50:
            raise ValueError("文章过短，至少需要50个字符才能进行结构分析")

        if len(content) > 50000:
            raise ValueError(f"文章过长，最大支持50000字符")
