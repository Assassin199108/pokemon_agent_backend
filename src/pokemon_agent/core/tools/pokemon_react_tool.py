import logging
import os
from typing import Dict, Any, List, Optional
from langchain_core.tools import BaseTool
from pydantic import Field
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..services.mcp_client.pokemon_mcp_tool import PokemonMcpTool
from .sub_tools.web_search import web_search
from .sub_tools.web_content_scraper import web_content_scraper

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# =========================
# 主ReAct宝可梦工具
# =========================

class PokemonReactTool(BaseTool):
    """基于ReAct模式的宝可梦信息检索工具"""
    name: str = "pokemon_react_tool"
    description: str = "使用ReAct模式智能检索宝可梦信息，自主思考、行动、观察直到收集充分数据"
    tools: Optional[List[Any]] = Field(default=None, exclude=True)
    all_sub_tools: Optional[List[Any]] = Field(default=None, exclude=True)
    mcp_client: Optional[Any] = Field(default=None, exclude=True)
    mcp_tools: Optional[List[Any]] = Field(default=None, exclude=True)
    manual_tools: Optional[List[Any]] = Field(default=None, exclude=True)
    llm: Optional[Any] = Field(default=None, exclude=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 初始化MCP客户端
        self.mcp_client = PokemonMcpTool()
        self.mcp_tools = []

        # 定义我们自己的、非MCP的工具
        self.manual_tools = [web_search, web_content_scraper]

        # 初始化所有工具为空列表，将在需要时动态加载
        self.all_sub_tools = self.manual_tools.copy()

        # 初始化LLM
        self.llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            model="x-ai/grok-4-fast:free",
            temperature=0.2,  # 稍微增加创造性，有利于ReAct思考
            api_key=os.getenv("ROUTER_API_KEY"),
            timeout=45,
            max_retries=2
        )

        logger.info("PokemonReactTool初始化完成")

    async def _load_mcp_tools(self):
        """异步加载MCP工具"""
        if not self.mcp_tools:
            try:
                self.mcp_tools = await self.mcp_client.get_available_tools()
                # 更新所有工具列表
                self.all_sub_tools = self.mcp_tools + self.manual_tools
                logger.info(f"成功加载 {len(self.mcp_tools)} 个MCP工具")
            except Exception as e:
                logger.error(f"加载MCP工具失败: {e}")
                # 如果MCP工具加载失败，只使用手动工具
                self.all_sub_tools = self.manual_tools.copy()

    def _ensure_tools_loaded(self):
        """确保工具已加载（同步包装器）"""
        if not self.mcp_tools:
            try:
                # 检查是否已经有事件循环在运行
                import asyncio
                try:
                    loop = asyncio.get_running_loop()
                    # 如果有循环在运行，不能嵌套，直接使用手动工具
                    logger.warning("检测到运行中的事件循环，跳过MCP工具加载")
                    self.all_sub_tools = self.manual_tools.copy()
                except RuntimeError:
                    # 没有运行中的循环，可以创建新的
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self._load_mcp_tools())
                    loop.close()
            except Exception as e:
                logger.error(f"同步加载MCP工具失败: {e}")
                self.all_sub_tools = self.manual_tools.copy()

    def _create_system_prompt(self):
        """创建ReAct代理的系统提示"""
        from langchain_core.prompts import PromptTemplate

        prompt_text = """你是一个专业的宝可梦信息专家，使用ReAct（推理-行动-观察）模式来收集宝可梦信息。

**你的核心任务**: 收集用户查询宝可梦的完整、准确信息，包括：
1. **基本信息**（名称、编号、属性、特性、身高、体重、分类等）
2. **战斗数据**（HP、攻击、防御、特攻、特防、速度、种族值总和）
3. **进化链信息**（进化阶段、进化条件、前后形态）
4. **游戏信息**（首次出现世代、版本、捕获地点）
5. **其他信息**（颜色、蛋群、生长率、栖息地等）

**可用工具**:
{tools}

**工具名称**:
{tool_names}

**智能工作流程**:
1. **🤔 思考**: 分析当前已有什么信息，还缺什么信息
2. **🛠️ 行动**: 选择最合适的工具获取缺失信息
3. **👀 观察**: 仔细分析工具返回的结果质量
4. **🔄 重复**: 继续思考→行动→观察，直到信息充分

**推荐的工具使用策略**:
**阶段1**: 尝试使用MCP工具获取基础信息（如果有可用的MCP工具）
**阶段2**: 如果MCP信息不足，使用 web_search 搜索相关资料
**阶段3**: 从搜索结果中选择权威网站（优先选择 wiki.52poke.com, bulbapedia.bulbagarden.net 等）
**阶段4**: 使用 web_content_scraper 提取详细的结构化信息
**阶段5**: 整合所有信息，确保数据完整性和一致性

**信息质量评估标准**:
当且仅当满足以下所有条件时，才认为信息收集充分：
✅ **基本信息完整**: 至少包含名称、属性、特性
✅ **战斗数据完整**: 包含所有六维基础数值
✅ **进化链清晰**: 能够理解进化关系和条件
✅ **游戏背景明确**: 知道首次出现和主要游戏信息
✅ **数据一致性**: 不同来源的信息不冲突

**容错和降级策略**:
- 如果某个工具失败，立即尝试替代方案
- 如果MCP工具不可用，直接使用网络搜索+内容提取
- 如果某个字段缺失，使用 "N/A" 标记，但尽量从其他来源补充

**最终输出格式**:
当信息收集充分后，使用以下JSON格式输出最终答案，键名使用英文，值使用中英文双语：

```json
{{"basic_info": {{"name": "皮卡丘 Pikachu", "national_dex_number": "025", "types": ["电 Electric"], "species": "鼠宝可梦 Mouse Pokémon", "height": "0.4米 0.4m", "weight": "6.0公斤 6.0kg", "abilities": ["静电 Static", "避雷针 Lightning Rod"]}}, "battle_stats": {{"hp": "35 生命值 HP", "attack": "55 攻击 Attack", "defense": "40 防御 Defense", "special_attack": "50 特攻 Special Attack", "special_defense": "50 特防 Special Defense", "speed": "90 速度 Speed", "base_stat_total": "320 总和 Total"}}, "evolution_chain": {{"evolution_stage": "基础形态 Basic Stage", "evolution_methods": "使用雷之石进化 Evolve using Thunder Stone", "previous_form": "皮丘 Pichu", "next_form": "雷丘 Raichu"}}, "game_info": {{"generation_introduced": "第一代 Generation I", "version_debut": "红/绿/蓝版本 Red/Green/Blue Version", "location_methods": "常青森林 Viridian Forest"}}, "additional_info": {{"color": "黄色 Yellow", "egg_groups": ["陆上蛋群 Field Group", "妖精蛋群 Fairy Group"], "growth_rate": "中等 Medium"}}}}
```

**开始执行**

Question: {input}
Thought: {agent_scratchpad}
"""

        return PromptTemplate.from_template(prompt_text)

    def _run(self, pokemon_name: str) -> Dict[str, Any]:
        """执行ReAct模式的宝可梦信息收集"""
        logger.info(f"开始ReAct模式收集宝可梦信息: {pokemon_name}")

        try:
            # 确保MCP工具已加载
            self._ensure_tools_loaded()
            logger.info(f"当前可用工具数量: {len(self.all_sub_tools)}")

            # 创建ReAct代理
            agent = create_react_agent(
                llm=self.llm,
                tools=self.all_sub_tools,
                prompt=self._create_system_prompt()
            )

            # 构建用户查询
            user_query = f"""
请收集关于"{pokemon_name}"的完整宝可梦信息。

请按照ReAct模式进行：
1. 首先思考需要什么信息
2. 选择合适的工具行动
3. 观察结果并继续
4. 直到信息充分，然后按照指定JSON格式输出最终答案

记住，只有当所有基本信息、战斗数据、进化链、游戏信息都完整时，才输出最终JSON答案。
"""

            logger.info("启动ReAct代理执行...")
            # 创建Agent Executor，优化迭代控制
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.all_sub_tools,
                verbose=False,  # 关闭详细日志以减少干扰
                handle_parsing_errors=True, # 处理解析错误
                max_iterations=6,  # 减少迭代次数以避免复杂状态管理
                early_stopping_method="force",  # 遇到错误时强制停止代理执行
                return_intermediate_steps=False,  # 不返回中间步骤以减少内存使用
                max_execution_time=90,  # 减少最大执行时间
                trim_intermediate_steps=-1  # 修剪中间步骤以避免状态累积
            )
            result = agent_executor.invoke({"input": user_query})

            # 处理代理结果
            if isinstance(result, dict):
                # 检查不同的可能输出格式
                if "output" in result:
                    # 新格式的输出
                    final_message = result["output"]
                elif "messages" in result:
                    # 旧格式的输出
                    final_message = result["messages"][-1].content if result["messages"] else ""
                else:
                    # 直接使用整个结果作为消息
                    final_message = str(result)

                # 检查是否包含JSON格式的最终答案
                if "{" in final_message and "}" in final_message:
                    try:
                        # 尝试提取JSON部分
                        json_start = final_message.find("{")
                        json_end = final_message.rfind("}") + 1
                        json_content = final_message[json_start:json_end]

                        import json
                        final_answer = json.loads(json_content)

                        return {
                            "success": True,
                            "pokemon_name": pokemon_name,
                            "final_answer": final_answer,
                            "agent_output": final_message,
                            "mode": "react_agent"
                        }
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON解析失败: {e}")
                        return {
                            "success": False,
                            "error": f"最终答案JSON格式错误: {str(e)}",
                            "agent_output": final_message
                        }
                else:
                    return {
                        "success": False,
                        "error": "代理未生成完整的最终答案",
                        "agent_output": final_message
                    }
            else:
                return {
                    "success": False,
                    "error": "代理返回格式异常",
                    "raw_result": result
                }

        except Exception as e:
            logger.error(f"ReAct代理执行失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"ReAct代理执行失败: {str(e)}",
                "pokemon_name": pokemon_name
            }

    async def _arun(self, pokemon_name: str) -> Dict[str, Any]:
        """异步版本"""
        # 确保MCP工具已加载（异步方式）
        await self._load_mcp_tools()
        logger.info(f"异步版本当前可用工具数量: {len(self.all_sub_tools)}")

        # 使用同步运行逻辑，但工具已经异步加载
        return self._run(pokemon_name)


# 为了兼容性，保持原有的类名
PokemonReactAgent = PokemonReactTool