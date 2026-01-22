# -*- coding: utf-8 -*-
"""
网络搜索子工具
使用Tavily API进行网络搜索
"""

import json
import logging
from typing import List, Dict, Any

from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def web_search(query: str) -> List[Dict[str, str]]:
    """
    使用Tavily执行网络搜索，为给定查询找到相关URL。
    当本地服务器失败时使用此工具查找百科页面。
    返回包含url、title和content的字典列表。
    """
    logger.info(f"执行网络搜索，查询: '{query}'")
    try:
        wrapper = TavilySearchAPIWrapper()
        results = wrapper.results(query, max_results=3, include_raw_content=False)
        return [{"url": res["url"], "title": res["title"], "content": res["content"]} for res in results]
    except Exception as e:
        logger.error(f"网络搜索失败: {str(e)}")
        return [{"error": f"搜索失败: {str(e)}"}]