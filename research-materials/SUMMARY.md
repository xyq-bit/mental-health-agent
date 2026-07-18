# 优质资源总结：可为本项目服务的要点

> 整理时间：2026-07-16
> 每份资源提取可落地的改进点、可引用的学术依据、可参考的架构设计。

---

## 一、LangGraph Persistence 官方文档

**来源**：`01-langgraph-persistence-docs.md`
**定位**：LangGraph 持久化层的权威参考

### 核心架构：Checkpointer + Store 双层记忆

| 层 | 组件 | 职责 | 生命周期 |
|---|---|---|---|
| **短期记忆** | Checkpointer | Thread 内状态保存、断点恢复、会话连续性 | 单次会话 |
| **长期记忆** | Store (BaseStore) | 跨 Thread 的用户画像、偏好、历史事实 | 跨会话持久 |

### 对你项目的改进点

1. **你现在的架构混用问题**：`long_term_summary` 字符串存在 State 里由 Checkpointer 管理，属于把长期记忆放进了短期记忆的槽位。应改为：
   - `SqliteSaver`（Checkpointer）→ 继续管当前会话的 `messages`、`q_idx`、`total_score` 等
   - `InMemoryStore` 或 `AsyncPostgresStore`（Store）→ 管用户画像、长期记忆摘要、跨会话的评估历史

2. **Store API 使用模式**：
   ```python
   from langgraph.store.memory import InMemoryStore
   store = InMemoryStore()
   # 存用户画像
   store.put(("user_profile", user_id), "profile", {...})
   # 取用户画像
   profile = store.get(("user_profile", user_id), "profile")
   # 语义搜索（需配置 embedding）
   results = store.search(("memories", user_id), query="抑郁史")
   ```

3. **关键文件更新**：在 `1graph.py` 中，`compile()` 时同时传入 `checkpointer` 和 `store` 两个参数。

---

## 二、Persistent Agent Memory in LangGraph（Focused.io）

**来源**：`02-persistent-agent-memory-langgraph.md`
**作者**：Austin Vance, Focused Labs
**日期**：2026-05-28

### 核心观点

1. **三层记忆模型**：
   - **Working Memory**（工作记忆）→ Checkpointer 中的 messages 列表
   - **Episodic Memory**（情节记忆）→ Store 中的语义搜索
   - **Semantic Memory**（语义记忆）→ Store 中的结构化知识

2. **确定性 Key 策略**：用 `"user_plan"` 而非 UUID 作为 Store 的 key，确保更新覆盖旧数据不发生重复。这对你的用户画像管理非常关键。

### 对你项目的改进点

- 你的"测评摘要"字段 `assessment_result` 应该放入 Store 而非 State
- 用户多次测评的历史应该累积在 Store 中，可以用 `store.search()` 做语义检索："该用户上次 PHQ-9 分数趋势如何？"
- 实现伪代码：
  ```python
  # 测评结束时
  store.put(
      ("assessments", username),
      f"phq9_{timestamp}",
      {"total_score": total_score, "risk_level": risk_level, "date": date}
  )
  # 下次测评时检索历史
  history = store.search(("assessments", username), query="PHQ-9 scores")
  ```

---

## 三、LangMem SDK — 可直接替代你的手写压缩节点

**来源**：`03-langmem-docs.md`、`04-langmem-launch-blog.md`、`09-langmem-readme.md`
**安装**：`pip install -U langmem`

### 和你项目最相关的三个功能

#### 1. `create_memory_store_manager`（Background 模式）

**直接替代你的 `node_memory_compress`**。它在后台自动提取、整合、更新 Agent 知识，而非你的"超过 N 条才触发"的被动策略。

```python
from langmem import create_memory_store_manager

manager = create_memory_store_manager(
    "deepseek:deepseek-chat",  # 可以用 DeepSeek！
    store=store,
    namespace=("memories", username),
)
# 对话结束后异步调用（不阻塞用户响应）
await manager.aturn(
    {"messages": session_messages},
    after="all",
)
```

#### 2. `create_manage_memory_tool` + `create_search_memory_tool`（Hot-path 模式）

给 Agent 添加"主动记忆管理"能力——Agent 自己决定何时存、何时查。心理咨询场景下，Agent 可以在用户提到重要信息（如"我上周开始吃安眠药"）时主动调用存储工具。

```python
from langmem import create_manage_memory_tool, create_search_memory_tool

tools = [
    create_manage_memory_tool(namespace=("memories",)),
    create_search_memory_tool(namespace=("memories",)),
]
```

#### 3. Prompt Optimization（LangMem 独有，进阶功能）

自动优化 Agent 的 System Prompt，从对话反馈中学习。对你的场景：可以让 It 从多次测评对话中自动发现更有效的共情话术。

### 对你的改进优先级

| 功能 | 价值 | 操作 |
|---|---|---|
| Background memory manager | 替代 `node_memory_compress` | `pip install langmem` → 替换压缩节点 |
| Memory tools (hot-path) | Agent 主动记忆 | 添加到你的 LangGraph agent tools 列表 |
| Prompt optimization | 进阶，可暂缓 | 先跑通基础记忆，后续迭代 |

