"""
文本处理工具
提供文本分词、去重、相似度计算、关键词提取等功能
"""

import re
import jieba
from typing import List, Set, Dict, Tuple, Optional
from collections import Counter
from difflib import SequenceMatcher

from app.core.logging import get_logger

logger = get_logger(__name__)


def tokenize_text(
    text: str,
    mode: str = "default",
    remove_stopwords: bool = False
) -> List[str]:
    """
    文本分词

    Args:
        text: 输入文本
        mode: 分词模式 ('default', 'search', 'all')
            - default: 精确模式
            - search: 搜索引擎模式
            - all: 全模式
        remove_stopwords: 是否移除停用词

    Returns:
        分词结果列表

    Examples:
        >>> tokenize_text("我爱自然语言处理")
        ['我', '爱', '自然语言', '处理']
    """
    if not text or not text.strip():
        return []

    try:
        # 根据模式选择分词方法
        if mode == "search":
            tokens = list(jieba.cut_for_search(text))
        elif mode == "all":
            tokens = list(jieba.cut(text, cut_all=True))
        else:  # default
            tokens = list(jieba.cut(text, cut_all=False))

        # 移除空白符
        tokens = [t.strip() for t in tokens if t.strip()]

        # 移除停用词（如果需要）
        if remove_stopwords:
            tokens = _remove_stopwords(tokens)

        logger.debug(f"文本分词完成: {len(tokens)} 个词")
        return tokens

    except Exception as e:
        logger.error(f"文本分词失败: {str(e)}")
        # 降级为简单空格分割
        return text.split()


def deduplicate_text(
    text: str,
    level: str = "sentence",
    keep_order: bool = True
) -> str:
    """
    文本去重

    Args:
        text: 输入文本
        level: 去重级别 ('char', 'word', 'sentence', 'paragraph')
        keep_order: 是否保持原始顺序

    Returns:
        去重后的文本

    Examples:
        >>> deduplicate_text("你好你好世界", level="word")
        '你好世界'
    """
    if not text or not text.strip():
        return text

    try:
        if level == "char":
            # 字符级去重
            if keep_order:
                seen: Set[str] = set()
                result = []
                for char in text:
                    if char not in seen:
                        seen.add(char)
                        result.append(char)
                return "".join(result)
            else:
                return "".join(set(text))

        elif level == "word":
            # 词级去重
            words = tokenize_text(text)
            if keep_order:
                seen_words: Set[str] = set()
                result_words = []
                for word in words:
                    if word not in seen_words:
                        seen_words.add(word)
                        result_words.append(word)
                return "".join(result_words)
            else:
                return "".join(set(words))

        elif level == "sentence":
            # 句子级去重
            sentences = _split_sentences(text)
            if keep_order:
                seen_sentences: Set[str] = set()
                result_sentences = []
                for sentence in sentences:
                    if sentence not in seen_sentences:
                        seen_sentences.add(sentence)
                        result_sentences.append(sentence)
                return "".join(result_sentences)
            else:
                return "".join(set(sentences))

        elif level == "paragraph":
            # 段落级去重
            paragraphs = text.split("\n\n")
            if keep_order:
                seen_paragraphs: Set[str] = set()
                result_paragraphs = []
                for para in paragraphs:
                    if para.strip() and para not in seen_paragraphs:
                        seen_paragraphs.add(para)
                        result_paragraphs.append(para)
                return "\n\n".join(result_paragraphs)
            else:
                unique_paras = [p for p in set(paragraphs) if p.strip()]
                return "\n\n".join(unique_paras)

        else:
            logger.warning(f"未知的去重级别: {level}，返回原文本")
            return text

    except Exception as e:
        logger.error(f"文本去重失败: {str(e)}")
        return text


def calculate_similarity(
    text1: str,
    text2: str,
    method: str = "sequence",
    tokenize: bool = True
) -> float:
    """
    计算文本相似度

    Args:
        text1: 第一个文本
        text2: 第二个文本
        method: 相似度计算方法
            - sequence: 序列匹配（基于difflib）
            - jaccard: Jaccard相似度
            - cosine: 余弦相似度
        tokenize: 是否先分词

    Returns:
        相似度分数 (0.0 - 1.0)

    Examples:
        >>> calculate_similarity("我爱编程", "我喜欢编程")
        0.75
    """
    if not text1 or not text2:
        return 0.0

    try:
        if method == "sequence":
            # 序列匹配相似度
            return SequenceMatcher(None, text1, text2).ratio()

        elif method == "jaccard":
            # Jaccard相似度
            if tokenize:
                tokens1 = set(tokenize_text(text1))
                tokens2 = set(tokenize_text(text2))
            else:
                tokens1 = set(text1)
                tokens2 = set(text2)

            if not tokens1 and not tokens2:
                return 1.0

            intersection = len(tokens1 & tokens2)
            union = len(tokens1 | tokens2)

            return intersection / union if union > 0 else 0.0

        elif method == "cosine":
            # 余弦相似度
            if tokenize:
                tokens1 = tokenize_text(text1)
                tokens2 = tokenize_text(text2)
            else:
                tokens1 = list(text1)
                tokens2 = list(text2)

            # 构建词频向量
            counter1 = Counter(tokens1)
            counter2 = Counter(tokens2)

            # 计算余弦相似度
            all_tokens = set(counter1.keys()) | set(counter2.keys())

            dot_product = sum(counter1[token] * counter2[token] for token in all_tokens)
            magnitude1 = sum(count ** 2 for count in counter1.values()) ** 0.5
            magnitude2 = sum(count ** 2 for count in counter2.values()) ** 0.5

            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0

            return dot_product / (magnitude1 * magnitude2)

        else:
            logger.warning(f"未知的相似度计算方法: {method}，使用默认方法")
            return SequenceMatcher(None, text1, text2).ratio()

    except Exception as e:
        logger.error(f"计算文本相似度失败: {str(e)}")
        return 0.0


