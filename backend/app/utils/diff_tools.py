"""
文本差分工具
提供文本差分算法、版本对比、变更高亮等功能
基于Myers差分算法
"""

from typing import List, Dict, Any, Tuple, Optional
from difflib import SequenceMatcher, unified_diff, ndiff
from enum import Enum

from app.core.logging import get_logger

logger = get_logger(__name__)


class ChangeType(str, Enum):
    """变更类型"""
    ADD = "add"
    DELETE = "delete"
    MODIFY = "modify"
    EQUAL = "equal"


class DiffResult:
    """差分结果"""

    def __init__(
        self,
        changes: List[Dict[str, Any]],
        old_text: str,
        new_text: str,
        similarity: float
    ):
        self.changes = changes
        self.old_text = old_text
        self.new_text = new_text
        self.similarity = similarity

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'changes': self.changes,
            'old_text': self.old_text,
            'new_text': self.new_text,
            'similarity': self.similarity,
            'stats': self.get_stats()
        }

    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        stats = {
            'additions': 0,
            'deletions': 0,
            'modifications': 0,
            'unchanged': 0
        }

        for change in self.changes:
            change_type = change['type']
            if change_type == ChangeType.ADD:
                stats['additions'] += 1
            elif change_type == ChangeType.DELETE:
                stats['deletions'] += 1
            elif change_type == ChangeType.MODIFY:
                stats['modifications'] += 1
            elif change_type == ChangeType.EQUAL:
                stats['unchanged'] += 1

        return stats


def compute_diff(
    old_text: str,
    new_text: str,
    granularity: str = "line",
    context_lines: int = 3
) -> DiffResult:
    """
    计算文本差分（Myers算法）

    Args:
        old_text: 旧文本
        new_text: 新文本
        granularity: 粒度级别
            - char: 字符级
            - word: 词级
            - line: 行级
        context_lines: 上下文行数

    Returns:
        差分结果对象

    Examples:
        >>> result = compute_diff("hello world", "hello python")
        >>> result.get_stats()
        {'additions': 1, 'deletions': 1, 'modifications': 0, 'unchanged': 1}
    """
    try:
        # 根据粒度分割文本
        if granularity == "char":
            old_items = list(old_text)
            new_items = list(new_text)
        elif granularity == "word":
            old_items = old_text.split()
            new_items = new_text.split()
        else:  # line
            old_items = old_text.splitlines(keepends=True)
            new_items = new_text.splitlines(keepends=True)

        # 使用SequenceMatcher计算差异
        matcher = SequenceMatcher(None, old_items, new_items)

        # 计算相似度
        similarity = matcher.ratio()

        # 提取变更
        changes = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # 未变更的部分
                content = _join_items(old_items[i1:i2], granularity)
                changes.append({
                    'type': ChangeType.EQUAL,
                    'content': content,
                    'old_range': (i1, i2),
                    'new_range': (j1, j2)
                })

            elif tag == 'delete':
                # 删除的部分
                content = _join_items(old_items[i1:i2], granularity)
                changes.append({
                    'type': ChangeType.DELETE,
                    'content': content,
                    'old_range': (i1, i2),
                    'new_range': None
                })

            elif tag == 'insert':
                # 新增的部分
                content = _join_items(new_items[j1:j2], granularity)
                changes.append({
                    'type': ChangeType.ADD,
                    'content': content,
                    'old_range': None,
                    'new_range': (j1, j2)
                })

            elif tag == 'replace':
                # 替换的部分（修改）
                old_content = _join_items(old_items[i1:i2], granularity)
                new_content = _join_items(new_items[j1:j2], granularity)
                changes.append({
                    'type': ChangeType.MODIFY,
                    'old_content': old_content,
                    'new_content': new_content,
                    'old_range': (i1, i2),
                    'new_range': (j1, j2)
                })

        logger.debug(
            f"差分计算完成: {len(changes)} 个变更, "
            f"相似度: {similarity:.2%}"
        )

        return DiffResult(
            changes=changes,
            old_text=old_text,
            new_text=new_text,
            similarity=similarity
        )

    except Exception as e:
        logger.error(f"差分计算失败: {str(e)}")
        # 返回空结果
        return DiffResult(
            changes=[],
            old_text=old_text,
            new_text=new_text,
            similarity=0.0
        )


