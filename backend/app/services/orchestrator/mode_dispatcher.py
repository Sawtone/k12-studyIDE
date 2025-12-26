"""
模式调度器
负责自动识别内容类型、模式切换管理
"""

import re
from typing import Dict, Any, Optional

from app.core.logging import get_logger
from app.core.exceptions import InvalidModeException
from app.services.llm.qwen_client import qwen_client

logger = get_logger(__name__)


class ModeDispatcher:
    """
    模式调度器

    职责：
    1. 自动识别内容类型（文科/理科）
    2. 模式切换管理
    3. 模式特定配置加载
    4. 能力暴露和限制
    """

    def __init__(self) -> None:
        """初始化模式调度器"""
        self.mode_configs = {
            "literature": self._get_literature_config(),
            "science": self._get_science_config()
        }
        logger.info("模式调度器已初始化")

    def _get_literature_config(self) -> Dict[str, Any]:
        """获取文科模式配置"""
        return {
            "name": "文科模式",
            "description": "适用于语文、英语等文科学习",
            "agents": [
                "grammar_checker",
                "polish",
                "structure_analyzer",
                "health_scorer"
            ],
            "ui_components": [
                "error_panel",
                "structure_tree",
                "health_score_card",
                "polish_suggestions"
            ],
            "shortcuts": {
                "Ctrl+G": "grammar_check",
                "Ctrl+P": "polish",
                "Ctrl+S": "structure_analysis",
                "Ctrl+H": "health_score"
            },
            "limits": {
                "max_content_length": 50000,
                "max_polish_length": 5000
            }
        }

    def _get_science_config(self) -> Dict[str, Any]:
        """获取理科模式配置"""
        return {
            "name": "理科模式",
            "description": "适用于数学、物理等理科学习",
            "agents": [
                "math_validator",
                "logic_tree_builder",
                "debugger"
            ],
            "ui_components": [
                "step_validator",
                "logic_tree_viewer",
                "debug_panel",
                "formula_editor"
            ],
            "shortcuts": {
                "Ctrl+V": "validate_steps",
                "Ctrl+L": "build_logic_tree",
                "Ctrl+D": "debug_mode"
            },
            "limits": {
                "max_content_length": 50000,
                "max_steps": 100
            }
        }

    async def detect_mode(self, content: str) -> str:
        """
        自动检测内容类型

        Args:
            content: 内容文本

        Returns:
            模式标识 (literature/science)
        """
        if not content or len(content) < 10:
            # 内容过短，默认为文科模式
            return "literature"

        # 规则1: 检查数学符号和公式
        math_patterns = [
            r'[+\-*/=<>≤≥≠]',  # 数学运算符
            r'\d+[xy]',  # 变量表达式
            r'[xy]\^?\d+',  # 幂次表达式
            r'\\frac|\\sqrt|\\sum|\\int',  # LaTeX公式
            r'[∫∑∏√∞]',  # 数学符号
            r'sin|cos|tan|log|ln',  # 数学函数
        ]

        math_score = 0
        for pattern in math_patterns:
            if re.search(pattern, content):
                math_score += 1

        # 规则2: 检查理科关键词
        science_keywords = [
            '已知', '求', '解方程', '证明', '计算',
            '设', '假设', '因为', '所以', '得',
            '方程', '不等式', '函数', '导数', '积分'
        ]

        for keyword in science_keywords:
            if keyword in content:
                math_score += 0.5

        # 规则3: 检查步骤编号
        if re.search(r'(步骤|解|解答)[:：]\s*\d+', content):
            math_score += 1

        # 规则4: 检查是否有明显的文科特征
        literature_patterns = [
            r'[，。！？；：""''（）《》]',  # 中文标点
            r'第[一二三四五六七八九十]+段',  # 段落标记
        ]

        literature_score = 0
        for pattern in literature_patterns:
            matches = re.findall(pattern, content)
            literature_score += len(matches) * 0.1

        # 判断模式
        if math_score >= 3:
            logger.info(f"检测为理科模式 (数学分数: {math_score}, 文科分数: {literature_score})")
            return "science"
        elif literature_score > math_score:
            logger.info(f"检测为文科模式 (数学分数: {math_score}, 文科分数: {literature_score})")
            return "literature"
        else:
            # 使用AI进行分类
            try:
                mode = await self._ai_detect_mode(content)
                logger.info(f"AI检测为: {mode}")
                return mode
            except Exception as e:
                logger.warning(f"AI检测失败: {str(e)}, 使用默认模式")
                return "literature"

    async def _ai_detect_mode(self, content: str) -> str:
        """
        使用AI检测内容类型

        Args:
            content: 内容文本

        Returns:
            模式标识
        """
        # 限制内容长度
        sample_content = content[:500] if len(content) > 500 else content

        system_prompt = """你是一个内容分类专家，请判断以下内容属于文科还是理科。

文科内容特征：
- 自然语言段落
- 文章、作文、阅读理解
- 语文、英语等学科

理科内容特征：
- 包含数学公式、方程
- 解题步骤、计算过程
- 数学、物理、化学等学科

请只回答"literature"或"science"。
"""

        user_prompt = f"""请判断以下内容的类型：

```
{sample_content}
```

请回答"literature"或"science"。
"""

        try:
            response = await qwen_client.complete(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                max_tokens=10
            )

            result = response.content.strip().lower()
            if "science" in result:
                return "science"
            else:
                return "literature"

        except Exception as e:
            logger.error(f"AI模式检测失败: {str(e)}")
            return "literature"

    async def switch_mode(
        self,
        session_id: str,
        from_mode: str,
        to_mode: str
    ) -> Dict[str, Any]:
        """
        切换模式

        Args:
            session_id: 会话ID
            from_mode: 原模式
            to_mode: 目标模式

        Returns:
            新模式的配置信息

        Raises:
            InvalidModeException: 无效的模式
        """
        # 验证目标模式
        if to_mode not in self.mode_configs:
            raise InvalidModeException(
                mode=to_mode,
                allowed_modes=list(self.mode_configs.keys())
            )

        logger.info(f"切换模式: {session_id}, {from_mode} -> {to_mode}")

        # 获取新模式配置
        new_config = self.mode_configs[to_mode]

        # 清理旧模式的缓存
        try:
            from app.cache.cache_strategies import session_cache, analysis_cache
            from datetime import datetime

            # 清理会话缓存中的模式相关数据
            await session_cache.delete_content(session_id)

            # 清理旧模式的分析结果缓存
            # 注意：这里只清理Redis缓存，数据库记录保留
            logger.info(f"已清理旧模式缓存: session={session_id}, mode={from_mode}")

        except Exception as e:
            logger.warning(f"清理旧模式缓存失败: {str(e)}")
            # 缓存清理失败不影响模式切换

        # 初始化新模式的Agent
        # 注意：Agent是无状态的，不需要特殊初始化
        # 只需要确保AgentCoordinator中已注册相应的Agent
        logger.info(f"新模式已就绪: session={session_id}, mode={to_mode}")

        return {
            "mode": to_mode,
            "config": new_config,
            "switched_at": datetime.utcnow().isoformat()
        }

    def get_mode_capabilities(self, mode: str) -> Dict[str, Any]:
        """
        获取模式能力

        Args:
            mode: 模式标识

        Returns:
            模式配置信息

        Raises:
            InvalidModeException: 无效的模式
        """
        if mode not in self.mode_configs:
            raise InvalidModeException(
                mode=mode,
                allowed_modes=list(self.mode_configs.keys())
            )

        return self.mode_configs[mode]

    def validate_operation(
        self,
        mode: str,
        operation: str
    ) -> bool:
        """
        验证操作是否适用于当前模式

        Args:
            mode: 模式标识
            operation: 操作名称

        Returns:
            是否允许
        """
        if mode not in self.mode_configs:
            return False

        config = self.mode_configs[mode]
        allowed_agents = config.get("agents", [])

        # 检查操作是否在允许的Agent列表中
        return operation in allowed_agents


# 创建全局模式调度器实例
mode_dispatcher = ModeDispatcher()
