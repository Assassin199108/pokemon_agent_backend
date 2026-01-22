# -*- coding: utf-8 -*-
"""
LLM处理链管理类
提供Map-Reduce链管理、提示词模板和LLM调用封装功能
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
try:
    from langchain.chains.summarize import load_summarize_chain
except ImportError:
    try:
        from langchain_core.chains import load_summarize_chain
    except ImportError:
        # 在新版本中可能需要直接使用
        load_summarize_chain = None
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from ....tools.time_out_tool import TimeoutTool, create_timeout_error_response

logger = logging.getLogger(__name__)


class LLMChainManager:
    """
    LLM处理链管理器

    功能：
    - Map-Reduce链管理
    - 提示词模板
    - LLM调用封装
    - 超时控制
    """

    def __init__(self,
                 model_name: str = "x-ai/grok-4-fast:free",
                 base_url: str = "https://openrouter.ai/api/v1",
                 temperature: float = 0.0,
                 timeout: int = 30):
        """
        初始化LLM链管理器

        Args:
            model_name: 模型名称
            base_url: API基础URL
            temperature: 温度参数
            timeout: 超时时间
        """
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.timeout = timeout

        # 初始化LLM
        self.llm = self._create_llm()

        # 初始化超时工具
        self.timeout_tool = TimeoutTool(default_timeout=timeout)

        logger.info(f"LLMChainManager初始化完成，模型: {model_name}")

    def _create_llm(self) -> ChatOpenAI:
        """
        创建LLM实例

        Returns:
            ChatOpenAI实例
        """
        return ChatOpenAI(
            base_url=self.base_url,
            model=self.model_name,
            temperature=self.temperature,
            api_key=os.getenv("ROUTER_API_KEY"),
            timeout=self.timeout
        )

    def create_map_reduce_chain(self,
                              map_prompt_template: str,
                              reduce_prompt_template: str,
                              verbose: bool = False):
        """
        创建Map-Reduce处理链

        Args:
            map_prompt_template: Map阶段提示词模板
            reduce_prompt_template: Reduce阶段提示词模板
            verbose: 是否显示详细日志

        Returns:
            Map-Reduce链
        """
        try:
            # 创建提示词
            map_prompt = PromptTemplate.from_template(map_prompt_template)
            reduce_prompt = PromptTemplate.from_template(reduce_prompt_template)

            # 创建Map-Reduce链
            chain = load_summarize_chain(
                self.llm,
                chain_type="map_reduce",
                map_prompt=map_prompt,
                combine_prompt=reduce_prompt,
                verbose=verbose
            )

            logger.info("Map-Reduce链创建成功")
            return chain

        except Exception as e:
            logger.error(f"Map-Reduce链创建失败: {e}")
            raise

    def run_chain_with_timeout(self,
                             chain,
                             documents: List[Document],
                             timeout: Optional[int] = None):
        """
        运行处理链（带超时控制）

        Args:
            chain: 处理链
            documents: 文档列表
            timeout: 超时时间

        Returns:
            tuple: (success, result, error_message)
        """
        actual_timeout = timeout or self.timeout

        def run_chain():
            return chain.invoke(documents)

        try:
            logger.info(f"开始LLM处理，超时时间: {actual_timeout}秒")
            result = self.timeout_tool.run_with_timeout(run_chain, timeout=actual_timeout)
            logger.info("LLM处理完成")
            return True, result, ""

        except Exception as e:
            error_msg = str(e)
            logger.error(f"LLM处理失败: {error_msg}")

            if "timeout" in error_msg.lower() or "time out" in error_msg.lower():
                timeout_response = create_timeout_error_response(
                    "LLM信息提取",
                    actual_timeout,
                    "大模型处理时间过长，请尝试内容较少的网页或简化查询"
                )
                return False, timeout_response, f"LLM处理超时: {error_msg}"
            else:
                error_response = {
                    "success": False,
                    "error": f"LLM处理失败: {error_msg}",
                    "suggestion": "大模型处理异常，请尝试其他网站获取宝可梦信息",
                    "error_type": "llm_processing"
                }
                return False, error_response, f"LLM处理错误: {error_msg}"

    def get_pokemon_map_prompt(self) -> str:
        """
        获取宝可梦Map阶段提示词

        Returns:
            Map阶段提示词模板
        """
        return """
        你是一个专业的宝可梦信息提取专家。请从以下文本块中提取宝可梦相关属性信息。

        请重点提取以下信息：
        - types: 宝可梦属性（如：电、火、水等）
        - abilities: 特性（包括普通特性和隐藏特性）
        - base_stats: 基础数值（hp, attack, defense, special_attack, special_defense, speed）
        - evolution_chain: 进化链信息
        - basic_info: 基本信息（名称、编号、身高、体重等）
        - game_info: 游戏信息（首次出现世代、版本等）

        如果找到相关信息，请返回JSON对象。如果没有找到宝可梦相关信息，返回空的JSON对象 {{}}。

        文本内容:
        ```{text}```

        JSON输出:
        """

    def get_pokemon_reduce_prompt(self) -> str:
        """
        获取宝可梦Reduce阶段提示词

        Returns:
            Reduce阶段提示词模板
        """
        return """
        你是一个专业的宝可梦信息整合专家。以下是从同一网页提取的多个数据块。
        你的任务是将所有这些信息整合成一个完整、准确的JSON对象。

        请确保最终JSON包含以下字段：
        - types: 属性列表
        - abilities: 特性列表
        - base_stats: 包含六维数值的对象
        - evolution_chain: 进化信息
        - basic_info: 基本信息（如果有的话）
        - game_info: 游戏信息（如果有的话）

        如果某些信息在所有数据块中都缺失，请使用 "N/A" 作为该字段的值。
        请使用英文键名，值可以是中文或英文。

        提取的数据块:
        ```{text}```

        最终整合的JSON输出:
        """

    def create_pokemon_extraction_chain(self, verbose: bool = False):
        """
        创建宝可梦信息提取链

        Args:
            verbose: 是否显示详细日志

        Returns:
            宝可梦信息提取链
        """
        map_prompt = self.get_pokemon_map_prompt()
        reduce_prompt = self.get_pokemon_reduce_prompt()

        return self.create_map_reduce_chain(map_prompt, reduce_prompt, verbose)

    def extract_pokemon_info(self, documents: List[Document]) -> tuple[bool, Any, str]:
        """
        提取宝可梦信息

        Args:
            documents: 文档列表

        Returns:
            tuple: (success, result, error_message)
        """
        try:
            # 创建提取链
            chain = self.create_pokemon_extraction_chain()

            # 运行提取链
            success, result, error_msg = self.run_chain_with_timeout(chain, documents)

            if success:
                logger.info("宝可梦信息提取成功")
                return True, result, ""
            else:
                return False, result, error_msg

        except Exception as e:
            error_msg = f"宝可梦信息提取异常: {e}"
            logger.error(error_msg)
            error_response = {
                "success": False,
                "error": error_msg,
                "suggestion": "信息提取过程中发生异常，请尝试其他网站",
                "error_type": "extraction_error"
            }
            return False, error_response, error_msg

    def validate_llm_response(self, response: str) -> tuple[bool, Any, str]:
        """
        验证LLM响应

        Args:
            response: LLM响应字符串

        Returns:
            tuple: (is_valid, parsed_data, error_message)
        """
        try:
            # 尝试解析JSON
            parsed_data = json.loads(response)

            # 验证是否为有效的宝可梦数据
            if not isinstance(parsed_data, dict):
                return False, None, "LLM返回的不是JSON对象"

            # 检查是否包含宝可梦相关信息
            has_pokemon_data = any(
                key in parsed_data for key in ['types', 'abilities', 'base_stats', 'evolution_chain']
            )

            if not has_pokemon_data:
                logger.warning("LLM返回的数据中未检测到宝可梦相关信息")

            return True, parsed_data, ""

        except json.JSONDecodeError as e:
            error_msg = f"JSON解析失败: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    def update_llm_config(self, **kwargs):
        """
        更新LLM配置

        Args:
            **kwargs: 配置参数
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.info(f"LLM配置更新: {key} = {value}")

        # 重新创建LLM实例
        if any(key in kwargs for key in ['model_name', 'base_url', 'temperature', 'timeout']):
            self.llm = self._create_llm()
            self.timeout_tool = TimeoutTool(default_timeout=self.timeout)
            logger.info("LLM实例已重新创建")

    def get_llm_info(self) -> Dict[str, Any]:
        """
        获取LLM信息

        Returns:
            LLM配置信息
        """
        return {
            "model_name": self.model_name,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "timeout": self.timeout,
            "max_tokens": getattr(self.llm, 'max_tokens', 'default'),
            "model_kwargs": getattr(self.llm, 'model_kwargs', {})
        }