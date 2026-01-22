# -*- coding: utf-8 -*-
"""
文本处理器类
提供文本分块、内容验证和格式化功能
"""

import logging
import re
from typing import List, Dict, Any, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class TextProcessor:
    """
    文本处理器

    功能：
    - 文本分块
    - 内容验证
    - 文本清理
    - 格式化
    """

    def __init__(self, chunk_size: int = 1500, chunk_overlap: int = 150):
        """
        初始化文本处理器

        Args:
            chunk_size: 块大小
            chunk_overlap: 块重叠大小
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 中文友好的分隔符
        self.separators = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]

        # 初始化文本分块器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=self.separators
        )

        logger.info(f"TextProcessor初始化完成，块大小: {chunk_size}, 重叠: {chunk_overlap}")

    def split_text(self, text: str) -> List[Document]:
        """
        分割文本为块

        Args:
            text: 要分割的文本

        Returns:
            文档块列表
        """
        try:
            logger.info(f"开始文本分块，原始长度: {len(text)}字符")

            # 预处理文本
            cleaned_text = self._preprocess_text(text)

            # 分割文本
            docs = self.text_splitter.create_documents([cleaned_text])

            logger.info(f"文本分块完成，生成{len(docs)}个块")
            return docs

        except Exception as e:
            logger.error(f"文本分块失败: {e}")
            return []

    def _preprocess_text(self, text: str) -> str:
        """
        预处理文本

        Args:
            text: 原始文本

        Returns:
            预处理后的文本
        """
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)

        # 确保中文标点符号后有空格
        text = re.sub(r'([。！？])', r'\1\n', text)

        # 移除行首行尾的空白
        text = text.strip()

        return text

    def validate_content(self, text: str) -> Tuple[bool, str]:
        """
        验证文本内容质量

        Args:
            text: 要验证的文本

        Returns:
            tuple: (is_valid, error_message)
        """
        if not text:
            return False, "文本内容为空"

        if len(text) < 100:
            return False, f"文本内容过短（{len(text)}字符），可能无法提取有效信息"

        if len(text) > 1000000:  # 1MB限制
            return False, f"文本内容过长（{len(text)}字符），超出处理限制"

        # 检查是否包含有效内容
        if not self._contains_meaningful_content(text):
            return False, "文本内容缺乏有效信息"

        return True, ""

    def _contains_meaningful_content(self, text: str) -> bool:
        """
        检查文本是否包含有意义的内容

        Args:
            text: 要检查的文本

        Returns:
            是否包含有意义的内容
        """
        # 移除空白字符后检查长度
        meaningful_chars = len(text.strip())
        if meaningful_chars < 50:
            return False

        # 检查是否包含中文或英文单词
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]{3,}', text))

        # 如果既有中文又有英文，或者其中一种足够多
        if chinese_chars > 10 or english_words > 5:
            return True

        # 检查数字和标点符号的比例
        total_chars = len(text)
        if total_chars == 0:
            return False

        non_content_chars = len(re.findall(r'[0-9\s\-\_\+\=\*\#\@\$\%\^\&\*\(\)\[\]\{\}\<\>\|\\\/\:\;\"\'\,\.\?\!]', text))
        content_ratio = (total_chars - non_content_chars) / total_chars

        return content_ratio > 0.3

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        分析文本特征

        Args:
            text: 要分析的文本

        Returns:
            文本分析结果
        """
        analysis = {
            'total_length': len(text),
            'char_count': len(text),
            'char_count_no_spaces': len(text.replace(' ', '')),
            'line_count': len(text.split('\n')),
            'word_count': len(text.split()),
            'chinese_char_count': len(re.findall(r'[\u4e00-\u9fff]', text)),
            'english_word_count': len(re.findall(r'[a-zA-Z]{3,}', text)),
            'digit_count': len(re.findall(r'[0-9]', text)),
            'sentence_count': len(re.findall(r'[。！？.!?]', text)),
            'paragraph_count': len([p for p in text.split('\n\n') if p.strip()]),
            'readability_score': 0
        }

        # 计算可读性分数（简化版）
        total_words = analysis['word_count']
        total_sentences = analysis['sentence_count']

        if total_sentences > 0 and total_words > 0:
            avg_words_per_sentence = total_words / total_sentences
            analysis['readability_score'] = max(0, min(100, 100 - avg_words_per_sentence))

        return analysis

    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """
        提取文本关键词

        Args:
            text: 要分析的文本
            max_keywords: 最大关键词数量

        Returns:
            关键词列表
        """
        try:
            # 简单的关键词提取，基于词频
            words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]{3,}', text.lower())

            # 过滤停用词
            stop_words = {
                '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这',
                'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these', 'those'
            }

            word_freq = {}
            for word in words:
                if word not in stop_words and len(word) > 1:
                    word_freq[word] = word_freq.get(word, 0) + 1

            # 按频率排序并返回前N个
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            keywords = [word for word, freq in sorted_words[:max_keywords]]

            logger.info(f"提取了{len(keywords)}个关键词")
            return keywords

        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            return []

    def format_text_summary(self, analysis: Dict[str, Any]) -> str:
        """
        格式化文本分析摘要

        Args:
            analysis: 文本分析结果

        Returns:
            格式化的摘要
        """
        summary = f"""
=== 文本分析摘要 ===
总长度: {analysis['total_length']} 字符
字符数: {analysis['char_count']} (不含空格: {analysis['char_count_no_spaces']})
行数: {analysis['line_count']}
词数: {analysis['word_count']}
段落数: {analysis['paragraph_count']}
句子数: {analysis['sentence_count']}

语言统计:
- 中文字符: {analysis['chinese_char_count']}
- 英文单词: {analysis['english_word_count']}
- 数字: {analysis['digit_count']}

可读性分数: {analysis['readability_score']:.1f}/100
==================
"""
        return summary.strip()

    def optimize_chunk_params(self, text: str) -> Dict[str, int]:
        """
        根据文本长度优化分块参数

        Args:
            text: 要处理的文本

        Returns:
            优化的分块参数
        """
        text_length = len(text)

        if text_length < 1000:
            return {
                'chunk_size': 500,
                'chunk_overlap': 50
            }
        elif text_length < 5000:
            return {
                'chunk_size': 1000,
                'chunk_overlap': 100
            }
        elif text_length < 20000:
            return {
                'chunk_size': 1500,
                'chunk_overlap': 150
            }
        else:
            return {
                'chunk_size': 2000,
                'chunk_overlap': 200
            }

    def get_chunk_info(self, docs: List[Document]) -> Dict[str, Any]:
        """
        获取分块信息

        Args:
            docs: 文档块列表

        Returns:
            分块信息
        """
        if not docs:
            return {
                'total_chunks': 0,
                'total_length': 0,
                'avg_chunk_length': 0,
                'min_chunk_length': 0,
                'max_chunk_length': 0
            }

        chunk_lengths = [len(doc.page_content) for doc in docs]

        return {
            'total_chunks': len(docs),
            'total_length': sum(chunk_lengths),
            'avg_chunk_length': sum(chunk_lengths) / len(chunk_lengths),
            'min_chunk_length': min(chunk_lengths),
            'max_chunk_length': max(chunk_lengths)
        }