# PokemonInfoTool 使用说明

## 概述

`PokemonInfoTool` 是一个自定义的 LangChain 工具，用于从权威来源搜索和提取宝可梦信息。该工具实现了以下功能：

1. **智能搜索**: 使用 Tavily API 搜索宝可梦相关信息
2. **权威来源选择**: 优先选择来自 wiki.52poke.com、serebii.net 等权威站点的链接
3. **网页抓取**: 使用 WebBaseLoader 加载网页内容
4. **智能提取**: 使用 LLM (GPT-4) 从 HTML 内容中提取结构化的宝可梦信息
5. **JSON 输出**: 返回包含所有宝可梦信息的 JSON 对象

## 功能特性

### 核心功能
- 🎯 **精确搜索**: 构造精确的中文查询，如 "皮卡丘 宝可梦 图鉴 神奇宝贝百科"
- 🔗 **智能链接选择**: 优先选择权威站点，确保信息准确性
- 📊 **结构化提取**: 提取全面的宝可梦信息，包括：
  - 基本信息（名称、编号、属性、种族值等）
  - 战斗数据（HP、攻击、防御等六维数据）
  - 进化链信息
  - 游戏信息（世代、版本等）
  - 额外信息（颜色、蛋群等）

### 技术特点
- 🚀 **异步支持**: 基于现代 Python 异步编程
- 🔄 **错误恢复**: 内置重试机制，提高成功率
- 📈 **可扩展性**: 模块化设计，易于扩展和维护

## 安装与配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 环境变量配置

创建 `.env` 文件或设置以下环境变量：

```bash
# OpenAI API Key (用于 LLM 信息提取)
export OPENAI_API_KEY="your_openai_api_key_here"

# Tavily API Key (用于网络搜索)
export TAVILY_API_KEY="your_tavily_api_key_here"
```

### 3. 可选配置

```bash
# 设置用户代理标识（推荐）
export USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

## 使用方法

### 基本使用

```python
from app.tools.pokemon_tool import PokemonInfoTool

# 创建工具实例
tool = PokemonInfoTool()

# 使用工具搜索宝可梦
result = tool._run("皮卡丘")

# 处理结果
if "error" not in result:
    print("成功获取信息!")
    print("数据来源:", result.get('source_url'))
    print("宝可梦信息:", result.get('data'))
else:
    print("错误:", result['error'])
```

### 在 LangChain Agent 中使用

```python
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.tools.pokemon_tool import PokemonInfoTool

# 创建工具
tools = [PokemonInfoTool()]

# 创建 LLM
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

# 创建 Agent
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个宝可梦专家助手，使用提供的工具回答宝可梦相关问题。"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 使用 Agent
response = agent_executor.invoke({
    "input": "请告诉我皮卡丘的详细信息和能力值"
})
```

## 输出格式

工具返回的 JSON 对象包含以下结构：

```json
{
  "pokemon_name": "皮卡丘",
  "source_url": "https://wiki.52poke.com/wiki/皮卡丘",
  "extraction_timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "basic_info": {
      "name": "皮卡丘",
      "national_dex": "25",
      "types": ["电"],
      "species": "鼠宝可梦",
      "height": "0.4",
      "weight": "6.0",
      "abilities": ["静电", "避雷针"]
    },
    "battle_stats": {
      "hp": "35",
      "attack": "55",
      "defense": "40",
      "special_attack": "50",
      "special_defense": "50",
      "speed": "90",
      "total": "320"
    },
    "evolution_chain": {
      "stage": "Basic",
      "evolves_from": "Pichu",
      "evolves_to": "Raichu"
    },
    "game_info": {
      "generation": "I",
      "version_debut": "红/绿/蓝"
    },
    "additional_info": {
      "color": "黄色",
      "egg_groups": ["陆上", "妖精"]
    }
  }
}
```

## 测试

运行测试脚本：

```bash
python test_pokemon_tool.py
```

这个脚本会测试几个经典宝可梦的信息提取功能。

## 错误处理

工具内置了多种错误处理机制：

1. **搜索失败**: 当无法找到搜索结果时，返回错误信息
2. **网页加载失败**: 当无法加载网页内容时，返回详细错误
3. **信息提取失败**: 当 LLM 无法正确提取信息时，会尝试使用简化的提示重试
4. **网络异常**: 捕获所有网络相关异常并提供友好的错误信息

## 注意事项

1. **API 限制**: 请确保您的 OpenAI 和 Tavily API 密钥有足够的配额
2. **网络延迟**: 由于涉及网络搜索和网页抓取，响应时间可能较长
3. **内容准确性**: 工具依赖于权威网站的信息，但建议在使用关键信息时进行验证
4. **语言支持**: 工具主要针对中文和英文宝可梦名称进行优化

## 扩展开发

### 添加新的权威站点

在 `_select_best_url` 方法中添加新的域名到 `priority_domains` 列表：

```python
priority_domains = [
    "wiki.52poke.com",
    "serebii.net",
    "bulbapedia.bulbagarden.net",
    "pokemon.com",
    "new-authority-site.com"  # 新增
]
```

### 修改提取字段

在 `_extract_with_llm` 方法的提示模板中添加或修改需要提取的信息字段。

### 更换 LLM 模型

在 `__init__` 方法中修改 LLM 的初始化参数：

```python
self.llm = ChatOpenAI(
    model="gpt-3.5-turbo",  # 更换模型
    temperature=0.1,        # 调整温度
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
```

## 许可证

本项目遵循 MIT 许可证。