# 宝可梦Multi-Agent系统架构方案 (V4.0 - 最终版)

---

## 一、 核心思想 (Core Ideology)

我们正在构建一个由**云端大脑驱动、在本地执行、具备自主决策能力的分布式智能系统**。其核心思想是“**分层的智能**”与“**能力的封装**”。

1.  **分层的智能 (Layered Intelligence)**: 系统智能被清晰地划分为三个层级：
    *   **交互与管理层 (主Agent)**: 负责理解用户宏观意图、管理多轮对话的上下文、维持用户体验的流畅性。它是系统的“情商”和“项目经理”。
    *   **策略与决策层 (对战Agent)**: 负责在特定领域（如宝可梦对战）内，基于当前态势进行深度思考和战术决策。它是系统的“专家”和“策略师”。
    *   **执行与探索层 (检索Agent/ReAct Agent)**: 负责解决定义明确的、具体的信息获取任务。它通过自主探索和试错来达成目标。它是系统的“研究员”和“实干家”。

2.  **能力的封装 (Capability Encapsulation)**: 系统中的“能力”被封装为标准化的“工具(Tools)”。Agent本身不包含复杂的业务逻辑代码，而是通过调用工具来完成任务。这种设计使得：
    *   **Agent更纯粹**: Agent的核心职责是“思考”和“决策”（即决定调用哪个工具），而不是“执行”。
    *   **能力可插拔**: 我们可以轻易地增加新工具（例如，一个查询天气影响的工具）来扩展Agent的能力，而无需修改Agent的核心代码。
    *   **逻辑可复用**: `PokemonInfoTool`这个工具可以被任何未来的Agent复用，而不仅仅是检索Agent。

---

## 二、 设计方案 (Design Plan)

我们采用**前后端分离的C/S架构**，后端系统在本地运行，并通过**云端API**调用大语言模型。

### 架构图

```mermaid
graph TD
    subgraph "用户设备 (Client)"
        A[移动端App (React Native/Flutter)]
    end

    subgraph "本地服务器 (Local Server)"
        B[FastAPI Web Server]
        subgraph "Agent层"
            C{主Agent}
            D[宝可梦检索Agent]
            E[宝可梦对战Agent]
        end
        subgraph "工具层"
            F_Agent((PokemonInfoTool ReAct Agent))
            G[BattleLogicTool]
            H[TeamManagementTool]
        end
        subgraph "本地服务/数据"
            I[用户队伍数据 (teams.json)]
            J[pokemon_mcp Server]
        end
    end

    subgraph "云端服务 (Cloud)"
        N[云端LLM厂商 API]
    end
    
    subgraph "互联网 (Internet)"
        K[搜索引擎 API]
        L[宝可梦百科网站]
    end

    %% 连接关系
    A -- "HTTP (RESTful API)" --> B
    B -- "Python函数调用" --> C
    C -- "路由/函数调用" --> D & E & H
    D -- "调用" --> F_Agent
    E -- "调用" --> G
    F_Agent -- "思考" --> N
    F_Agent -- "行动" --> J & K
    C & E -- "思考/对话" --> N
    K -- "搜索" --> L
```
技术栈:
- 前端: React Native / Flutter
- 后端 Web 框架: FastAPI (Python)
- Agent 框架: LangChain (Python)
- 大语言模型: 通过API调用的云端LLM (如OpenAI GPT系列, Anthropic Claude系列)
- 核心工具实现: Python

## 三、 Multi-Agent 实现方案
1. 主Agent (The Conductor) - 功能与方案
- 功能:
    1. 意图路由 (Intent Routing): 作为系统的唯一入口，分析用户输入的自然语言，判断其属于“信息查询”、“队伍管理”还是“发起对战”等宏观意图，并将任务分发给对应的子Agent或工具。
    2. 对话管理 (Dialogue Management): 对于需要多轮交互才能完成的任务（如创建队伍、替换成员），主Agent负责维持对话状态，通过连续的澄清式提问来收集所有必要信息，然后再执行最终操作。
    3. 用户上下文维持: 负责管理用户的全局上下文，如当前正在查看的宝可梦、用户的基本偏好等。
