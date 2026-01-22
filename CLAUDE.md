<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


## 要求
- 每次使用中文输出,你在对话中的思考
- 问题修复时，需要详细描述问题发生原因，以及输出解决的思路

## Project Overview

实时网络检索与对战型宝可梦Multi-Agent系统。项目目标：创建能实时上网查询宝可梦信息，组建宝可梦队伍，与模型对战，并与用户进行对话的Agent系统。

## 总体计划

**阶段一**: ✅ 构建核心信息获取工具 (PokemonInfoTool) - 系统基石，负责从互联网精准抓取宝可梦数据
**阶段二**: ⏳ 创建宝可梦检索Agent - 让Agent学会使用工具，理解用户意图，整理数据为用户友好格式
**阶段三**: ⏳ 搭建后端服务 (API) - 将Agent封装成服务，供网页端调用
**阶段四**: ⏳ 实现多Agent路由与对战逻辑 - 扩展系统，加入主Agent和对战Agent
**阶段五**: ⏳ 网页集成 - 开发网页界面并与后端服务对接

## 当前进度

✅ **阶段一已完成**
- 核心工具 `PokemonInfoTool` 完全实现
- 支持智能搜索、权威来源选择、网页抓取、LLM信息提取
- 完整的错误处理和超时机制
- 测试脚本验证功能正常

## Development Commands

### Environment Setup
```bash
# Install dependencies from requirements.txt
pip install -r requirements.txt

# Alternatively, use uv (if preferred)
uv pip install -r requirements.txt
```

### Running the Application
```bash
# Run the main application
python main.py

# Test the PokemonInfoTool
python test_pokemon_tool.py

# Run FastAPI application (once implemented)
uvicorn app.main:app --reload
```

### Development Environment
- Python version: >=3.11
- Package manager: pip (uv is also available)
- Virtual environment: venv (present in project root)
- Required env vars: `ROUTER_API_KEY`, `TAVILY_API_KEY`

## Project Architecture

### Directory Structure
```
pokemon_agent_backend/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py              # FastAPI application entry point (placeholder)
│   ├── main_agent.py        # Main agent implementation (placeholder)
│   ├── models.py            # Data models (placeholder)
│   ├── retrieval_agent.py   # Retrieval agent implementation (placeholder)
│   └── tools/
│       └── pokemon_tool.py # ✅ Core PokemonInfoTool implementation
├── main.py                  # Entry point with basic Pokémon tool test
├── test_pokemon_tool.py     # ✅ Comprehensive tool testing
├── requirements.txt         # Python dependencies
└── pyproject.toml          # Project configuration
```

### Key Dependencies
- **fastapi**: Web framework for building APIs
- **uvicorn**: ASGI server for FastAPI
- **langchain**: Framework for building LLM applications
- **langchain_openai**: OpenAI integration for LangChain
- **langchain_community**: Community tools including Tavily search
- **beautifulsoup4**: Web scraping library
- **tavily-python**: Search API integration

### Current Implementation Status

#### ✅ 已完成组件
1. **PokemonInfoTool** (`app/tools/pokemon_tool.py`)
   - 智能搜索：使用Tavily API搜索宝可梦信息
   - 权威来源选择：优先wiki.52poke.com等站点
   - 网页抓取：WebBaseLoader加载内容
   - LLM信息提取：使用GPT模型提取结构化数据
   - 完整错误处理：超时保护、重试机制、降级提取
   - 超时控制：搜索30s、网页加载20s、LLM处理45s

2. **测试框架** (`test_pokemon_tool.py`)
   - 完整的功能测试脚本
   - 环境变量检查
   - 多宝可梦测试用例

#### ⏳ 待完成组件
1. **FastAPI应用** (`app/main.py`) - 需要实现API端点
2. **Agent架构** (`app/main_agent.py`, `app/retrieval_agent.py`) - 需要实现Agent逻辑
3. **数据模型** (`app/models.py`) - 需要定义数据结构
4. **多Agent路由** - 需要实现对战逻辑和Agent协调

### Next Development Steps
**优先级顺序:**
1. 实现FastAPI应用端点，封装PokemonInfoTool为HTTP服务
2. 创建retrieval_agent，集成工具并处理用户对话
3. 设计数据模型，规范宝可梦信息结构
4. 实现main_agent，协调多个子Agent
5. 添加对战Agent和路由逻辑