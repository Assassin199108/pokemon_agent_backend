# -*- coding: utf-8 -*-
"""
网页内容抓取子工具
从URL加载内容，清洗并提取结构化宝可梦信息
"""

import json
import logging
from typing import List, Dict, Any

from langchain_core.tools import tool

from ...services.web.cache import WebCache
from ...services.web.processing import WebLoader, HTMLCleaner, TextProcessor
from ...services.web.extraction import LLMChainManager, PokemonExtractor

logger = logging.getLogger(__name__)


# 初始化模块组件
web_cache = WebCache(max_size=100, expire_days=1)
web_loader = WebLoader(default_timeout=25)
html_cleaner = HTMLCleaner()
text_processor = TextProcessor(chunk_size=1500, chunk_overlap=150)
llm_chain_manager = LLMChainManager(
    model_name="x-ai/grok-4-fast:free",
    base_url="https://openrouter.ai/api/v1",
    temperature=0.0,
    timeout=30
)
pokemon_extractor = PokemonExtractor()


@tool
def web_content_scraper(url: str) -> str:
    """
    从URL加载内容，清洗并使用Map-Reduce过程提取结构化宝可梦信息。
    针对宝可梦数据提取优化，具有超时保护和缓存功能。
    返回包含提取信息或错误详情的JSON字符串。
    """
    logger.info(f"开始处理URL: {url}")

    # 检查缓存
    cached_result = web_cache.get(url)
    if cached_result is not None:
        return cached_result

    try:
        # 1. 加载网页内容
        success, content, error_msg = web_loader.load_and_validate(url, min_length=200)
        if not success:
            # 缓存错误结果
            error_json = json.dumps(content, ensure_ascii=False)
            web_cache.set(url, error_json)
            return error_json

        docs = content

        # 2. 清洗HTML内容
        success, cleaned_text, error_msg = html_cleaner.clean_html(docs[0].page_content)
        if not success:
            error_response = {
                "success": False,
                "error": error_msg,
                "url": url,
                "suggestion": "网页格式异常，请尝试其他网站获取宝可梦信息",
                "error_type": "html_parsing"
            }
            error_json = json.dumps(error_response, ensure_ascii=False)
            web_cache.set(url, error_json)
            return error_json

        # 3. 文本分块处理
        split_docs = text_processor.split_text(cleaned_text)
        if not split_docs:
            error_response = {
                "success": False,
                "error": "文本分块失败",
                "url": url,
                "suggestion": "网页内容处理异常，请尝试其他网站获取宝可梦信息",
                "error_type": "text_processing"
            }
            error_json = json.dumps(error_response, ensure_ascii=False)
            web_cache.set(url, error_json)
            return error_json

        # 4. 提取宝可梦信息
        success, result, error_msg = llm_chain_manager.extract_pokemon_info(split_docs)
        if not success:
            # 缓存LLM错误结果
            error_json = json.dumps(result, ensure_ascii=False)
            web_cache.set(url, error_json)
            return error_json

        llm_response = result

        # 5. 验证和标准化提取结果
        success, final_result, error_msg = pokemon_extractor.extract_and_validate(llm_response, url)

        # 缓存最终结果
        result_json = json.dumps(final_result, ensure_ascii=False)
        web_cache.set(url, result_json)

        if success:
            logger.info(f"宝可梦信息提取成功，URL: {url}")
        else:
            logger.warning(f"宝可梦信息提取失败，URL: {url}，原因: {error_msg}")

        return result_json

    except Exception as e:
        logger.error(f"网页抓取过程中发生未预期错误: {str(e)}")
        error_response = {
            "success": False,
            "error": f"网页抓取失败: {str(e)}",
            "url": url,
            "suggestion": "网页处理过程中发生异常，请尝试其他网站获取宝可梦信息",
            "error_type": "unexpected"
        }
        error_json = json.dumps(error_response, ensure_ascii=False)
        web_cache.set(url, error_json)
        return error_json


# 缓存管理工具函数
def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    return web_cache.get_stats()

def clear_cache() -> None:
    """清空缓存"""
    web_cache.clear()

def is_url_cached(url: str) -> bool:
    """检查URL是否已缓存"""
    return web_cache.is_cached(url)