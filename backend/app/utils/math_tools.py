"""
数学工具
提供数学公式解析、LaTeX转换、符号化表示、公式验证等功能
"""

import re
from typing import Dict, Any, Optional, List, Tuple, Union
from sympy import (
    sympify, latex, simplify, expand, factor,
    solve, diff, integrate, Symbol, Expr,
    SympifyError, parse_expr
)
from sympy.parsing.latex import parse_latex

from app.core.logging import get_logger

logger = get_logger(__name__)


def parse_math_expression(
    expression: str,
    variables: Optional[List[str]] = None,
    simplify_result: bool = True
) -> Dict[str, Any]:
    """
    解析数学表达式

    Args:
        expression: 数学表达式字符串
        variables: 变量列表（可选）
        simplify_result: 是否简化结果

    Returns:
        解析结果字典，包含:
            - success: 是否成功
            - expr: SymPy表达式对象
            - latex: LaTeX格式
            - variables: 变量列表
            - error: 错误信息（如果失败）

    Examples:
        >>> parse_math_expression("x**2 + 2*x + 1")
        {'success': True, 'expr': x**2 + 2*x + 1, 'latex': 'x^{2} + 2 x + 1', ...}
    """
    try:
        # 预处理表达式
        expression = _preprocess_expression(expression)

        # 解析表达式
        if variables:
            # 创建符号变量
            symbols = {var: Symbol(var) for var in variables}
            expr = parse_expr(expression, local_dict=symbols)
        else:
            expr = sympify(expression)

        # 简化表达式
        if simplify_result:
            expr = simplify(expr)

        # 提取变量
        expr_variables = sorted([str(s) for s in expr.free_symbols])

        # 转换为LaTeX
        latex_str = latex(expr)

        logger.debug(f"数学表达式解析成功: {expression}")

        return {
            'success': True,
            'expr': expr,
            'latex': latex_str,
            'variables': expr_variables,
            'original': expression
        }

    except SympifyError as e:
        logger.error(f"数学表达式解析失败: {str(e)}")
        return {
            'success': False,
            'error': f"解析失败: {str(e)}",
            'original': expression
        }
    except Exception as e:
        logger.error(f"数学表达式解析异常: {str(e)}")
        return {
            'success': False,
            'error': f"未知错误: {str(e)}",
            'original': expression
        }


def latex_to_sympy(
    latex_str: str,
    simplify_result: bool = True
) -> Dict[str, Any]:
    """
    将LaTeX表达式转换为SymPy表达式

    Args:
        latex_str: LaTeX格式的数学表达式
        simplify_result: 是否简化结果

    Returns:
        转换结果字典

    Examples:
        >>> latex_to_sympy(r"\\frac{x^2 + 1}{x}")
        {'success': True, 'expr': (x**2 + 1)/x, ...}
    """
    try:
        # 清理LaTeX字符串
        latex_str = latex_str.strip()
        if latex_str.startswith('$') and latex_str.endswith('$'):
            latex_str = latex_str[1:-1]
        if latex_str.startswith('$$') and latex_str.endswith('$$'):
            latex_str = latex_str[2:-2]

        # 解析LaTeX
        expr = parse_latex(latex_str)

        # 简化表达式
        if simplify_result:
            expr = simplify(expr)

        # 提取变量
        variables = sorted([str(s) for s in expr.free_symbols])

        logger.debug(f"LaTeX转换成功: {latex_str}")

        return {
            'success': True,
            'expr': expr,
            'variables': variables,
            'original_latex': latex_str
        }

    except Exception as e:
        logger.error(f"LaTeX转换失败: {str(e)}")
        return {
            'success': False,
            'error': f"转换失败: {str(e)}",
            'original_latex': latex_str
        }


def sympy_to_latex(
    expr: Union[Expr, str],
    mode: str = "equation"
) -> str:
    """
    将SymPy表达式转换为LaTeX格式

    Args:
        expr: SymPy表达式或字符串
        mode: 输出模式
            - equation: 完整方程格式 ($$...$$)
            - inline: 行内格式 ($...$)
            - plain: 纯LaTeX代码

    Returns:
        LaTeX格式字符串

    Examples:
        >>> sympy_to_latex("x**2 + 1", mode="inline")
        '$x^{2} + 1$'
    """
    try:
        # 如果是字符串，先解析
        if isinstance(expr, str):
            result = parse_math_expression(expr)
            if not result['success']:
                return expr
            expr = result['expr']

        # 转换为LaTeX
        latex_str = latex(expr)

        # 根据模式添加包装
        if mode == "equation":
            return f"$${latex_str}$$"
        elif mode == "inline":
            return f"${latex_str}$"
        else:  # plain
            return latex_str

    except Exception as e:
        logger.error(f"SymPy转LaTeX失败: {str(e)}")
        return str(expr)