> ⚠️ 注意：LangMem 默认用 Anthropic 模型。但你在 `create_memory_store_manager` 时可以传 `"deepseek:deepseek-chat"` 来用 DeepSeek。需要验证兼容性。

---

## 四、LangGraph State Management 生产部署（AlterSquare）

**来源**：`05-langgraph-state-management.md`
**作者**：Taher Pardawala
**日期**：2026-04-24

### 对你当前架构的直接影响

#### 1. Checkpointer 选择矩阵

| 场景 | 你的现状 | 建议 |
|---|---|---|
| 单机 CLI 开发 | ✅ `SqliteSaver` | 维持现状，够用 |
| Gradio Web 部署 | ⚠️ 多用户同时访问 | 考虑 `AsyncPostgresSaver` |
| 毕设演示 | ✅ 单用户 | `SqliteSaver` 完全够用 |

#### 2. 你代码中的潜在问题

**消息列表无限增长** → 你的 `messages` 没有硬上限。文章建议用 `trim_messages` 或自定义 reducer `return merged[-50:]`。你目前只在 > 100 条时触发压缩，但中间的状态已经膨胀。

**具体修复建议**：在你的 `append_messages` reducer 中加硬上限：
```python
def append_messages(old: List[dict], new: List[dict]) -> List[dict]:
    if len(new) > 0 and new[0].get("__reset__"):
        return new[1:]
    return (old + new)[-200:]  # 硬上限：最多保留最近 200 条
```

#### 3. Schema 版本化

你当前没有 `schema_version` 字段。建议从现在开始加，避免将来毕设改数据结构时破坏已有用户数据：
```python
class AgentState(TypedDict):
    schema_version: int  # 加这一行，当前值=1
    # ... 其余字段
```

#### 4. 检查点策略

每轮对话都存 checkpoint 可能导致数据膨胀。文章建议用 `checkpoint_during` 标记跳过不必要的节点。你可以在 `node_question`（仅发问不改变数据）时跳过 checkpoint。

---

## 五、HopeBot 论文 —— 最直接的学术依据

**来源**：`06-hopebot-arxiv.md`、`06-hopebot-paper.pdf`
**标题**：Development and Evaluation of HopeBot: an LLM-based chatbot for structured and interactive PHQ-9 depression screening
**作者**：Zhijun Guo, Alvina Lai, Julia Ive 等
**日期**：2025-07（v1），2026-01（v2）

### 关键研究数据（毕设可直接引用）

| 指标 | 数值 | 意义 |
|---|---|---|
| 样本量 | **132 名成年人**（英国+中国） | 跨文化验证 |
| ICC（组内相关系数） | **0.91** | 聊天机器人与自填问卷得分高度一致 |
| 完全一致率 | **45%** | 近一半用户两种方式得分完全相同 |
| 用户信任度 | **71% 更信任聊天机器人** | 75 名反馈者中多数偏好机器人版本 |
| 舒适度评分 | **8.4/10** | 用户感到舒适 |
| 声音清晰度 | **7.7/10** | 表达足够清晰 |
| 敏感话题处理 | **7.6/10** | 处理敏感话题的能力 |
| 推荐意愿 | **87.1%** | 愿意重新使用或推荐 |

### HopeBot 的技术方案 vs 你的方案

| 特性 | HopeBot | 你的项目 |
|---|---|---|
| LLM 后端 | 通用 LLM（未指定具体模型） | DeepSeek-Chat |
| PHQ-9 管理 | RAG + 实时澄清 | LCEL Chain / 独立打分节点 |
| 交互模式 | **语音**（voice-based） | 文本（Gradio Chatbot） |
| 评估方法 | 受控实验（within-subject） | 无正式评估 |
| 危机处理 | 未在摘要中详述 | Q9 单独触发预警，硬编码文案 |

### 对你的改进点

1. **毕设 Related Work**：HopeBot 做的是几乎和你一模一样的事（LLM 驱动的 PHQ-9），除了它是语音交互。这是你 Related Work 章节最重要的引用。

2. **评估方法借鉴**：他们在 132 人上做了 within-subject 实验（同一人先自填 PHQ-9，再用 HopeBot）。你的毕设可以采用同样的设计，比如找 20-30 名志愿者做同样对比，报 ICC 值。ICC = 0.91 是你评估时的参考基线。

3. **RAG + 实时澄清**：他们的 PHQ-9 流程用了 RAG 来增强解释性指导，并用"实时澄清"处理模糊回答。你目前如果模型提取 `得分:` 失败就直接默认为 0——可以借鉴 HopeBot 的澄清策略：当用户回答太模糊时，追问一次"你是说大概几天有这种情况？"而非直接判 0。

4. **信任因素分析**：71% 用户更信任机器人的原因是"结构更清晰、有解释性指导、支持性语气"。你可以在自由对话阶段的 system prompt 里强化这三点（你的 system prompt 当前只有共情引导，缺少结构化解释）。

---

## 六、MoPHES 论文 —— 评估与对话分离的架构

