"""
宝可梦Mcp Client，集成多个MCP工具
支持宝可梦信息、检索等多种服务的调用
"""
import json
import logging
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
# Ensure your FastAPI server (main.py) is running!
client = MultiServerMCPClient(
    {
        "math": {
            "command": "uv",
            # Make sure to update to the full absolute path to your math_server.py file
            "args": [
                    "--directory", 
                    "/Users/wangwei/project/personel/pokemon_mcp", 
                    "run", 
                    "pokemon_mcp.py"
            ],
            "transport": "stdio"
        }
        #"weather": {
            # Make sure you start your weather server on port 8000
        #    "url": "http://localhost:8000/mcp/",
        #    "transport": "streamable_http",
        #}
    }
)

class PokemonMcpTool:
    def __init__(self):
        self.client = client
        self.tools = None

    async def get_available_tools(self):
        """获取可用工具列表"""
        if self.tools is None:
            self.tools = await self.client.get_tools()
        return self.tools

    async def direct_tool_call(self, tool_name, **kwargs):
        """直接调用指定工具"""
        try:
            if self.tools is None:
                await self.get_available_tools()

            # 查找对应的工具
            tool = None
            for t in self.tools:
                if t.name == tool_name:
                    tool = t
                    break

            if tool is None:
                return {"error": f"Tool {tool_name} not found"}

            # 调用工具
            result = await tool.ainvoke(kwargs)
            return result
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {"error": str(e)}

    async def get_pokemon_info(self, pokemon_name: str):
        """查询宝可梦信息，使用MCP工具"""
        try:
            if self.tools is None:
                await self.get_available_tools()

            # 查找get_pokemon_info工具
            tool = None
            for t in self.tools:
                if t.name == "get_pokemon_info":
                    tool = t
                    break

            if tool is None:
                return {"error": "get_pokemon_info tool not found"}

            # 调用工具
            result = await tool.ainvoke({"identifier": pokemon_name})
            return result
        except Exception as e:
            logger.error(f"Error fetching info for {pokemon_name}: {e}")
            return {"error": str(e)}

# 使用示例
async def main():
    # 初始化增强的宝可梦Agent
    mcpTool = PokemonMcpTool()

    # 获取可用工具
    available_tools = await mcpTool.get_available_tools()
    print("可用工具:", json.dumps([str(tool) for tool in available_tools], indent=2, ensure_ascii=False))

    # 检索宝可梦 (search_pokemon 需要query参数)
    search_pokemon = await mcpTool.direct_tool_call("search_pokemon", query="pikachu")
    print("宝可梦检索:", json.dumps(search_pokemon, indent=2, ensure_ascii=False))

    # 查询宝可梦信息（只使用基本工具，需要英文名称）
    basic_result = await mcpTool.get_pokemon_info("pikachu")
    print("基本查询结果:", json.dumps(basic_result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())