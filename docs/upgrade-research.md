# 项目升级方案：当前 vs 最新方案全景对比

> 整理时间：2026-07-16

---

## 一、记忆压缩

### 当前方案
手写 `node_memory_compress`，messages > 100 条才触发一次 LLM 调用做摘要，存进 `long_term_summary: str`。

### 最新方案：LangGraph 原生双层记忆架构

LangGraph 提供两套互补的持久化系统：

| 组件 | 职责 |
|---|---|
| **Checkpointer** | Thread 内的短期状态（会话连续性、断点恢复） |
| **Store** | 跨 thread 的长期记忆（用户偏好、历史事实） |

二者可以同时启用。你把长期摘要塞进 State 里，是把本该放 Store 的东西放进了 Checkpointer，属于架构性混用。

**升级路径：**
- `SqliteSaver`（Checkpointer）继续管当前会话 → 不变
- 新增 `InMemoryStore` / `PostgresStore`（Store）管跨会话用户画像 → 替代 `long_term_summary` 字段

> 🔗 [LangGraph Persistence 官方文档](https://docs.langchain.com/oss/python/langgraph/persistence)
> 🔗 [原理深讲：Persistent Agent Memory in LangGraph (2026/05)](https://focused.io/lab/persistent-agent-memory-in-langgraph)

---

### 更上一层：LangMem SDK

[LangMem](https://github.com/langchain-ai/langmem) 帮助 Agent 从交互中学习和适应：

- 从对话中提取关键信息的工具
- 通过 Prompt 精化优化 Agent 行为
- 维护长期记忆，与 LangGraph Store 层原生集成

可**完全替代手写的压缩节点**，且质量更高（语义提取 vs 截断压缩）。

**两种记忆形成模式：**

| 模式 | 特点 |
|---|---|
| **Hot-path** | 对话中实时更新，有感知延迟 |
| **Background** | 对话结束后异步提取，不影响响应速度 |

> ⚠️ LangMem 的 p95 检索延迟在 LOCOMO 基准上达到 59.82 秒。若需亚秒级记忆召回，应使用 Mem0（0.200s p95）或 Zep。心理咨询场景延迟容忍度较高，LangMem 可用。

> 🔗 [GitHub](https://github.com/langchain-ai/langmem)
> 🔗 [官方文档](https://langchain-ai.github.io/langmem/)
> 🔗 [发布博客](https://www.langchain.com/blog/langmem-sdk-launch)

---

## 二、持久化层

### 当前方案
`SqliteSaver` — 单进程 CLI 场景足够。

### 最新方案

| 方案 | 适用场景 |
|---|---|
| **SqliteSaver** | 单进程原型、本地 CLI 工具 |
| **AsyncPostgresSaver + asyncpg** | 多实例 Web 服务，行级锁 + 水平扩展 |

**升级路径：** `SqliteSaver`（dev）→ `AsyncPostgresSaver + asyncpg 连接池`（prod）

> 🔗 [LangGraph State Management: Undocumented Issues After Commit](https://altersquare.io/langgraph-state-management-undocumented-issues-after-commit/)

---

## 三、PHQ-9 Agent 学术前沿

### ① HopeBot（最相关！）

HopeBot 是一个基于 LLM、使用 RAG 和实时澄清来管理 PHQ-9 的聊天机器人。

**实验结果（132 名受试者）：**
- ICC = 0.91（与自填问卷一致性极高）
- 45% 完全一致
- 71%（75 名参与者）表示更信任聊天机器人版本
- 理由：结构更清晰、有解释性指导、支持性语气

这篇论文和你做的几乎是同一件事，ICC=0.91 可作为评估基线参考，可直接引用为 Related Work。

> 🔗 [arxiv: 2507.05984](https://arxiv.org/abs/2507.05984)

---

### ② MoPHES（技术架构参考）

MoPHES 框架使用两个经过微调的 MiniCPM4-0.5B LLM：

| LLM | 职责 |
|---|---|
| LLM-1 | 在心理健康数据集上微调，评估用户心理状态、预测焦虑/抑郁严重程度 |
| LLM-2 | 在多轮对话上微调，与用户进行对话交流 |

**与你项目的关键差异：** 评估 LLM 和对话 LLM 分离，而你现在两个职责都压在一个 DeepSeek 上。这是一个值得考虑的架构演进方向。

> 🔗 [arxiv: 2510.16085](https://arxiv.org/abs/2510.16085)
> 🔗 [GitHub](https://github.com/weixun2018/MoPHES)

---

## 四、可观测性

### 当前方案
`print()` 调试，无可观测性基础设施。

### 最新方案：LangSmith Tracing

企业级 LangGraph 部署四大支柱：
1. PostgreSQL 检查点持久化
2. **LangSmith Tracing** 可观测性
3. 基于 interrupt 的人机协作治理
4. 部署目标（LangGraph Platform 或自托管容器）

> 🔗 [LangSmith](https://www.langsmith.com/)（免费 tier 够用）

---

## 升级优先级建议

| 优先级 | 改动 | 价值 | 难度 |
|---|---|---|---|
| ⭐⭐⭐ | 读 HopeBot 论文 | 毕设 Related Work 直接引用 | 低 |
| ⭐⭐⭐ | 修复 `node_continue` 空返回 | 修复已知 bug | 已解决 |
| ⭐⭐ | 加 LangGraph BaseStore 存用户画像 | 替代 `long_term_summary` 字段 | 中 |
| ⭐⭐ | 接 LangSmith | 调试和演示都提升一个档次 | 低 |
| ⭐ | LangMem SDK | 替代压缩节点，语义记忆 | 中 |
| ⭐ | PostgresSaver | 仅在做 Web 服务时需要 | 中 |