**来源**：`07-mophes-arxiv.md`、`07-mophes-paper.pdf`、`10-mophes-readme.md`
**标题**：MoPHES: Leveraging on-device LLMs as Agent for Mobile Psychological Health Evaluation and Support
**作者**：Xun Wei, Pukai Zhou, Zeyu Wang
**日期**：2025-10-17

### 核心架构：双模型分离

```
用户输入 → [评估 LLM] → 心理状态标签（抑郁/焦虑严重度 0-3）
         → [对话 LLM] → 共情回复 + 治疗建议
```

两个 LLM 都是 **MiniCPM4-0.5B**（仅 5 亿参数），分别针对不同任务微调后在手机上本地运行。

### 与你项目的关键差异

| 维度 | MoPHES | 你的项目 |
|---|---|---|
| 评估/对话 | **两个独立模型** | 一个 DeepSeek 同时做 |
| 模型规模 | MiniCPM4-0.5B（端侧） | DeepSeek-Chat（云端） |
| 部署 | 手机本地（llama.cpp） | 服务器 + Gradio |
| 评估范围 | 抑郁 + 焦虑 | 仅抑郁（PHQ-9） |
| 数据 | 11.3 万条中文心理咨询 QA | 无训练数据（用通用 API） |

### 对你的改进点

1. **评估/对话分离思路**：你目前 PHQ-9 打分和共情回复用的是同一个 LCEL Chain（同一个 prompt 里要求"打分 + 反馈"）。MoPHES 的思路是更专业的做法——打分应该是一个精确的、确定性的任务（甚至可以不用 LLM，用规则），而共情回复才是 LLM 的主场。你的 `1graph.py` 已经在做这个分离（`node_score` 单独打分，`node_chat` 单独对话），但 `6persisitent.py` 的 LCEL 链仍然是混合的。

2. **评估模型 benchmark**：论文给出了完整的评估框架（Accuracy, Precision, Recall, F1 for Depression & Anxiety），你可以用同样的指标来评估你的 PHQ-9 打分准确度。当前你的打分没有客观的 ground truth 做对比——可以学 MoPHES 的设计，找标注数据验证。

3. **每 5 轮自动评估**：MoPHES 的评估不是一次性的——每 5 轮对话自动重新评估用户心理状态。你的项目只在首次对话时做一次 PHQ-9，这在长期咨询场景中不够。你应该考虑在自由对话阶段定期（如每 10 轮）触发一次简短的心境复查。

4. **GAD-7 扩展**：README 中提到的 commit `134a272` 说引入了 GAD-7 量表——这意味着你已经走向抑郁+焦虑双维度评估，和 MoPHES 的方向一致。可以从 MoPHES 论文中借评估指标设计。

5. **数据参考**：MoPHES 使用的 Chinese-Psychological-QA-Dataset 和 EmoLLM 都是中文心理咨询数据。如果你的毕设需要微调或评估数据，这些是可直接使用的开放资源。

---

## 七、LangSmith — 可观测性即战力

**来源**：`08-langsmith.md`

### 对你的改进点

1. **替换所有 `print()` 调试**：你目前用 `print(f"[question] q_idx=...")` 和 `print(f"[score] 第{q_idx}题得分=...")` 做调试。LangSmith 可以自动追踪每次 `graph.invoke()` 的完整链路。

2. **毕设答辩展示**：LangSmith 的追踪仪表盘可以作为你的系统架构演示图，比用 PPT 画流程图更直观、更专业。

3. **接入极其简单**：设置环境变量即可，不需要改代码：
   ```bash
   export LANGCHAIN_TRACING_V2=true
   export LANGCHAIN_API_KEY="your-key"
   export LANGCHAIN_PROJECT="mental-health-agent"
   ```

4. **免费 tier 足够**：LangSmith 有免费额度，个人毕设项目完全够用。

---

## 八、综合行动清单（按优先级）

### 立即执行（本周）

- [ ] **给 State 加 `schema_version` 字段**（参考资源四 §3）
- [ ] **消息列表加硬上限**（`append_messages` 返回 `[-200:]`，参考资源四 §2）
- [ ] **毕设 Related Work 引用 HopeBot + MoPHES**（参考资源五 §1、资源六 §1）

### 短期（1-2 周）

- [ ] **接 LangSmith**（替换 print 调试，参考资源七）
- [ ] **引入 LangGraph Store 存用户画像**（替代 `long_term_summary` 字段，参考资源一、二）
- [ ] **评估/对话分离**：`node_score` 用 temperature=0 的精确打分，`node_chat` 用 temperature=0.7 的共情对话（参考资源六 §1）

### 中期（1 个月）

- [ ] **安装 LangMem SDK**（替代手写压缩节点，参考资源三）
- [ ] **自由对话中加入定期心境复查**（参考资源六 §3）
- [ ] **找 20 名志愿者做 within-subject 对比实验**（参考资源五 §2）

### 长期（毕设后期 / Web 部署）

- [ ] **从 SqliteSaver 迁移到 AsyncPostgresSaver**（参考资源四 §1）
- [ ] **加 LangMem 的 Prompt Optimization**（从对话中优化共情话术，参考资源三 §3）
