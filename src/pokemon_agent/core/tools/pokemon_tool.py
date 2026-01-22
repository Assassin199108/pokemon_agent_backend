import os
from .time_out_tool import TimeoutHandler, TimeoutError
import logging
from typing import Type, Dict, Any, List, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_community.tools import TavilySearchResults
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
import json
from ..services.mcp_client.pokemon_mcp_tool import PokemonMcpTool
from langgraph.prebuilt import create_react_agent

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 1. 定义工具的输入模型
class PokemonInput(BaseModel):
    pokemon_name: str = Field(description="The name of the Pokémon to search for in Chinese or English.")

# 2. 定义核心工具
class PokemonInfoTool(BaseTool):
    name: str = "pokemon_info_tool"
    description: str = "Searches for comprehensive Pokémon information from authoritative sources and extracts structured data."
    args_schema: Type[BaseModel] = PokemonInput

    # 使用Field定义可选字段，提供默认值
    search: Optional[TavilySearchResults] = Field(default=None, exclude=True)
    llm: Optional[ChatOpenAI] = Field(default=None, exclude=True)
    parser: Optional[JsonOutputParser] = Field(default=None, exclude=True)
    tools: Optional[List[Any]] = Field(default=None, exclude=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化搜索工具
        logger.info("Initializing TavilySearchResults with max_results=5")
        self.search = TavilySearchResults(max_results=5)
        self.tools = PokemonMcpTool.get_available_tools
        # 初始化LLM（使用GPT-3.5-turbo以提高响应速度）
        self.llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            model="x-ai/grok-4-fast:free",
            # model="gpt-oss-120b",
            temperature=0,
            api_key=os.getenv("ROUTER_API_KEY"),
            timeout=30,  # 添加超时设置
            max_retries=2  # 添加重试次数限制
        )
        # 初始化JSON解析器
        self.parser = JsonOutputParser()
        logger.info("PokemonInfoTool initialization completed")

    def _select_best_url(self, search_results: List[Dict[str, Any]]) -> Optional[str]:
        """从搜索结果中选择最佳的URL，优先选择权威站点"""
        logger.info(f"Selecting best URL from {len(search_results)} search results")
        if not search_results:
            logger.warning("No search results available for URL selection")
            return None

        # 定义权威站点的优先级
        priority_domains = [
            "wiki.52poke.com",
            "serebii.net",
            "bulbapedia.bulbagarden.net",
            "pokemon.com",
            "pokemon.jp"
        ]

        # 首先检查是否有高优先级域名
        for result in search_results:
            url = result.get('url', '')
            logger.debug(f"Checking URL: {url}")
            for domain in priority_domains:
                if domain in url:
                    logger.info(f"Found priority domain URL: {url}")
                    return url

        # 如果没有找到高优先级域名，返回第一个结果
        fallback_url = search_results[0].get('url')
        logger.info(f"No priority domain found, using fallback URL: {fallback_url}")
        return fallback_url

    def _extract_with_llm(self, html_content: str, pokemon_name: str) -> Dict[str, Any]:
        """使用LLM从HTML内容中提取宝可梦信息"""
        logger.info(f"Starting LLM extraction for Pokemon: {pokemon_name}")
        logger.debug(f"HTML content length: {len(html_content)} characters")

        # 创建专门的提取提示
        prompt = PromptTemplate(
            template="""
            You are a Pokémon information extraction expert. Please carefully analyze the provided HTML content and extract comprehensive information about the Pokémon "{pokemon_name}".

            Please extract the following information and return it in JSON format with ENGLISH keys and CHINESE/ENGLISH values:

            1. **Basic Information:**
               - name: Name in both Chinese and English, e.g., "皮卡丘 Pikachu"
               - national_dex_number: National Pokédex Number, e.g., "025"
               - types: Types in Chinese and English, e.g., ["电 Electric"]
               - species: Species in Chinese and English, e.g., "鼠宝可梦 Mouse Pokémon"
               - height: Height in meters, e.g., "0.4米 0.4m"
               - weight: Weight in kilograms, e.g., "6.0公斤 6.0kg"
               - abilities: Abilities in Chinese and English, e.g., ["静电 Static", "避雷针 Lightning Rod"]
               - gender_ratio: Gender ratio, e.g., "50%雄性 50% Male, 50%雌性 50% Female"
               - catch_rate: Catch rate, e.g., "190"
               - base_friendship: Base Friendship, e.g., "70"
               - base_experience: Base Experience yield, e.g., "112"

            2. **Battle Stats:**
               - hp: HP in Chinese and English, e.g., "35 生命值 HP"
               - attack: Attack in Chinese and English, e.g., "55 攻击 Attack"
               - defense: Defense in Chinese and English, e.g., "40 防御 Defense"
               - special_attack: Special Attack in Chinese and English, e.g., "50 特攻 Special Attack"
               - special_defense: Special Defense in Chinese and English, e.g., "50 特防 Special Defense"
               - speed: Speed in Chinese and English, e.g., "90 速度 Speed"
               - base_stat_total: Base Stat Total, e.g., "320 总和 Total"
               - effort_values: Effort Values (EVs) in Chinese and English, e.g., "速度 Speed: 2 努力值 EV"

            3. **Evolution Chain:**
               - evolution_stage: Evolution stage in Chinese and English, e.g., "基础形态 Basic Stage"
               - evolution_methods: Evolution methods and conditions in Chinese and English, e.g., "使用雷之石进化 Evolve using Thunder Stone"
               - previous_form: Previous form in chain with both languages, e.g., "皮丘 Pichu"
               - next_form: Next form in chain with both languages, e.g., "雷丘 Raichu"

            4. **Game Information:**
               - generation_introduced: Generation introduced in both languages, e.g., "第一代 Generation I"
               - version_debut: Version debut in both languages, e.g., "红/绿/蓝版本 Red/Green/Blue Version"
               - location_methods: Location methods in both languages, e.g., "常青森林 Viridian Forest"

            5. **Additional Info:**
               - color: Color in both languages, e.g., "黄色 Yellow"
               - egg_groups: Egg groups in both languages, e.g., ["陆上蛋群 Field Group", "妖精蛋群 Fairy Group"]
               - egg_cycles: Egg cycles with description, e.g., "10 孵化周期 Egg Cycles"
               - base_happiness: Base happiness with description, e.g., "70 初始友好度 Base Happiness"
               - growth_rate: Growth rate in both languages, e.g., "中等 Medium"
               - habitat: Habitat in both languages, e.g., "森林 Forest Habitat"

            6. **Image URLs:**
               - official_artwork: URL of the official Pokémon artwork image e.g., "https://wiki.52poke.com/wiki/File:025Pikachu.png"

            Please be thorough and accurate. If information is not available in the HTML content, use "N/A" for that field.
            For image URLs, look for img tags, src attributes, or any image links related to the Pokémon. Focus on finding:
            - Main official artwork/sprite

            IMPORTANT: Use ENGLISH keys for all JSON fields. Provide values in both Chinese and English when possible, separated by spaces or slashes.

            HTML Content:
            {html_content}

            Please return the extracted information in the following JSON format:
            {format_instructions}
            """,
            input_variables=["pokemon_name", "html_content"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        # 限制HTML内容长度以避免上下文溢出和减少处理时间
        truncated_html = html_content[:25000]  # 从25K减少到10K
        logger.info(f"Truncated HTML content to {len(truncated_html)} characters for faster processing")

        try:
            logger.info("Creating and invoking primary LLM extraction chain")
            agent = create_react_agent(model=self.llm, tools=self.tools)
            chain = prompt | agent | self.parser
            result = chain.invoke({
                "pokemon_name": pokemon_name,
                "html_content": truncated_html
            })
            logger.info("Primary LLM extraction completed successfully")
            return result
        except Exception as e:
            logger.warning(f"Primary LLM extraction failed: {str(e)}")
            # 如果JSON解析失败，尝试重新提取
            logger.info("Attempting retry extraction with simplified prompt")
            try:
                logger.info("Creating retry prompt template")
                retry_prompt = PromptTemplate(
                    template="""
                    Please extract Pokémon information from the HTML and return ONLY valid JSON with ENGLISH keys and CHINESE/ENGLISH values.
                    Focus on: name, types, abilities, base_stats, evolution_chain, image_urls.

                    For basic_info, include fields like: name, types, abilities
                    For battle_stats, include: hp, attack, defense, special_attack, special_defense, speed
                    For evolution_chain, include: evolution_stage, evolution_methods
                    For image_urls, extract any image links related to:
                    - Official artwork/sprite

                    IMPORTANT: Use ENGLISH keys for all JSON fields. Provide values in both Chinese and English when possible.

                    HTML Content:
                    {html_content}

                    Return JSON format with ENGLISH keys and CHINESE/ENGLISH values:
                    {{
                        "basic_info": {{
                            "name": "皮卡丘 Pikachu",
                            "types": ["电 Electric"],
                            "abilities": ["静电 Static", "避雷针 Lightning Rod"]
                        }},
                        "battle_stats": {{
                            "hp": "35 生命值 HP",
                            "attack": "55 攻击 Attack",
                            "defense": "40 防御 Defense",
                            "special_attack": "50 特攻 Special Attack",
                            "special_defense": "50 特防 Special Defense",
                            "speed": "90 速度 Speed"
                        }},
                        "evolution_chain": {{
                            "evolution_stage": "基础形态 Basic Stage",
                            "evolution_methods": "使用雷之石进化 Evolve using Thunder Stone"
                        }},
                        "game_info": {{
                            "generation_introduced": "第一代 Generation I",
                            "version_debut": "红/绿/蓝版本 Red/Green/Blue Version"
                        }},
                        "additional_info": {{
                            "color": "黄色 Yellow",
                            "habitat": "森林 Forest Habitat"
                        }},
                        "image_urls": {{
                            "official_artwork": "https://wiki.52poke.com/wiki/File:025Pikachu.png"
                        }}
                    }}
                    """,
                    input_variables=["html_content"]
                )

                logger.info("Creating and invoking retry LLM extraction chain")
                retry_truncated_html = truncated_html[:20000]  # 进一步减少重试时的内容长度
                logger.debug(f"Retry HTML content length: {len(retry_truncated_html)} characters")
                retry_chain = retry_prompt | self.llm | self.parser
                retry_result = retry_chain.invoke({"html_content": retry_truncated_html})
                logger.info("Retry LLM extraction completed successfully")
                return retry_result
            except Exception as retry_e:
                logger.error(f"Retry LLM extraction also failed: {str(retry_e)}")
                return {
                    "error": f"Failed to extract information: {str(e)}",
                    "fallback_error": f"Retry also failed: {str(retry_e)}"
                }

    def _run(self, pokemon_name: str) -> Dict[str, Any]:
        """执行宝可梦信息检索和提取"""
        logger.info(f"Starting Pokemon info extraction for: {pokemon_name}")
        try:
            # 步骤1: 搜索 (添加超时处理)
            logger.info("Step 1: Starting search phase")
            try:
                search_query = f"{pokemon_name} 宝可梦 图鉴 神奇宝贝百科"
                logger.debug(f"Search query: {search_query}")
                with TimeoutHandler(30):  # 30秒搜索超时
                    logger.info("Invoking Tavily search")
                    search_results = self.search.invoke(search_query)
                    logger.info(f"Search completed, returned {len(search_results)} results")
            except TimeoutError:
                logger.error("Search operation timed out after 30 seconds")
                return {"error": "Search operation timed out after 30 seconds"}

            if not search_results:
                logger.warning(f"No search results found for {pokemon_name}")
                return {"error": f"No search results found for {pokemon_name}"}

            # 步骤2: 选择最佳链接
            logger.info("Step 2: Selecting best URL from search results")
            best_url = self._select_best_url(search_results)
            if not best_url:
                logger.error("Could not find a suitable URL from search results")
                return {"error": "Could not find a suitable URL from search results"}

            # 步骤3: 抓取网页内容 (添加超时处理)
            logger.info("Step 3: Loading webpage content")
            try:
                logger.debug(f"Loading content from URL: {best_url}")
                with TimeoutHandler(20):  # 20秒网页加载超时
                    loader = WebBaseLoader(best_url)
                    docs = loader.load()
                    html_content = docs[0].page_content
                    logger.info(f"Webpage content loaded, length: {len(html_content)} characters")

                    if not html_content or len(html_content.strip()) < 100:
                        logger.warning("Insufficient content loaded from the webpage")
                        return {"error": "Insufficient content loaded from the webpage"}

            except TimeoutError:
                logger.error("Webpage loading timed out after 20 seconds")
                return {"error": "Webpage loading timed out after 20 seconds"}
            except Exception as e:
                logger.error(f"Failed to load webpage content: {str(e)}")
                return {"error": f"Failed to load webpage content: {str(e)}"}

            # 步骤4: 使用LLM提取信息 (添加超时处理)
            logger.info("Step 4: Starting LLM information extraction")
            try:
                with TimeoutHandler(45):  # 减少到45秒LLM处理超时
                    logger.info("Starting LLM extraction with timeout protection")
                    extracted_info = self._extract_with_llm(html_content, pokemon_name)
                    logger.info("LLM information extraction completed successfully")
            except TimeoutError:
                logger.error("LLM information extraction timed out after 45 seconds")
                # 尝试降级提取模式
                logger.info("Attempting fallback extraction mode")
                try:
                    fallback_result = self._fallback_extraction(html_content, pokemon_name)
                    if fallback_result and not fallback_result.get("error"):
                        logger.info("Fallback extraction completed successfully")
                        extracted_info = fallback_result
                    else:
                        return {"error": "LLM information extraction timed out and fallback failed"}
                except Exception as fallback_e:
                    logger.error(f"Fallback extraction also failed: {str(fallback_e)}")
                    return {"error": "LLM information extraction timed out after 45 seconds and fallback failed"}

            # 添加元数据
            logger.info("Compiling final result with metadata")
            result = {
                "pokemon_name": pokemon_name,
                "source_url": best_url,
                "extraction_timestamp": str(json.dumps({"timestamp": "current_time"})),  # 简单的时间戳
                "data": extracted_info
            }

            logger.info(f"Pokemon info extraction completed successfully for: {pokemon_name}")
            return result

        except Exception as e:
            logger.error(f"Unexpected error during execution: {str(e)}")
            return {"error": f"Unexpected error during execution: {str(e)}"}

    def _fallback_extraction(self, html_content: str, pokemon_name: str) -> Dict[str, Any]:
        """降级提取模式 - 使用更简单的提示和更少的内容"""
        logger.info("Starting fallback extraction with simplified approach")

        try:
            # 使用极简的提示模板
            fallback_prompt = PromptTemplate(
                template="""
                Extract basic Pokemon information from HTML content for {pokemon_name}.
                Return only this JSON structure with ENGLISH keys and CHINESE/ENGLISH values:
                {{
                    "name": "皮卡丘 Pikachu",
                    "types": ["电 Electric", "飞行 Flying"],
                    "abilities": ["静电 Static", "避雷针 Lightning Rod"],
                    "basic_stats": {{
                        "hp": "35 生命值 HP",
                        "attack": "55 攻击 Attack",
                        "defense": "40 防御 Defense",
                        "special_attack": "50 特攻 Special Attack",
                        "special_defense": "50 特防 Special Defense",
                        "speed": "90 速度 Speed"
                    }},
                    "image_urls": {{
                        "official_artwork": "https://wiki.52poke.com/wiki/File:025Pikachu.png"
                    }}
                }}

                Also extract any image URLs found in the HTML for official artwork, type charts, or other Pokemon-related images.
                Use ENGLISH keys and provide values in both Chinese and English when possible.
                Focus on comprehensive bilingual output for better user experience.

                HTML: {html_content}
                """,
                input_variables=["pokemon_name", "html_content"]
            )

            # 只使用前3000字符
            minimal_html = html_content[:3000]
            logger.info(f"Using minimal HTML content: {len(minimal_html)} characters")

            # 创建简化链
            fallback_chain = fallback_prompt | self.llm | self.parser

            logger.info("Invoking fallback extraction chain")
            result = fallback_chain.invoke({
                "pokemon_name": pokemon_name,
                "html_content": minimal_html
            })

            logger.info("Fallback extraction completed successfully")
            return result

        except Exception as e:
            logger.error(f"Fallback extraction failed: {str(e)}")
            return {"error": f"Fallback extraction failed: {str(e)}"}

    async def _arun(self, _pokemon_name: str) -> Dict[str, Any]:
        """异步版本"""
        raise NotImplementedError("This tool does not support async execution yet.")