def highlight_changes(
    diff_result: DiffResult,
    format: str = "html",
    show_unchanged: bool = False
) -> str:
    """
    高亮显示变更

    Args:
        diff_result: 差分结果
        format: 输出格式
            - html: HTML格式
            - markdown: Markdown格式
            - ansi: ANSI终端颜色
            - plain: 纯文本
        show_unchanged: 是否显示未变更的部分

    Returns:
        高亮后的文本

    Examples:
        >>> result = compute_diff("old", "new")
        >>> highlight_changes(result, format="html")
        '<del>old</del><ins>new</ins>'
    """
    try:
        output_lines = []

        for change in diff_result.changes:
            change_type = change['type']

            # 跳过未变更的部分（如果不显示）
            if change_type == ChangeType.EQUAL and not show_unchanged:
                continue

            if format == "html":
                output_lines.append(_format_html(change))
            elif format == "markdown":
                output_lines.append(_format_markdown(change))
            elif format == "ansi":
                output_lines.append(_format_ansi(change))
            else:  # plain
                output_lines.append(_format_plain(change))

        return "\n".join(output_lines)

    except Exception as e:
        logger.error(f"高亮显示失败: {str(e)}")
        return diff_result.new_text


def get_change_summary(
    diff_result: DiffResult,
    detailed: bool = False
) -> Dict[str, Any]:
    """
    获取变更摘要

    Args:
        diff_result: 差分结果
        detailed: 是否返回详细信息

    Returns:
        变更摘要字典

    Examples:
        >>> result = compute_diff("old text", "new text")
        >>> get_change_summary(result)
        {'total_changes': 2, 'additions': 1, 'deletions': 1, ...}
    """
    try:
        stats = diff_result.get_stats()

        summary = {
            'total_changes': (
                stats['additions'] +
                stats['deletions'] +
                stats['modifications']
            ),
            'additions': stats['additions'],
            'deletions': stats['deletions'],
            'modifications': stats['modifications'],
            'unchanged': stats['unchanged'],
            'similarity': diff_result.similarity,
            'similarity_percent': f"{diff_result.similarity:.1%}"
        }

        if detailed:
            # 添加详细的变更列表
            summary['changes'] = []
            for change in diff_result.changes:
                if change['type'] != ChangeType.EQUAL:
                    change_info = {
                        'type': change['type'],
                        'old_range': change.get('old_range'),
                        'new_range': change.get('new_range')
                    }

                    if change['type'] == ChangeType.MODIFY:
                        change_info['old_content'] = change.get('old_content', '')[:50]
                        change_info['new_content'] = change.get('new_content', '')[:50]
                    else:
                        change_info['content'] = change.get('content', '')[:50]

                    summary['changes'].append(change_info)

        logger.debug(f"变更摘要生成完成: {summary['total_changes']} 个变更")

        return summary

    except Exception as e:
        logger.error(f"生成变更摘要失败: {str(e)}")
        return {
            'total_changes': 0,
            'error': str(e)
        }


def compute_unified_diff(
    old_text: str,
    new_text: str,
    old_label: str = "old",
    new_label: str = "new",
    context_lines: int = 3
) -> str:
    """
    计算统一差分格式（类似git diff）

    Args:
        old_text: 旧文本
        new_text: 新文本
        old_label: 旧文件标签
        new_label: 新文件标签
        context_lines: 上下文行数

    Returns:
        统一差分格式的字符串

    Examples:
        >>> compute_unified_diff("line1\\nline2", "line1\\nline3")
        '--- old\\n+++ new\\n@@ -1,2 +1,2 @@\\n line1\\n-line2\\n+line3'
    """
    try:
        old_lines = old_text.splitlines(keepends=True)
        new_lines = new_text.splitlines(keepends=True)

        diff_lines = unified_diff(
            old_lines,
            new_lines,
            fromfile=old_label,
            tofile=new_label,
            lineterm='',
            n=context_lines
        )

        return '\n'.join(diff_lines)

    except Exception as e:
        logger.error(f"统一差分计算失败: {str(e)}")
        return ""


def compute_ndiff(
    old_text: str,
    new_text: str
) -> str:
    """
    计算ndiff格式差分（更详细的差异）

    Args:
        old_text: 旧文本
        new_text: 新文本

    Returns:
        ndiff格式的字符串

    Examples:
        >>> compute_ndiff("hello", "hallo")
        '  h\\n- e\\n+ a\\n  l\\n  l\\n  o'
    """
    try:
        old_lines = old_text.splitlines(keepends=True)
        new_lines = new_text.splitlines(keepends=True)

        diff_lines = ndiff(old_lines, new_lines)

        return ''.join(diff_lines)

    except Exception as e:
        logger.error(f"ndiff计算失败: {str(e)}")
        return ""


def merge_changes(
    base_text: str,
    changes_list: List[Dict[str, Any]]
) -> str:
    """
    合并多个变更

    Args:
        base_text: 基础文本
        changes_list: 变更列表

    Returns:
        合并后的文本
    """
    try:
        result = base_text

        # 按位置排序变更（从后往前应用，避免位置偏移）
        sorted_changes = sorted(
            changes_list,
            key=lambda x: x.get('position', 0),
            reverse=True
        )

        for change in sorted_changes:
            change_type = change['type']
            position = change.get('position', 0)
            length = change.get('length', 0)

            if change_type == ChangeType.ADD:
                content = change.get('content', '')
                result = result[:position] + content + result[position:]

            elif change_type == ChangeType.DELETE:
                result = result[:position] + result[position + length:]

            elif change_type == ChangeType.MODIFY:
                content = change.get('content', '')
                result = result[:position] + content + result[position + length:]

        logger.debug(f"变更合并完成: {len(changes_list)} 个变更")

        return result

    except Exception as e:
        logger.error(f"变更合并失败: {str(e)}")
        return base_text


