# Pokemon Agent API 使用文档

## 概述

Pokemon Agent API 提供两种宝可梦信息检索方式，支持中英文双语显示，所有数据均从权威来源实时获取。

## 环境要求

- Python >= 3.11
- 必需环境变量：
  - `ROUTER_API_KEY`: OpenRouter API 密钥
  - `TAVILY_API_KEY`: Tavily 搜索 API 密钥

## API 端点

### 1. 健康检查

**GET** `/health`

检查API服务状态。

**响应示例：**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "0.1.0"
}
```

---

### 2. 直接检索模式

**POST** `/api/v1/pokemon/info`

使用 PokemonInfoTool 直接检索宝可梦信息，适合快速获取基础数据。

#### 请求参数

```json
{
  "pokemon_name": "Pikachu"
}
```

#### 响应格式

成功响应（200）：
```json
{
  "pokemon_name": "Pikachu",
  "source_url": "https://wiki.52poke.com/wiki/%E7%9A%AE%E5%8D%A1%E4%B8%98",
  "extraction_timestamp": "{\"timestamp\": \"2024-01-15T10:30:00Z\"}",
  "data": {
    "basic_info": {
      "name": "皮卡丘 Pikachu",
      "national_dex_number": "025",
      "types": ["电 Electric"],
      "abilities": ["静电 Static", "避雷针 Lightning Rod"],
      ...
    },
    "battle_stats": {
      "hp": "35 生命值 HP",
      "attack": "55 攻击 Attack",
      ...
    },
    "evolution_chain": {
      "evolution_stage": "基础形态 Basic Stage",
      "next_form": "雷丘 Raichu",
      ...
    }
  }
}
```

#### 特点

- **快速**：通常在10-30秒内完成
- **直接**：固定工作流程，无智能决策
- **轻量**：适合获取基础信息

#### 工作流程

1. 搜索宝可梦信息（Tavily API）
2. 选择最佳来源（优先wiki.52poke.com）
3. 抓取网页内容
4. LLM提取结构化数据

---

### 3. 智能Agent模式

**POST** `/api/v1/pokemon/react-info`

使用 PokemonReactTool 通过 ReAct（推理-行动-观察）模式智能收集宝可梦信息。

#### 请求参数

```json
{
  "pokemon_name": "Charizard"
}
```

#### 响应格式

成功响应（200）：
```json
{
  "success": true,
  "pokemon_name": "Charizard",
  "mode": "react_agent",
  "final_answer": {
    "basic_info": {
      "name": "喷火龙 Charizard",
      ...
    },
    "battle_stats": {
      ...
    }
  },
  "agent_output": "...agent reasoning process..."
}
```

#### 特点

- **智能**：自主思考，动态选择工具
- **全面**：收集更完整的信息
- **容错**：工具失败时自动切换策略
- **耗时**：通常需要30-90秒

#### 工作流程

1. **思考**：分析已获取信息，确定信息缺口
2. **行动**：选择合适工具（MCP工具/网络搜索/内容提取）
3. **观察**：评估工具返回结果质量
4. **重复**：继续循环直到信息充分

#### 信息充分标准

当满足以下条件时，Agent认为信息收集充分：
- ✅ 基本信息完整（名称、属性、特性）
- ✅ 战斗数据完整（六维基础数值）
- ✅ 进化链清晰（进化关系和条件）
- ✅ 游戏背景明确（首次出现和版本信息）
- ✅ 数据一致性（不同来源信息不冲突）

---

## 数据模型说明

### 宝可梦基础信息 (basic_info)

| 字段 | 说明 | 示例 |
|------|------|------|
| name | 宝可梦名称（中英） | "皮卡丘 Pikachu" |
| national_dex_number | 全国图鉴编号 | "025" |
| types | 属性列表 | ["电 Electric"] |
| species | 分类 | "鼠宝可梦 Mouse Pokémon" |
| height | 身高 | "0.4米 0.4m" |
| weight | 体重 | "6.0公斤 6.0kg" |
| abilities | 特性列表 | ["静电 Static", "避雷针 Lightning Rod"] |
| gender_ratio | 性别比例 | "50%雄性 50% Male, 50%雌性 50% Female" |
| catch_rate | 捕获率 | "190" |
| color | 颜色 | "黄色 Yellow" |
| egg_groups | 蛋群 | ["陆上蛋群 Field Group"] |
| habitat | 栖息地 | "森林 Forest Habitat" |

### 战斗数据 (battle_stats)

| 字段 | 说明 | 示例 |
|------|------|------|
| hp | 生命值 | "35 生命值 HP" |
| attack | 攻击 | "55 攻击 Attack" |
| defense | 防御 | "40 防御 Defense" |
| special_attack | 特攻 | "50 特攻 Special Attack" |
| special_defense | 特防 | "50 特防 Special Defense" |
| speed | 速度 | "90 速度 Speed" |
| base_stat_total | 种族值总和 | "320 总和 Total" |
| effort_values | 努力值 | "速度 Speed: 2 努力值 EV" |

### 进化链 (evolution_chain)

| 字段 | 说明 | 示例 |
|------|------|------|
| evolution_stage | 进化阶段 | "基础形态 Basic Stage" |
| evolution_methods | 进化方法 | "使用雷之石进化 Evolve using Thunder Stone" |
| previous_form | 前形态 | "皮丘 Pichu" |
| next_form | 后形态 | "雷丘 Raichu" |

### 游戏信息 (game_info)

| 字段 | 说明 | 示例 |
|------|------|------|
| generation_introduced | 首次世代 | "第一代 Generation I" |
| version_debut | 首次版本 | "红/绿/蓝版本 Red/Green/Blue Version" |
| location_methods | 捕获地点 | "常青森林 Viridian Forest" |

---

## 错误处理

### 错误响应格式

```json
{
  "error": "错误描述",
  "details": "详细说明（可选）",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 常见错误码

| HTTP状态码 | 错误类型 | 说明 |
|------------|----------|------|
| 400 | Bad Request | 请求参数错误（如宝可梦名称过短） |
| 408 | Request Timeout | 请求超时（搜索/抓取/LLM处理超时） |
| 429 | Too Many Requests | API限流 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 外部服务不可用（如Tavily API） |

---

## 使用建议

### 何时使用直接检索模式？

✅ 推荐场景：
- 需要快速获取宝可梦基础信息
- 对响应时间要求高
- 只需要基本信息（属性、特性、基础数值）

❌ 不推荐场景：
- 需要非常详细的信息
- 需要验证数据完整性
- 处理稀有或新发布宝可梦

### 何时使用智能Agent模式？

✅ 推荐场景：
- 需要全面、详细的宝可梦数据
- 可以接受较长等待时间
- 需要信息质量保障
- 处理复杂查询或稀有宝可梦

❌ 不推荐场景：
- 需要快速响应（如实时应用）
- 简单的查询需求
- 系统资源有限

---

## 性能指标

### 直接检索模式

- **平均响应时间**：15-25秒
- **搜索超时**：30秒
- **网页加载超时**：20秒
- **LLM处理超时**：45秒

### 智能Agent模式

- **平均响应时间**：45-75秒
- **最大迭代次数**：6次
- **最大执行时间**：90秒
- **单次工具调用超时**：30-45秒

---

## 示例代码

### Python 使用示例

```python
import requests
import json

API_BASE_URL = "http://localhost:8000"

def get_pokemon_info(pokemon_name, mode="direct"):
    """获取宝可梦信息"""

    endpoint = "/api/v1/pokemon/info" if mode == "direct" else "/api/v1/pokemon/react-info"

    response = requests.post(
        f"{API_BASE_URL}{endpoint}",
        json={"pokemon_name": pokemon_name},
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# 使用直接模式
pikachu_data = get_pokemon_info("Pikachu", mode="direct")
if pikachu_data:
    print(f"皮卡丘属性: {pikachu_data['data']['basic_info']['types']}")
    print(f"种族值总和: {pikachu_data['data']['battle_stats']['base_stat_total']}")

# 使用智能Agent模式
charizard_data = get_pokemon_info("Charizard", mode="react")
if charizard_data and charizard_data['success']:
    print(f"喷火龙特性: {charizard_data['final_answer']['basic_info']['abilities']}")
```

### JavaScript/Node.js 使用示例

```javascript
const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000';

async function getPokemonInfo(pokemonName, mode = 'direct') {
  const endpoint = mode === 'direct'
    ? '/api/v1/pokemon/info'
    : '/api/v1/pokemon/react-info';

  try {
    const response = await axios.post(`${API_BASE_URL}${endpoint}`, {
      pokemon_name: pokemonName
    }, {
      headers: { 'Content-Type': 'application/json' }
    });

    return response.data;
  } catch (error) {
    console.error(`Error: ${error.response?.status}`);
    console.error(error.response?.data);
    return null;
  }
}

// 使用示例
(async () => {
  // 获取皮卡丘信息
  const pikachuData = await getPokemonInfo('Pikachu', 'direct');
  if (pikachuData) {
    console.log(`皮卡丘HP: ${pikachuData.data.battle_stats.hp}`);
  }

  // 使用智能Agent模式获取喷火龙信息
  const charizardData = await getPokemonInfo('Charizard', 'react');
  if (charizardData && charizardData.success) {
    console.log(`喷火龙速度: ${charizardData.final_answer.battle_stats.speed}`);
  }
})();
```

---

## 高级功能

### 1. 批量查询

```python
# 批量查询多个宝可梦
pokemon_list = ["Pikachu", "Charizard", "Blastoise", "Venusaur"]

results = []
for pokemon in pokemon_list:
    # 对稀有宝可梦使用智能Agent模式
    mode = "react" if pokemon in ["Charizard"] else "direct"
    data = get_pokemon_info(pokemon, mode=mode)
    if data:
        results.append(data)

print(f"成功查询 {len(results)} 个宝可梦")
```

### 2. 数据缓存建议

```python
import sqlite3
import json
from datetime import datetime, timedelta

class PokemonCache:
    def __init__(self, db_path="pokemon_cache.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS pokemon_cache (
                name TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

    def get(self, pokemon_name):
        """从缓存获取数据（有效期24小时）"""
        cursor = self.conn.execute(
            "SELECT data, timestamp FROM pokemon_cache WHERE name = ?",
            (pokemon_name.lower(),)
        )
        result = cursor.fetchone()

        if result:
            data, timestamp = result
            cache_time = datetime.fromisoformat(timestamp)
            if datetime.now() - cache_time < timedelta(hours=24):
                return json.loads(data)

        return None

    def set(self, pokemon_name, data):
        """保存数据到缓存"""
        self.conn.execute(
            "REPLACE INTO pokemon_cache (name, data, timestamp) VALUES (?, ?, ?)",
            (pokemon_name.lower(), json.dumps(data), datetime.now().isoformat())
        )
        self.conn.commit()

# 使用缓存
 cache = PokemonCache()

def get_pokemon_with_cache(pokemon_name, mode="direct"):
    # 先查缓存
    cached = cache.get(pokemon_name)
    if cached:
        print(f"从缓存获取 {pokemon_name} 数据")
        return cached

    # 缓存未命中，调用API
    data = get_pokemon_info(pokemon_name, mode)
    if data:
        cache.set(pokemon_name, data)

    return data
```

---

## 限制与注意事项

### 1. API 限制

- 请求频率限制：根据 Tavily API 和 OpenRouter API 的配额
- 单次请求超时：60-90秒（取决于模式）
- 支持的最大请求大小：10 MB

### 2. 数据限制

- 数据来源于公开网络，可能不完全准确
- 新发布宝可梦信息可能不完整
- 部分稀有宝可梦信息可能难以获取
- 图片URL可能失效，需要额外处理

### 3. 最佳实践

- ✅ 对已知宝可梦使用直接模式
- ✅ 实现缓存机制减少API调用
- ✅ 处理超时和错误情况
- ✅ 对批量操作添加延迟（rate limiting）
- ❌ 不要频繁请求同一宝可梦
- ❌ 不要在生产环境使用同步阻塞调用

---

## 故障排除

### 问题1: 超时错误（408）

**原因**：
- 网络搜索耗时过长
- 目标网站加载缓慢
- LLM处理复杂内容

**解决方案**：
- 检查网络连接
- 稍后重试
- 使用智能Agent模式（有更好的重试机制）

### 问题2: "No search results found"

**原因**：
- 宝可梦名称拼写错误
- 使用了非标准名称
- 稀有宝可梦信息不足

**解决方案**：
- 验证宝可梦名称拼写
- 尝试使用英文名称
- 使用智能Agent模式

### 问题3: "Insufficient content loaded"

**原因**：
- 目标网站结构变化
- 网页访问受限
- 内容被反爬虫机制拦截

**解决方案**：
- 使用智能Agent模式（支持备用策略）
- 检查目标网站可用性
- 尝试其他宝可梦验证系统状态

---

## 更新日志

### v0.1.0 (2024-01-15)

- ✅ 初始化 OpenAPI 规范
- ✅ 实现 PokemonInfoTool API
- ✅ 实现 PokemonReactTool API
- ✅ 添加完整的数据模型文档
- ✅ 提供多语言示例代码

---

## 支持与反馈

- GitHub Issues: https://github.com/your-org/pokemon-agent-backend/issues
- 项目文档: https://pokemon-agent-backend.readthedocs.io
- API 状态: https://status.pokemon-agent.com

---

## 许可证

MIT License - 详见项目根目录 LICENSE 文件