def validate_formula(
    formula: str,
    expected_variables: Optional[List[str]] = None,
    check_syntax: bool = True,
    check_balance: bool = True
) -> Dict[str, Any]:
    """
    验证数学公式

    Args:
        formula: 数学公式字符串
        expected_variables: 期望的变量列表
        check_syntax: 是否检查语法
        check_balance: 是否检查括号平衡

    Returns:
        验证结果字典，包含:
            - valid: 是否有效
            - errors: 错误列表
            - warnings: 警告列表
            - variables: 实际变量列表

    Examples:
        >>> validate_formula("x**2 + 2*x + 1", expected_variables=["x"])
        {'valid': True, 'errors': [], 'warnings': [], 'variables': ['x']}
    """
    errors = []
    warnings = []
    variables = []

    try:
        # 检查括号平衡
        if check_balance:
            balance_errors = _check_bracket_balance(formula)
            errors.extend(balance_errors)

        # 检查语法
        if check_syntax:
            parse_result = parse_math_expression(formula, simplify_result=False)

            if not parse_result['success']:
                errors.append(f"语法错误: {parse_result.get('error', '未知错误')}")
            else:
                variables = parse_result['variables']

                # 检查期望变量
                if expected_variables:
                    expected_set = set(expected_variables)
                    actual_set = set(variables)

                    # 缺失的变量
                    missing = expected_set - actual_set
                    if missing:
                        warnings.append(f"缺失变量: {', '.join(missing)}")

                    # 多余的变量
                    extra = actual_set - expected_set
                    if extra:
                        warnings.append(f"未预期的变量: {', '.join(extra)}")

        # 检查常见错误模式
        pattern_errors = _check_common_patterns(formula)
        warnings.extend(pattern_errors)

        valid = len(errors) == 0

        logger.debug(f"公式验证完成: valid={valid}, errors={len(errors)}, warnings={len(warnings)}")

        return {
            'valid': valid,
            'errors': errors,
            'warnings': warnings,
            'variables': variables,
            'formula': formula
        }

    except Exception as e:
        logger.error(f"公式验证异常: {str(e)}")
        return {
            'valid': False,
            'errors': [f"验证异常: {str(e)}"],
            'warnings': warnings,
            'variables': variables,
            'formula': formula
        }


def solve_equation(
    equation: str,
    variable: str,
    domain: str = "real"
) -> Dict[str, Any]:
    """
    求解方程

    Args:
        equation: 方程字符串（如 "x**2 - 4 = 0"）
        variable: 求解变量
        domain: 求解域 ('real', 'complex')

    Returns:
        求解结果字典

    Examples:
        >>> solve_equation("x**2 - 4 = 0", "x")
        {'success': True, 'solutions': [-2, 2], ...}
    """
    try:
        # 分割等式
        if '=' in equation:
            left, right = equation.split('=', 1)
            expr = sympify(left) - sympify(right)
        else:
            expr = sympify(equation)

        # 创建变量符号
        var_symbol = Symbol(variable, real=(domain == 'real'))

        # 求解
        solutions = solve(expr, var_symbol)

        # 转换解为字符串和LaTeX
        solutions_str = [str(sol) for sol in solutions]
        solutions_latex = [latex(sol) for sol in solutions]

        logger.debug(f"方程求解成功: {len(solutions)} 个解")

        return {
            'success': True,
            'solutions': solutions,
            'solutions_str': solutions_str,
            'solutions_latex': solutions_latex,
            'equation': equation,
            'variable': variable
        }

    except Exception as e:
        logger.error(f"方程求解失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'equation': equation,
            'variable': variable
        }


def differentiate(
    expression: str,
    variable: str,
    order: int = 1
) -> Dict[str, Any]:
    """
    求导数

    Args:
        expression: 表达式字符串
        variable: 求导变量
        order: 求导阶数

    Returns:
        求导结果字典

    Examples:
        >>> differentiate("x**3 + 2*x", "x")
        {'success': True, 'derivative': 3*x**2 + 2, ...}
    """
    try:
        # 解析表达式
        expr = sympify(expression)
        var_symbol = Symbol(variable)

        # 求导
        derivative = diff(expr, var_symbol, order)

        # 简化
        derivative_simplified = simplify(derivative)

        logger.debug(f"求导成功: {order}阶导数")

        return {
            'success': True,
            'derivative': derivative_simplified,
            'derivative_str': str(derivative_simplified),
            'derivative_latex': latex(derivative_simplified),
            'original': expression,
            'variable': variable,
            'order': order
        }

    except Exception as e:
        logger.error(f"求导失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'original': expression,
            'variable': variable
        }


