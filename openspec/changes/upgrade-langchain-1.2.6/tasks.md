## 1. Preparation and Planning

### 1.1 Codebase Analysis
- [ ] 1.1.1 Run `rg -n "from langchain|import langchain" src/` to identify all LangChain usage
- [ ] 1.1.2 Create inventory of affected files and import patterns
- [ ] 1.1.3 Identify deprecated APIs currently in use
- [ ] 1.1.4 Review LangChain 1.2.6 migration guide and breaking changes documentation
- [ ] 1.1.5 Check compatibility of all dependent packages (langchain-mcp-adapters, etc.)

### 1.2 Environment Setup
- [ ] 1.2.1 Create feature branch `feature/upgrade-langchain-1.2.6`
- [ ] 1.2.2 Backup current `uv.lock` file
- [ ] 1.2.3 Set up test environment with current version as baseline
- [ ] 1.2.4 Run full test suite and document baseline metrics (pass rate, coverage)

## 2. Dependency Updates

### 2.1 Update pyproject.toml
- [ ] 2.1.1 Update `langchain>=0.1.0` to `langchain>=1.2.6,<2.0.0`
- [ ] 2.1.2 Update `langchain-core>=0.1.0` to `langchain-core>=0.3.0,<0.4.0`
- [ ] 2.1.3 Update `langgraph>=0.2.0` to `langgraph>=0.2.60,<0.3.0`
- [ ] 2.1.4 Verify `langchain-community>=0.3.0` compatibility
- [ ] 2.1.5 Update `langchain-openai>=0.3.0` pointer
- [ ] 2.1.6 Document all version changes in commit message

### 2.2 Lock File Generation
- [ ] 2.2.1 Run `uv lock --upgrade-package langchain` to update lock file
- [ ] 2.2.2 Verify all transitive dependencies resolve correctly
- [ ] 2.2.3 Check for any dependency conflicts
- [ ] 2.2.4 Run `uv sync` to install updated packages
- [ ] 2.2.5 Verify installed versions with `uv pip list | grep langchain`

## 3. Core Tool Refactoring

### 3.1 PokemonInfoTool Updates (Critical Path)
- [ ] 3.1.1 Update import: `from langchain_core.tools import BaseTool`
- [ ] 3.1.2 Refactor tool initialization pattern for 1.x
- [ ] 3.1.3 Update `args_schema` usage if API changed
- [ ] 3.1.4 Update `_run` method signature and type hints
- [ ] 3.1.5 Test tool in isolation with sample Pokémon queries
- [ ] 3.1.6 Verify error handling works correctly

### 3.2 Import Path Updates
- [ ] 3.2.1 Update all `langchain.tools` imports to `langchain_core.tools`
- [ ] 3.2.2 Update `langchain_community.tools.tavily_search` imports
- [ ] 3.2.3 Update `langchain_core.output_parsers` imports
- [ ] 3.2.4 Update `langchain_core.prompts` imports
- [ ] 3.2.5 Update `langchain_community.document_loaders` imports

### 3.3 Web Search Tool Updates
- [ ] 3.3.1 Update TavilySearchResults initialization
- [ ] 3.3.2 Verify search parameters still supported
- [ ] 3.3.3 Test timeout and error handling
- [ ] 3.3.4 Verify search results format unchanged

### 3.4 Web Loader Updates
- [ ] 3.4.1 Update WebBaseLoader usage if API changed
- [ ] 3.4.2 Test loader with pokemon wiki URLs
- [ ] 3.4.3 Verify content extraction still works
- [ ] 3.4.4 Check for any parsing changes

## 4. Agent and Chain Updates

### 4.1 Retrieval Agent Updates
- [ ] 4.1.1 Check agent creation pattern with `langgraph`
- [ ] 4.1.2 Update agent configuration if needed
- [ ] 4.1.3 Test agent tool binding
- [ ] 4.1.4 Verify agent execution flow

### 4.2 LLM Integration Updates
- [ ] 4.2.1 Test ChatOpenAI initialization with custom base_url
- [ ] 4.2.2 Verify timeout configuration still works
- [ ] 4.2.3 Check model parameter compatibility
- [ ] 4.2.4 Verify streaming if used

