# Project Context

## Purpose
Build a real-time web-searching and battle-capable Pokémon Multi-Agent System. The system enables users to:
- Query Pokémon information from the internet in real-time
- Build Pokémon teams with strategic composition
- Engage in battles against AI opponents
- Have natural language conversations about Pokémon

## Tech Stack
- **Python** (3.11+) - Primary language
- **FastAPI** - Web framework for building APIs
- **LangChain** - Framework for building LLM applications
- **OpenAI GPT-4** - LLM for information extraction and conversation
- **Tavily Search API** - Web search for Pokémon information
- **BeautifulSoup4** - Web scraping for content extraction
- **Uvicorn** - ASGI server for FastAPI
- **pytest** - Testing framework

## Project Conventions

### Code Style
- Follow PEP 8 for Python code style
- Use type hints for all function signatures
- Use snake_case for functions and variables
- Use PascalCase for class names
- Keep functions focused and under 50 lines when possible
- Add docstrings for complex functions explaining parameters and return values
- English for code/comments, Chinese for user-facing documentation

### Architecture Patterns
- **Multi-Agent Architecture**: Separate agents for different capabilities (retrieval, battle, main coordination)
- **Tool-Based Design**: LangChain tools for external API interactions
- **Async/Await**: Use async patterns for I/O-bound operations
- **Service Layer**: API layer separate from agent logic
- **Data Models**: Pydantic models for structured data validation

### Testing Strategy
- Unit tests for individual components and tools
- Integration tests for API endpoints
- Test fixtures for common Pokémon data
- Mock external APIs in tests
- Test error handling and edge cases
- Run tests before committing changes

### Git Workflow
- Main branch: `main` (used for PRs)
- Create feature branches for new work
- Make small, focused commits
- Write descriptive commit messages
- Create PR for review before merging
- Co-author commits with Claude when assisted

## Domain Context

### Pokémon Domain Knowledge
- **Pokémon Data**: Types, stats, abilities, moves, evolutions
- **Battle Mechanics**: Type effectiveness, STAB (Same-Type Attack Bonus), stats calculation
- **Teams**: Strategic composition with 6 Pokémon per team
- **Gens**: Different generations have different available Pokémon and mechanics
- **Popular Resources**: wiki.52poke.com (Chinese), Bulbapedia (English), Serebii

### Agent Responsibilities
- **Retrieval Agent**: Searches web for Pokémon info, processes with LLM, returns structured data
- **Battle Agent**: Manages battle logic, team building, strategy
- **Main Agent**: Routes requests, coordinates between agents, handles user conversation

### Multi-Agent Flow
1. User asks about a Pokémon
2. Main Agent determines if retrieval needed
3. Retrieval Agent uses PokemonInfoTool to search and extract info
4. Information stored/returned in structured format
5. Battle Agent can use this info for team building and battles

## Important Constraints
- **API Keys Required**: Must have OPENAI_API_KEY and TAVILY_API_KEY
- **Rate Limits**: Respect external API rate limits (Tavily, OpenAI)
- **Timeout Handling**: All external calls must have timeouts (30s search, 20s load, 45s LLM)
- **Error Handling**: Graceful degradation when APIs fail
- **Chinese Focus**: Primary user base expects Chinese language support

## External Dependencies
- **Tavily Search API** - Web search for Pokémon information
- **OpenAI API** - GPT-4 for information extraction and conversation
- **Pokémon Websites** - wiki.52poke.com, Bulbapedia, Serebii for data
- **GitHub** - Code hosting and version control
