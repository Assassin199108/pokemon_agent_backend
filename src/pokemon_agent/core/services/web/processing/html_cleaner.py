# -*- coding: utf-8 -*-
"""
HTML清洗器类
提供HTML标签清洗、内容提取和噪声过滤功能
"""

import logging
from typing import List
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class HTMLCleaner:
    """
    HTML内容清洗器

    功能：
    - HTML标签清洗
    - 噪声元素过滤
    - 内容提取
    - 文本清理
    """

    def __init__(self):
        """
        初始化HTML清洗器
        """
        # 要移除的HTML标签
        self.remove_tags = [
            'script', 'style', 'nav', 'footer', 'header',
            'aside', 'iframe', 'form', 'button', 'input',
            'select', 'textarea', 'noscript', 'meta'
        ]

        # 要移除的CSS类名
        self.remove_classes = [
            'nav', 'menu', 'sidebar', 'advertisement', 'ad',
            'banner', 'popup', 'modal', 'footer', 'header',
            'navigation', 'social', 'share', 'comment'
        ]

        # 要移除的ID前缀
        self.remove_id_prefixes = [
            'nav-', 'menu-', 'sidebar-', 'ad-', 'banner-',
            'footer-', 'header-', 'navigation-', 'social-'
        ]

        logger.info("HTMLCleaner初始化完成")

    def clean_html(self, html_content: str) -> tuple[bool, str, str]:
        """
        清洗HTML内容

        Args:
            html_content: HTML内容字符串

        Returns:
            tuple: (success, cleaned_text, error_message)
        """
        try:
            logger.info("开始HTML清洗处理")

            # 解析HTML
            soup = BeautifulSoup(html_content, "html.parser")

            # 移除不需要的标签
            self._remove_tags(soup)

            # 移除不需要的类和ID
            self._remove_classes_and_ids(soup)

            # 移除注释
            self._remove_comments(soup)

            # 提取文本
            cleaned_text = self._extract_text(soup)

            # 清理文本
            cleaned_text = self._clean_text(cleaned_text)

            logger.info(f"HTML清洗完成，提取文本长度: {len(cleaned_text)}字符")
            return True, cleaned_text, ""

        except Exception as e:
            error_msg = f"HTML解析失败: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg

    def _remove_tags(self, soup: BeautifulSoup):
        """
        移除不需要的HTML标签

        Args:
            soup: BeautifulSoup对象
        """
        removed_count = 0
        for tag_name in self.remove_tags:
            tags = soup.find_all(tag_name)
            for tag in tags:
                tag.decompose()
                removed_count += 1

        if removed_count > 0:
            logger.debug(f"移除了{removed_count}个{', '.join(self.remove_tags)}标签")

    def _remove_classes_and_ids(self, soup: BeautifulSoup):
        """
        移除不需要的类和ID

        Args:
            soup: BeautifulSoup对象
        """
        # 移除指定类的元素
        for class_name in self.remove_classes:
            elements = soup.find_all(class_=class_name)
            for element in elements:
                element.decompose()

        # 移除指定ID前缀的元素
        for prefix in self.remove_id_prefixes:
            elements = soup.find_all(id=lambda x: x and x.startswith(prefix))
            for element in elements:
                element.decompose()

    def _remove_comments(self, soup: BeautifulSoup):
        """
        移除HTML注释

        Args:
            soup: BeautifulSoup对象
        """
        from bs4 import Comment
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            comment.extract()

    def _extract_text(self, soup: BeautifulSoup) -> str:
        """
        提取文本内容

        Args:
            soup: BeautifulSoup对象

        Returns:
            提取的文本内容
        """
        # 获取文本，使用换行符分隔
        text = soup.get_text(separator='\n', strip=True)
        return text

    def _clean_text(self, text: str) -> str:
        """
        清理文本内容

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        # 移除多余的空白字符
        import re

        # 替换多个换行为单个换行
        text = re.sub(r'\n\s*\n', '\n', text)

        # 替换多个空格为单个空格
        text = re.sub(r'\s+', ' ', text)

        # 移除行首行尾的空白
        text = text.strip()

        return text

    def extract_links(self, html_content: str) -> List[dict]:
        """
        提取页面中的链接

        Args:
            html_content: HTML内容

        Returns:
            链接列表，每个链接包含href和text
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            links = []

            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                if href and text:
                    links.append({
                        'href': href,
                        'text': text
                    })

            logger.info(f"提取了{len(links)}个链接")
            return links

        except Exception as e:
            logger.error(f"提取链接失败: {e}")
            return []

    def extract_images(self, html_content: str) -> List[dict]:
        """
        提取页面中的图片

        Args:
            html_content: HTML内容

        Returns:
            图片列表，每个图片包含src和alt
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            images = []

            for img in soup.find_all('img', src=True):
                src = img['src']
                alt = img.get('alt', '')
                if src:
                    images.append({
                        'src': src,
                        'alt': alt
                    })

            logger.info(f"提取了{len(images)}个图片")
            return images

        except Exception as e:
            logger.error(f"提取图片失败: {e}")
            return []

    def get_page_structure(self, html_content: str) -> dict:
        """
        获取页面结构信息

        Args:
            html_content: HTML内容

        Returns:
            页面结构信息
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # 统计标签数量
            tag_counts = {}
            for tag in soup.find_all(True):
                tag_name = tag.name
                tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1

            # 获取标题
            title = soup.title.string if soup.title else ""

            # 获取主要标题
            headings = []
            for i in range(1, 7):
                h_tags = soup.find_all(f'h{i}')
                for h in h_tags:
                    headings.append({
                        'level': i,
                        'text': h.get_text(strip=True)
                    })

            structure = {
                'title': title,
                'tag_counts': tag_counts,
                'headings': headings,
                'total_tags': sum(tag_counts.values()),
                'has_tables': len(soup.find_all('table')) > 0,
                'has_lists': len(soup.find_all(['ul', 'ol'])) > 0,
                'has_forms': len(soup.find_all('form')) > 0
            }

            return structure

        except Exception as e:
            logger.error(f"获取页面结构失败: {e}")
            return {}

    def validate_html_quality(self, html_content: str) -> dict:
        """
        验证HTML质量

        Args:
            html_content: HTML内容

        Returns:
            质量评估结果
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # 基本质量指标
            quality_metrics = {
                'has_title': bool(soup.title and soup.title.string),
                'has_headings': len(soup.find_all(['h1', 'h2', 'h3'])) > 0,
                'has_paragraphs': len(soup.find_all('p')) > 0,
                'content_length': len(soup.get_text(strip=True)),
                'structure_score': 0,
                'recommendations': []
            }

            # 计算结构分数
            score = 0
            if quality_metrics['has_title']:
                score += 20
            if quality_metrics['has_headings']:
                score += 30
            if quality_metrics['has_paragraphs']:
                score += 20
            if quality_metrics['content_length'] > 500:
                score += 30

            quality_metrics['structure_score'] = score

            # 生成建议
            if not quality_metrics['has_title']:
                quality_metrics['recommendations'].append("建议添加页面标题")
            if not quality_metrics['has_headings']:
                quality_metrics['recommendations'].append("建议添加标题结构")
            if not quality_metrics['has_paragraphs']:
                quality_metrics['recommendations'].append("建议使用段落标签")
            if quality_metrics['content_length'] < 500:
                quality_metrics['recommendations'].append("内容较少，可能影响信息提取效果")

            return quality_metrics

        except Exception as e:
            logger.error(f"HTML质量验证失败: {e}")
            return {
                'has_title': False,
                'has_headings': False,
                'has_paragraphs': False,
                'content_length': 0,
                'structure_score': 0,
                'recommendations': ['HTML解析失败，无法评估质量']
            }