### 4.3 Chain Updates
- [ ] 4.3.1 Review `langchain_core` chain usage
- [ ] 4.3.2 Update to new `Runnable` interface if needed
- [ ] 4.3.3 Verify prompt templates still work
- [ ] 4.3.4 Check output parsers compatibility

## 5. Testing and Validation

### 5.1 Unit Test Updates
- [ ] 5.1.1 Update test imports to match new module paths
- [ ] 5.1.2 Fix any mocking issues with new API
- [ ] 5.1.3 Update test assertions if needed
- [ ] 5.1.4 Ensure all test files pass: `pytest tests/ -v`

### 5.2 Integration Testing
- [ ] 5.2.1 Test PokemonInfoTool end-to-end with real API calls
- [ ] 5.2.2 Verify tool integration with agents
- [ ] 5.2.3 Test error scenarios (timeout, not found, API errors)
- [ ] 5.2.4 Verify MCP adapter compatibility
- [ ] 5.2.5 Test batch operations if implemented

### 5.3 Performance Testing
- [ ] 5.3.1 Measure tool execution time for comparison
- [ ] 5.3.2 Check memory usage of updated components
- [ ] 5.3.3 Verify no performance regression > 10%
- [ ] 5.3.4 Test concurrent tool execution

### 5.4 Code Quality Checks
- [ ] 5.4.1 Run `mypy src/` to verify type hints
- [ ] 5.4.2 Run `flake8 src/` to check code style
- [ ] 5.4.3 Run `black src/` for code formatting
- [ ] 5.4.4 Run `isort src/` for import sorting
- [ ] 5.4.5 Verify no new linting errors introduced

## 6. Documentation Updates

### 6.1 Code Documentation
- [ ] 6.1.1 Update module docstrings with new LangChain version
- [ ] 6.1.2 Add comments for any non-obvious migration decisions
- [ ] 6.1.3 Update type hints documentation if changed
- [ ] 6.1.4 Document any new patterns for future development

### 6.2 README Updates
- [ ] 6.2.1 Update version requirement documentation
- [ ] 6.2.2 Add migration notes for developers
- [ ] 6.2.3 Update API usage examples if needed
- [ ] 6.2.4 Document any breaking changes for users

### 6.3 CHANGELOG Entry
- [ ] 6.3.1 Create CHANGELOG entry for this upgrade
- [ ] 6.3.2 List all breaking changes
- [ ] 6.3.3 List all files modified
- [ ] 6.3.4 Add migration guide notes

## 7. Final Validation

### 7.1 Pre-Merge Checklist
- [ ] 7.1.1 All tests passing (unit and integration)
- [ ] 7.1.2 Code coverage maintained at >= 90%
- [ ] 7.1.3 Type checking passes with mypy
- [ ] 7.1.4 Linting passes with no errors
- [ ] 7.1.5 Code formatting consistent with black and isort
- [ ] 7.1.6 Manual testing completed successfully
- [ ] 7.1.7 Performance regression < 10%

### 7.2 PR Preparation
- [ ] 7.2.1 Rebase branch on latest main
- [ ] 7.2.2 Squash commits if needed
- [ ] 7.2.3 Write comprehensive PR description
- [ ] 7.2.4 Add screenshots of test results
- [ ] 7.2.5 Request code review from team

### 7.3 Deployment Preparation
- [ ] 7.3.1 Document any deployment considerations
- [ ] 7.3.2 Verify environment variables still work
- [ ] 7.3.3 Check production dependency installation
- [ ] 7.3.4 Prepare rollback plan if needed

## 8. Cross-Check with Proposal Requirements

### 8.1 Proposal Compliance
- [ ] 8.1.1 Verify all requirements from specs/tooling/spec.md are implemented
- [ ] 8.1.2 Check all modified requirements are properly updated
- [ ] 8.1.3 Ensure no deprecated patterns remain
- [ ] 8.1.4 Confirm all scenarios pass testing

### 8.2 Documentation Review
- [ ] 8.2.1 Review proposal.md for accuracy post-implementation
- [ ] 8.2.2 Review design.md for consistency with actual changes
- [ ] 8.2.3 Ensure tasks.md completion status reflects reality
- [ ] 8.2.4 Update any documentation if implementation differs from plan