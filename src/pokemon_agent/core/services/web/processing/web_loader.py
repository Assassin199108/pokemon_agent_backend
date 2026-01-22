# -*- coding: utf-8 -*-
"""
网页加载器类
提供网页内容加载、超时控制和错误处理功能
"""

import json
import logging
from typing import List, Dict, Any, Optional
from langchain_community.document_loaders import WebBaseLoader
from ....tools.time_out_tool import TimeoutTool, create_timeout_error_response

logger = logging.getLogger(__name__)


class WebLoader:
    """
    网页内容加载器

    功能：
    - 网页内容加载
    - 超时控制
    - 错误处理
    - 响应验证
    """

    def __init__(self, default_timeout: int = 25):
        """
        初始化网页加载器

        Args:
            default_timeout: 默认超时时间（秒）
        """
        self.default_timeout = default_timeout
        self.timeout_tool = TimeoutTool(default_timeout=default_timeout)
        logger.info(f"WebLoader初始化完成，默认超时: {default_timeout}秒")

    def load_content(self, url: str, timeout: Optional[int] = None) -> tuple[bool, Any, str]:
        """
        加载网页内容

        Args:
            url: 目标URL
            timeout: 超时时间，不指定则使用默认值

        Returns:
            tuple: (success, content, error_message)
            - success: 是否成功
            - content: 成功时为文档列表，失败时为错误响应字典
            - error_message: 错误信息，成功时为空
        """
        actual_timeout = timeout or self.default_timeout
        logger.info(f"开始加载网页内容: {url}, 超时时间: {actual_timeout}秒")

        def load_web_content():
            loader = WebBaseLoader(url)
            return loader.load()

        try:
            # 使用超时工具加载内容
            docs = self.timeout_tool.run_with_timeout(load_web_content, timeout=actual_timeout)

            # 验证内容
            if not docs or not docs[0].page_content:
                error_response = {
                    "success": False,
                    "error": "无法从URL加载内容",
                    "url": url,
                    "suggestion": "网站内容为空，请尝试其他网站获取宝可梦信息",
                    "error_type": "empty_content"
                }
                return False, error_response, "网页内容为空"

            logger.info(f"网页内容加载成功，内容长度: {len(docs[0].page_content)}字符")
            return True, docs, ""

        except Exception as load_error:
            error_msg = str(load_error)
            logger.error(f"网页内容加载失败: {error_msg}")

            # 根据错误类型生成相应的错误响应
            if "timeout" in error_msg.lower() or "time out" in error_msg.lower():
                timeout_response = create_timeout_error_response(
                    "网页内容加载",
                    actual_timeout,
                    "网站响应时间过长，请尝试其他网站获取宝可梦信息"
                )
                return False, timeout_response, f"加载超时: {error_msg}"

            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                network_error_response = {
                    "success": False,
                    "error": f"网络连接异常: {error_msg}",
                    "url": url,
                    "suggestion": "网络连接失败，请尝试其他网站获取宝可梦信息",
                    "error_type": "network"
                }
                return False, network_error_response, f"网络错误: {error_msg}"

            else:
                loading_error_response = {
                    "success": False,
                    "error": f"加载网页失败: {error_msg}",
                    "url": url,
                    "suggestion": "网站访问异常，请尝试其他网站获取宝可梦信息",
                    "error_type": "loading"
                }
                return False, loading_error_response, f"加载失败: {error_msg}"

    def get_content_info(self, docs) -> Dict[str, Any]:
        """
        获取内容信息

        Args:
            docs: 文档列表

        Returns:
            内容信息字典
        """
        if not docs or not docs[0].page_content:
            return {
                "has_content": False,
                "content_length": 0,
                "source": None,
                "metadata": {}
            }

        doc = docs[0]
        return {
            "has_content": True,
            "content_length": len(doc.page_content),
            "source": doc.metadata.get('source', ''),
            "metadata": doc.metadata
        }

    def validate_content(self, content: str, min_length: int = 200) -> tuple[bool, str]:
        """
        验证内容是否有效

        Args:
            content: 内容文本
            min_length: 最小长度要求

        Returns:
            tuple: (is_valid, error_message)
        """
        if not content:
            return False, "内容为空"

        if len(content) < min_length:
            return False, f"内容长度不足，最少需要{min_length}字符，当前只有{len(content)}字符"

        return True, ""

    def load_and_validate(self, url: str, min_length: int = 200, timeout: Optional[int] = None) -> tuple[bool, Any, str]:
        """
        加载并验证网页内容

        Args:
            url: 目标URL
            min_length: 最小长度要求
            timeout: 超时时间

        Returns:
            tuple: (success, content, error_message)
        """
        # 加载内容
        success, content, error_msg = self.load_content(url, timeout)

        if not success:
            return False, content, error_msg

        # 验证内容
        is_valid, validation_error = self.validate_content(content[0].page_content, min_length)
        if not is_valid:
            error_response = {
                "success": False,
                "error": validation_error,
                "url": url,
                "suggestion": "网站内容不充分，请尝试其他网站获取宝可梦信息",
                "error_type": "insufficient_content"
            }
            return False, error_response, validation_error

        return True, content, ""