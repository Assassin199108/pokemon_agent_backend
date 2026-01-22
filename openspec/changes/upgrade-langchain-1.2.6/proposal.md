# Change: Upgrade LangChain to Version 1.2.6

## Why
Current project uses LangChain 0.3.x, which has several limitations:
- Outdated API patterns inconsistent with modern LangChain architecture
- Missing new features and improvements in LangChain 1.x
- Technical debt from pre-1.0 API decisions
- Inconsistent with LangChain's recommended patterns for production applications

Upgrading to LangChain 1.2.6 provides:
- Stable, production-ready API
- Better performance and reliability
- Improved type hints and IDE support
- Consistent patterns across all LangChain components
- Access to latest features and bug fixes

## What Changes

**Breaking Changes - Code Updates Required:**
- Update dependencies in `pyproject.toml`:
  - `langchain>=0.1.0` → `langchain>=1.2.6,<2.0.0`
  - `langchain-core>=0.1.0` → `langchain-core>=0.3.0,<0.4.0`
  - `langgraph>=0.2.0` → `langgraph>=0.2.60,<0.3.0`
  - Update related packages to compatible versions
- Refactor code for LangChain 1.x API changes:
  - Replace deprecated `langchain.tools.BaseTool` with new base class
  - Update `langchain_community.tools.TavilySearchResults` import path
  - Migrate `langchain_core` imports to new module structure
  - Update `langgraph` API usage for agent creation
- Update type hints and model definitions for Pydantic v2 compatibility

**Non-Breaking Changes:**
- Update lock file with `uv lock` and `uv sync`
- Run full test suite to verify compatibility
- Update documentation with new API patterns

## Impact

**Affected Specifications:**
- New capability: `tooling` - Project tooling and dependency management

**Affected Code Files:**
- `pyproject.toml` - Dependency version constraints
- `src/pokemon_agent/core/tools/pokemon_tool.py` - BaseTool usage
- `src/pokemon_agent/core/tools/pokemon_react_tool.py` - Tool implementation
- `src/pokemon_agent/core/tools/sub_tools/web_search.py` - Tavily integration
- `src/pokemon_agent/core/tools/sub_tools/web_content_scraper.py` - Document loaders
- `src/pokemon_agent/core/services/web/processing/web_loader.py` - WebBaseLoader usage
- `src/pokemon_agent/core/services/web/extraction/llm_chains.py` - Chains and prompts
- `src/pokemon_agent/core/services/mcp_client/pokemon_mcp_tool.py` - MCP integration
- `src/pokemon_agent/core/agents/retrieval_agent.py` - Agent creation
- `src/pokemon_agent/core/agents/main_agent.py` - Agent patterns
- All test files that mock or test LangChain components

**Risks:**
- Significant API changes may require substantial refactoring
- Some community integrations may not be fully compatible with 1.x yet
- Need careful testing to ensure battle system logic remains intact
- MCP adapters compatibility needs verification

**Rollback Plan:**
- Branch protection and PR review required
- Keep upgrade branch separate until fully validated
- Original pyproject.toml can be restored if issues arise