- 实现方案:
    1. 使用LangChain的Router Chains来实现意图路由。主Agent会有一个Prompt，其中描述了各个子Agent或工具能处理的任务类型，LLM根据用户输入来决定最佳路由目标。
    2. 对话管理将通过带有记忆功能的Chain实现。主Agent会接入一个ConversationBufferMemory，使其能够记住之前的对话历史。在处理需要多轮交互的任务时，它会基于历史和当前输入来生成下一步的澄清式问题，直到收集到足够信息为止。
2. 宝可梦检索Agent (The Researcher) - 功能与方案
- 功能:
    1. 任务接收: 从主Agent处接收明确的查询任务，例如“获取皮卡丘的完整信息”。
    2. 工具调用: 它的唯一职责是调用PokemonInfoTool这个强大的工具来完成信息获取任务。它本身不关心信息是如何被获取的。
    3. 结果格式化: 将PokemonInfoTool返回的结构化JSON数据，根据用户的原始问题，整理成一段通顺、易读的自然语言回复。
- 实现方案:
    1. 这将是一个相对简单的Agent。其核心是一个调用PokemonInfoTool的函数。
    2. 在接收到任务后，它会解析出需要查询的宝可梦名称，调用PokemonInfoTool(pokemon_name=...)。
    3. 拿到返回的JSON后，它会使用一个格式化Prompt调用LLM，将JSON数据“翻译”成自然语言，然后返回给主Agent。
3. 宝可梦对战Agent (The Strategist) - 功能与方案
- 功能:
    1. 对战初始化: 接收双方的队伍配置，并调用LLM进行“出战策略思考”，为AI方选择最佳的出战宝可梦。
    2. 回合管理: 管理对战的每一个回合，包括接收用户操作、决策AI操作、结算回合结果。
    3. AI决策: 在每个AI行动的回合，调用LLM进行“回合战术思考”，基于当前战场态势（HP、属性、状态等）选择最优的招式。
    4. 状态更新与播报: 调用BattleLogicTool计算伤害和结果，更新战场状态，并生成生动的战报解说。
- 实现方案:
    1. 该Agent将以一个状态机的形式存在，其状态包括SELECTING_POKEMON, AWAITING_INPUT, CALCULATING_RESULT, BATTLE_END等。
    2. 在SELECTING_POKEMON和AWAITING_INPUT（轮到AI行动时）这两个状态下，它会暂停，并构造详细的、包含战场数据的Prompt来调用云端LLM，以获取策略和战术决策。
    3. 它会频繁调用BattleLogicTool（一个纯Python实现的、包含游戏规则和伤害公式的工具）来执行确定性的计算。
## 四、 Agent之间的通信方案及协议
本架构中，Agent之间不进行直接的、点对点的自由对话。它们遵循一套更结构化的、以主Agent为中心的调用与回调机制。
- 协议: 可以理解为内部函数调用 (Internal Function Calls)。当一个Agent需要另一个Agent或工具的能力时，它就像调用一个本地Python函数一样调用它。FastAPI将外部的HTTP请求转换为了第一次内部函数调用。
- 通信模式:
    1. 用户 -> 主Agent (HTTP API):
        * 协议: RESTful HTTP/HTTPS。
        * 流程: 移动App将用户操作（如发送消息）打包成JSON，通过POST请求发送到FastAPI后端的/chat或/action端点。
    2. 主Agent -> 子Agent/工具 (同步函数调用):
        * 协议: Python函数调用。
        * 流程: 主Agent在分析完用户意图后，直接在代码中调用对应子Agent或工具的执行方法，例如 retrieval_agent.run(task=...) 或 team_tool.add_pokemon(...)。这是一个同步阻塞调用，主Agent会等待调用的完成和返回结果。
    3. 子Agent -> 工具 (同步函数调用):
        * 协议: Python函数调用。
        * 流程: 与上一步类似。例如，检索Agent调用pokemon_info_tool.run(...)。
    4. Agent -> LLM (远程HTTP API):
        * 协议: RESTful HTTP/HTTPS。
        * 流程: 任何Agent（主Agent、对战Agent、或PokemonInfoTool内部的ReAct Agent）需要“思考”时，都会通过LangChain的LLM封装器，向云端LLM厂商的API端点发起一个安全的HTTP请求。这是一个同步的网络I/O操作。
总结: 这种以主Agent为核心的星型通信模式，避免了多Agent之间自由通信可能导致的混乱和不可预测性，使得整个系统的行为更加稳定、可控和易于调试。信息流清晰地从用户输入开始，经过各层Agent和工具的处理，最终形成输出返回给用户。