def extract_keywords(
    text: str,
    top_k: int = 10,
    method: str = "tfidf",
    with_weights: bool = False
) -> List[str] | List[Tuple[str, float]]:
    """
    提取关键词

    Args:
        text: 输入文本
        top_k: 返回前K个关键词
        method: 提取方法
            - tfidf: TF-IDF算法
            - textrank: TextRank算法
            - frequency: 词频统计
        with_weights: 是否返回权重

    Returns:
        关键词列表，如果with_weights=True则返回(词, 权重)元组列表

    Examples:
        >>> extract_keywords("人工智能是未来的发展方向", top_k=3)
        ['人工智能', '未来', '发展']
    """
    if not text or not text.strip():
        return []

    try:
        if method == "tfidf":
            # 使用jieba的TF-IDF
            import jieba.analyse
            keywords = jieba.analyse.extract_tags(
                text,
                topK=top_k,
                withWeight=with_weights
            )

        elif method == "textrank":
            # 使用jieba的TextRank
            import jieba.analyse
            keywords = jieba.analyse.textrank(
                text,
                topK=top_k,
                withWeight=with_weights
            )

        elif method == "frequency":
            # 简单词频统计
            tokens = tokenize_text(text, remove_stopwords=True)
            counter = Counter(tokens)

            if with_weights:
                total = sum(counter.values())
                keywords = [
                    (word, count / total)
                    for word, count in counter.most_common(top_k)
                ]
            else:
                keywords = [word for word, _ in counter.most_common(top_k)]

        else:
            logger.warning(f"未知的关键词提取方法: {method}，使用默认方法")
            import jieba.analyse
            keywords = jieba.analyse.extract_tags(
                text,
                topK=top_k,
                withWeight=with_weights
            )

        logger.debug(f"关键词提取完成: {len(keywords)} 个关键词")
        return keywords

    except Exception as e:
        logger.error(f"关键词提取失败: {str(e)}")
        return []


# ============================================
# 辅助函数
# ============================================

def _split_sentences(text: str) -> List[str]:
    """
    分割句子

    Args:
        text: 输入文本

    Returns:
        句子列表
    """
    # 中英文句子分割符
    sentence_delimiters = r'[。！？!?;；\n]+'
    sentences = re.split(sentence_delimiters, text)

    # 过滤空句子
    return [s.strip() for s in sentences if s.strip()]


def _remove_stopwords(tokens: List[str]) -> List[str]:
    """
    移除停用词

    Args:
        tokens: 词列表

    Returns:
        移除停用词后的词列表
    """
    # 常见中文停用词
    stopwords = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
        '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
        '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '个',
        '们', '他', '她', '它', '我们', '你们', '他们', '她们', '它们'
    }

    return [token for token in tokens if token not in stopwords]


def calculate_text_stats(text: str) -> Dict[str, int]:
    """
    计算文本统计信息

    Args:
        text: 输入文本

    Returns:
        统计信息字典

    Examples:
        >>> calculate_text_stats("你好世界")
        {'char_count': 4, 'word_count': 2, 'sentence_count': 1}
    """
    if not text:
        return {
            'char_count': 0,
            'word_count': 0,
            'sentence_count': 0,
            'paragraph_count': 0
        }

    try:
        # 字符数（不含空白）
        char_count = len(text.replace(' ', '').replace('\n', '').replace('\t', ''))

        # 词数
        words = tokenize_text(text)
        word_count = len(words)

        # 句子数
        sentences = _split_sentences(text)
        sentence_count = len(sentences)

        # 段落数
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)

        return {
            'char_count': char_count,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count
        }

    except Exception as e:
        logger.error(f"计算文本统计信息失败: {str(e)}")
        return {
            'char_count': len(text),
            'word_count': 0,
            'sentence_count': 0,
            'paragraph_count': 0
        }
