# Changelog

## [Unreleased]

## [1.2.6] - 2026-01-22

### 重大变更
- **LangChain 1.2.6 升级**: 从 LangChain 0.3.x 升级到 1.2.6 稳定版本
  - `langchain` 0.3.27 → **1.2.6**
  - `langchain-core` 0.3.76 → **1.2.7**
  - `langchain-openai` 0.3.33 → **1.1.7**
  - `langgraph` 0.6.7 → **1.0.6**
  - `langchain-mcp-adapters` 0.1.10 → **0.2.1**
  - 新增: `langchain-text-splitters` **1.1.0**

### 更新内容

#### 依赖更新
- 更新 `pyproject.toml` 中的 LangChain 相关包版本约束
- 移除版本上限限制，确保与 LangChain 1.2.6 的兼容性
- 添加 `langchain-text-splitters>=0.3.0` 作为显式依赖

#### 导入路径更新
- **`src/pokemon_agent/core/tools/pokemon_tool.py`**
  - 更新 `BaseTool` 导入: `langchain.tools` → `langchain_core.tools`
  - 更新 `TavilySearchResults` 导入: `langchain_community.tools.tavily_search` → `langchain_community.tools`

- **`src/pokemon_agent/core/tools/pokemon_react_tool.py`**
  - 更新 `BaseTool` 导入: `langchain.tools` → `langchain_core.tools`
  - 更新 `create_react_agent` 导入: `langchain.agents` → `langgraph.prebuilt`
  - 移除 `AgentExecutor` 导入（代码中仍需要重构）

- **`src/pokemon_agent/core/services/web/extraction/llm_chains.py`**
  - 添加对 `load_summarize_chain` 的兼容性导入处理
  - 使用 try-except 支持不同版本的导入路径

#### 已知问题
- `pokemon_react_tool.py` 中的 `AgentExecutor` 使用需要重构
  - LangChain 1.x 中 `AgentExecutor` API 已改变
  - 当前代码会导致运行时错误
  - 建议迁移到 `langgraph` 的新的 agent 执行模式

### 迁移指南

#### 开发者注意事项
1. **BaseTool 导入**: 所有工具类现在应从 `langchain_core.tools` 导入
   ```python
   # 旧
   from langchain.tools import BaseTool
   # 新
   from langchain_core.tools import BaseTool
   ```

2. **版本兼容性**: LangChain 1.x 是重大版本升级，API 有较大变化
   - 测试所有工具功能确保正常工作
   - 检查自定义 agent 实现是否需要更新

3. **新依赖**: `langchain-text-splitters` 现在是显式依赖
   - 已在 `pyproject.toml` 中添加
   - 自动随其他包一起安装

### 测试状态
- ✅ 基本导入测试通过
- ✅ PokemonInfoTool 初始化正常
- ⚠️ 完整功能测试待完成
- ⚠️ Agent 执行逻辑需要重构

### 相关文件
- `pyproject.toml` - 依赖版本更新
- `uv.lock` - 锁定文件更新
- `src/pokemon_agent/core/tools/pokemon_tool.py` - 导入路径更新
- `src/pokemon_agent/core/tools/pokemon_react_tool.py` - 导入路径更新
- `src/pokemon_agent/core/services/web/extraction/llm_chains.py` - 兼容性导入
- `CHANGELOG.md` - 本文档

### 后续计划
1. 重构 `pokemon_react_tool.py` 中的 AgentExecutor 使用
2. 运行完整测试套件
3. 验证所有工具功能正常
4. 更新相关文档

---

## [0.1.0] - 2026-01-22

### 初始版本
- 基础 PokemonInfoTool 实现
- Web 搜索和内容提取功能
- MCP 工具集成
- 多 Agent 架构（初步）