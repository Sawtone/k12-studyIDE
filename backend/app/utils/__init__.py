"""
工具函数库
提供文本处理、数学计算、差分对比等通用工具
"""

from app.utils.text_tools import (
    tokenize_text,
    deduplicate_text,
    calculate_similarity,
    extract_keywords
)

from app.utils.math_tools import (
    parse_math_expression,
    latex_to_sympy,
    sympy_to_latex,
    validate_formula
)

from app.utils.diff_tools import (
    compute_diff,
    highlight_changes,
    get_change_summary
)

__all__ = [
    # 文本工具
    "tokenize_text",
    "deduplicate_text",
    "calculate_similarity",
    "extract_keywords",

    # 数学工具
    "parse_math_expression",
    "latex_to_sympy",
    "sympy_to_latex",
    "validate_formula",

    # 差分工具
    "compute_diff",
    "highlight_changes",
    "get_change_summary",
]