def integrate_expression(
    expression: str,
    variable: str,
    definite: bool = False,
    lower_bound: Optional[float] = None,
    upper_bound: Optional[float] = None
) -> Dict[str, Any]:
    """
    求积分

    Args:
        expression: 表达式字符串
        variable: 积分变量
        definite: 是否为定积分
        lower_bound: 下界（定积分）
        upper_bound: 上界（定积分）

    Returns:
        积分结果字典

    Examples:
        >>> integrate_expression("x**2", "x")
        {'success': True, 'integral': x**3/3, ...}
    """
    try:
        # 解析表达式
        expr = sympify(expression)
        var_symbol = Symbol(variable)

        # 求积分
        if definite and lower_bound is not None and upper_bound is not None:
            result = integrate(expr, (var_symbol, lower_bound, upper_bound))
        else:
            result = integrate(expr, var_symbol)

        # 简化
        result_simplified = simplify(result)

        logger.debug(f"积分成功: {'定积分' if definite else '不定积分'}")

        return {
            'success': True,
            'integral': result_simplified,
            'integral_str': str(result_simplified),
            'integral_latex': latex(result_simplified),
            'original': expression,
            'variable': variable,
            'definite': definite
        }

    except Exception as e:
        logger.error(f"积分失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'original': expression,
            'variable': variable
        }


# ============================================
# 辅助函数
# ============================================

def _preprocess_expression(expression: str) -> str:
    """
    预处理数学表达式

    Args:
        expression: 原始表达式

    Returns:
        处理后的表达式
    """
    # 移除空白
    expression = expression.strip()

    # 替换常见符号
    replacements = {
        '×': '*',
        '÷': '/',
        '²': '**2',
        '³': '**3',
        '√': 'sqrt',
    }

    for old, new in replacements.items():
        expression = expression.replace(old, new)

    return expression


def _check_bracket_balance(expression: str) -> List[str]:
    """
    检查括号平衡

    Args:
        expression: 表达式字符串

    Returns:
        错误列表
    """
    errors = []
    brackets = {'(': ')', '[': ']', '{': '}'}
    stack = []

    for i, char in enumerate(expression):
        if char in brackets:
            stack.append((char, i))
        elif char in brackets.values():
            if not stack:
                errors.append(f"位置 {i}: 多余的右括号 '{char}'")
            else:
                left, left_pos = stack.pop()
                if brackets[left] != char:
                    errors.append(
                        f"位置 {left_pos}-{i}: 括号不匹配 '{left}' 和 '{char}'"
                    )

    # 检查未闭合的括号
    for left, pos in stack:
        errors.append(f"位置 {pos}: 未闭合的左括号 '{left}'")

    return errors


def _check_common_patterns(expression: str) -> List[str]:
    """
    检查常见错误模式

    Args:
        expression: 表达式字符串

    Returns:
        警告列表
    """
    warnings = []

    # 连续运算符
    if re.search(r'[+\-*/]{2,}', expression):
        warnings.append("检测到连续运算符")

    # 空括号
    if '()' in expression:
        warnings.append("检测到空括号")

    # 除以零
    if re.search(r'/\s*0(?!\d)', expression):
        warnings.append("可能存在除以零")

    return warnings


def simplify_expression(
    expression: str,
    method: str = "simplify"
) -> Dict[str, Any]:
    """
    简化表达式

    Args:
        expression: 表达式字符串
        method: 简化方法
            - simplify: 通用简化
            - expand: 展开
            - factor: 因式分解

    Returns:
        简化结果字典

    Examples:
        >>> simplify_expression("(x+1)**2", method="expand")
        {'success': True, 'result': x**2 + 2*x + 1, ...}
    """
    try:
        # 解析表达式
        expr = sympify(expression)

        # 根据方法简化
        if method == "expand":
            result = expand(expr)
        elif method == "factor":
            result = factor(expr)
        else:  # simplify
            result = simplify(expr)

        logger.debug(f"表达式简化成功: {method}")

        return {
            'success': True,
            'result': result,
            'result_str': str(result),
            'result_latex': latex(result),
            'original': expression,
            'method': method
        }

    except Exception as e:
        logger.error(f"表达式简化失败: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'original': expression,
            'method': method
        }