# ============================================
# 辅助函数
# ============================================

def _join_items(items: List[str], granularity: str) -> str:
    """
    根据粒度连接项目

    Args:
        items: 项目列表
        granularity: 粒度

    Returns:
        连接后的字符串
    """
    if granularity == "char":
        return "".join(items)
    elif granularity == "word":
        return " ".join(items)
    else:  # line
        return "".join(items)


def _format_html(change: Dict[str, Any]) -> str:
    """HTML格式化"""
    change_type = change['type']

    if change_type == ChangeType.ADD:
        return f'<ins>{change["content"]}</ins>'
    elif change_type == ChangeType.DELETE:
        return f'<del>{change["content"]}</del>'
    elif change_type == ChangeType.MODIFY:
        return (
            f'<del>{change["old_content"]}</del>'
            f'<ins>{change["new_content"]}</ins>'
        )
    else:  # EQUAL
        return change["content"]


def _format_markdown(change: Dict[str, Any]) -> str:
    """Markdown格式化"""
    change_type = change['type']

    if change_type == ChangeType.ADD:
        return f'**+ {change["content"]}**'
    elif change_type == ChangeType.DELETE:
        return f'~~- {change["content"]}~~'
    elif change_type == ChangeType.MODIFY:
        return (
            f'~~- {change["old_content"]}~~\n'
            f'**+ {change["new_content"]}**'
        )
    else:  # EQUAL
        return change["content"]


def _format_ansi(change: Dict[str, Any]) -> str:
    """ANSI终端颜色格式化"""
    change_type = change['type']

    # ANSI颜色代码
    RED = '\033[91m'
    GREEN = '\033[92m'
    RESET = '\033[0m'

    if change_type == ChangeType.ADD:
        return f'{GREEN}+ {change["content"]}{RESET}'
    elif change_type == ChangeType.DELETE:
        return f'{RED}- {change["content"]}{RESET}'
    elif change_type == ChangeType.MODIFY:
        return (
            f'{RED}- {change["old_content"]}{RESET}\n'
            f'{GREEN}+ {change["new_content"]}{RESET}'
        )
    else:  # EQUAL
        return f'  {change["content"]}'


def _format_plain(change: Dict[str, Any]) -> str:
    """纯文本格式化"""
    change_type = change['type']

    if change_type == ChangeType.ADD:
        return f'+ {change["content"]}'
    elif change_type == ChangeType.DELETE:
        return f'- {change["content"]}'
    elif change_type == ChangeType.MODIFY:
        return (
            f'- {change["old_content"]}\n'
            f'+ {change["new_content"]}'
        )
    else:  # EQUAL
        return f'  {change["content"]}'


def compare_versions(
    versions: List[Tuple[str, str]],
    labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    比较多个版本

    Args:
        versions: 版本列表 [(version_id, content), ...]
        labels: 版本标签列表

    Returns:
        版本比较结果

    Examples:
        >>> compare_versions([("v1", "text1"), ("v2", "text2")])
        {'comparisons': [...], 'timeline': [...]}
    """
    try:
        if len(versions) < 2:
            return {'error': '至少需要2个版本进行比较'}

        comparisons = []
        timeline = []

        # 两两比较相邻版本
        for i in range(len(versions) - 1):
            old_id, old_content = versions[i]
            new_id, new_content = versions[i + 1]

            # 计算差分
            diff_result = compute_diff(old_content, new_content)

            # 获取摘要
            summary = get_change_summary(diff_result)

            comparison = {
                'from_version': old_id,
                'to_version': new_id,
                'from_label': labels[i] if labels and i < len(labels) else old_id,
                'to_label': labels[i + 1] if labels and i + 1 < len(labels) else new_id,
                'summary': summary,
                'diff': diff_result.to_dict()
            }

            comparisons.append(comparison)

            # 添加到时间线
            timeline.append({
                'version': new_id,
                'label': labels[i + 1] if labels and i + 1 < len(labels) else new_id,
                'changes': summary['total_changes']
            })

        logger.debug(f"版本比较完成: {len(versions)} 个版本")

        return {
            'total_versions': len(versions),
            'comparisons': comparisons,
            'timeline': timeline
        }

    except Exception as e:
        logger.error(f"版本比较失败: {str(e)}")
        return {'error': str(e)}
