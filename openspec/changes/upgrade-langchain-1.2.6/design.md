# Design: LangChain 1.2.6 Upgrade Strategy

## Context
The current codebase uses LangChain 0.3.x, which is the pre-stable release series. LangChain 1.0 introduced significant architectural changes with breaking API modifications that require careful migration planning.

This upgrade affects the entire codebase, particularly the tool implementations, agent orchestration, and external API integrations (Tavily, OpenAI).

## Goals
1. Successfully migrate to LangChain 1.2.6 with minimal functional impact
2. Update all code to use modern, recommended patterns
3. Ensure test coverage remains comprehensive
4. Maintain backward compatibility for existing features
5. Document new patterns for future development

## Non-Goals
- Major architectural refactors beyond LangChain migration
- Changing core business logic or battle mechanics
- Adding new features during the upgrade
- Supporting both 0.x and 1.x APIs simultaneously

## Key Changes from LangChain 0.x to 1.x

### 1. Tool Architecture (`BaseTool` changes)
**Before (0.3.x):**
```python
from langchain.tools import BaseTool

class PokemonInfoTool(BaseTool):
    name: str = "pokemon_info_tool"
    description: str = "..."
    args_schema: Type[BaseModel] = PokemonInput
```

**After (1.2.6):**
```python
from langchain_core.tools import BaseTool

class PokemonInfoTool(BaseTool):
    name: str = "pokemon_info_tool"
    description: str = "..."
    args_schema: Type[BaseModel] = PokemonInput
    # New: explicit return type
    def _run(self, pokemon_name: str) -> dict:
        ...
```

**Impact**: All tool classes need import path updates and may need method signatures adjusted.

### 2. Community Package Restructure
**Before (0.3.x):**
```python
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import WebBaseLoader
```

**After (1.2.6):**
```python
from langchain_community.tools import TavilySearchResults
from langchain_community.document_loaders import WebBaseLoader
# May require additional backward compat imports
```

**Impact**: Import paths changed, some tools moved to separate packages

### 3. LLM and Chat Model Updates
**Before (0.3.x):**
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    model="x-ai/grok-4-fast:free",
    temperature=0,
    api_key=os.getenv("ROUTER_API_KEY"),
)
```

**After (1.2.6):**
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    model="x-ai/grok-4-fast:free",
    temperature=0,
    api_key=os.getenv("ROUTER_API_KEY"),
    # timeout via httpx client if needed
)
# Note: timeout parameter moved or changed
```

**Impact**: Timeout and retry configuration may need updates

### 4. LangGraph Agent Creation
**Before (0.2.x):**
```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(llm, tools)
```

**After (0.2.60):**
```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(llm, tools)
# Same API but internal implementation changes
```

**Impact**: Likely compatible but need testing

## Migration Steps

### Phase 1: Dependency Updates
1. Update `pyproject.toml` with new version constraints
2. Run `uv lock` to regenerate lock file
3. Run `uv sync` to install updated packages
4. Verify all packages resolve without conflicts

### Phase 2: Import Path Updates
1. Update all imports from `langchain.xxx` to new paths
2. Replace deprecated imports with new locations
3. Verify `langchain_community` imports still work
4. Update `langchain_core` imports if needed

### Phase 3: Tool Refactoring
1. Update all `BaseTool` subclass imports
2. Refactor tool `__init__` methods if needed
3. Update `args_schema` patterns to new format
4. Test each tool individually

### Phase 4: Chain and Agent Updates
1. Review LangChain chain usage patterns
2. Update to new `Runnable` interface
3. Verify agent orchestration still works
4. Test end-to-end agent workflows

### Phase 5: Testing and Validation
1. Run full test suite
2. Mock external APIs appropriately
3. Verify error handling still works
4. Performance regression testing

## Testing Strategy

### Unit Tests
- Each tool should have isolated tests
- Mock LLM and API calls
- Verify input validation
- Check error conditions

### Integration Tests
- Test tool combinations
- Verify agent workflows end-to-end
- Test external API integrations
- Validate timeout and retry behavior

### Manual Testing Checklist
- [ ] Single Pokémon lookup works
- [ ] Batch Pokémon lookup works
- [ ] Web search timeout handled gracefully
- [ ] LLM extraction produces valid JSON
- [ ] Error messages are user-friendly
- [ ] CORS and web API endpoints work

## Dependencies and Compatibility Matrix

| Package | Current | Target | Status | Notes |
|---------|---------|--------|--------|-------|
| langchain | 0.3.27 | >=1.2.6,<2.0.0 | ✅ Supported | Major version upgrade |
| langchain-core | 0.3.76 | >=0.3.0,<0.4.0 | ✅ Compatible | Already 0.3.x |
| langchain-community | 0.3.30 | >=0.3.0,<0.4.0 | ⚠️ Check | May need patches |
| langchain-openai | 0.3.33 | >=0.2.0,<0.3.0 | ✅ Compatible | Already compatible |
| langgraph | 0.2.x | >=0.2.60,<0.3.0 | ✅ Compatible | Minor upgrade |
| langchain-mcp-adapters | 0.1.10 | >=0.1.0 | ⚠️ Verify | May need updates |
| pydantic | 2.11.0 | >=2.5.0 | ✅ Compatible | Already v2 |

## Rollback Plan

If critical issues are discovered:
1. Revert `pyproject.toml` changes
2. Restore `uv.lock` from git
3. Run `uv sync --reinstall`
4. Verify functionality returns to baseline

**Rollback Criteria:**
- Critical functionality broken (Pokémon lookup fails)
- Performance degradation > 20%
- External API incompatibility (Tavily, OpenAI)
- Test coverage drops below 90%

## Open Questions
1. Are there any LangChain 1.x features we should adopt beyond minimal migration?
2. Should we migrate to the new LangGraph API simultaneously?
3. Do we need to update MCP adapter implementations?
4. Are there any deprecated Tavily integration patterns to avoid?

## Decision Log
- ✅ Use `from langchain_core.tools import BaseTool` instead of `langchain.tools`
- ✅ Keep Pydantic v2 (already compatible)
- ✅ Update all `langchain_community` imports in single pass
- ✅ Test MCP adapters compatibility before full migration