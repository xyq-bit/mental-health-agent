# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Mental health conversational agent using LangChain/LangGraph + DeepSeek API + Gradio. Conducts PHQ-9 depression screening assessments with crisis intervention, then transitions to free-form empathetic dialogue. Two architectural tracks exist in parallel:

- **App track** (`4app.py` → `6persisitent.py`): Linear Gradio callback with manual state dict, suitable for simple deployment.
- **Graph track** (`1graph.py`, `1graph_skeleton.py`): LangGraph `StateGraph` with nodes, conditional routers, and SQLite checkpointing — the strategic direction for complex multi-turn flows.

## Commands

```bash
# Activate conda environment
conda activate mental_agent

# Run the Gradio web app (persistent multi-user version)
python 6persisitent.py

# Run the simpler single-user Gradio app
python 4app.py

# Run the LangGraph-based agent (terminal, with SQLite checkpointing)
python 1graph.py

# Run the LangGraph skeleton (terminal, in-memory checkpointing)
python 1graph_skeleton.py

# Run the CLI PHQ-9 assessment (no UI)
python 3phq9_agent.py
```

There are no tests, linters, or build steps configured. No test framework is installed.

## Environment

- **Python**: 3.11 via Conda env `mental_agent` (`C:\Users\13207\.conda\envs\mental_agent\`)
- **API**: DeepSeek API, accessed via OpenAI-compatible SDK. API key in `.env` as `OPENAI_API_KEY`. Base URL: `https://api.deepseek.com`.
- **`.env` is gitignored** — never commit it.

## Architecture

### State shape (`AgentState` / state dict)

All tracks share the same conceptual state:

| Field | Purpose |
|---|---|
| `phase` | `0`=login, `1`=assessment (PHQ-9), `2`=crisis intervention, `3`=free chat |
| `waiting` | `False` = ask next question; `True` = score the answer / await crisis reply |
| `q_idx` | Current PHQ-9 question index (1-based in graph track, 0-based in app track) |
| `total_score` | Cumulative PHQ-9 score (0–27) |
| `q9_score` | Score for question 9 (suicidal ideation) — tracked separately for crisis routing |
| `crisis_flag` | (graph track only) Whether crisis intervention is active |
| `messages` | Chat history as `[{"role": "...", "content": "..."}]` |
| `assessment_result` | Set after assessment completes (e.g., "总分15分，评估为...") |
| `long_term_summary` | Compressed summary of old messages evicted by the sliding window |
| `waiting_for_crisis_ack` | (app track) `True` when Q9 triggered crisis warning and we're waiting for user response before wrapping up |

### Graph track flow (LangGraph — `1graph.py`, `1graph_skeleton.py`)

```
START → init → [memory_compress?] → entry_router →
  ├─ question → END (wait for user input)
  ├─ score → score_router →
  │   ├─ next → question
  │   ├─ crisis_warning → END (wait for user input)
  │   └─ assessment_end → chat → END
  ├─ crisis_warning → END
  ├─ crisis_reply → assessment_end → chat → END
  └─ chat → END
```

`entry_router` dispatches on `(phase, waiting)`. `score_router` branches on `q9_score >= 1` (crisis) or `q_idx >= 9` (done) or continues to next question.

Messages use a custom reducer (`append_messages`) that supports a `__reset__` sentinel for replacement mode (used by memory compression).

Persistence: `1graph.py` uses `SqliteSaver` with `data/mental_agent.db`; `1graph_skeleton.py` uses `InMemorySaver`.

### App track flow (Gradio — `6persisitent.py`, `4app.py`)

Linear callback `chat_and_assess()`: check `waiting_for_crisis_ack` → check `is_finished` (free chat) → otherwise assessment phase (LCEL chain scores answer → advance question index).

Persistence: JSON files in `data/{username}.json` with atomic writes (write to `.tmp`, then `os.replace()`).

### Crisis intervention logic

Both tracks implement the same rule: **Q9 score ≥ 1 triggers crisis warning regardless of total score**. Flow:
1. Q9 scored ≥1 → hardcoded `CRISIS_WARNING_TEXT` is shown immediately
2. User responds → LLM generates empathetic follow-up → assessment wraps up with risk level

### Sliding window memory

When `messages` / `free_chat_history` exceeds 50 entries, the oldest 25 are summarized by the LLM into `long_term_summary` and evicted. The summary is prepended to the system prompt for future turns.

### LLM usage

Two patterns coexist:
- **LCEL chain** (`prompt | llm`): Used for PHQ-9 scoring in the app track. Regex-parses "得分: N / 反馈: ..." from output.
- **Raw OpenAI SDK**: Used for free chat, crisis follow-up, and summarization. Simpler but bypasses LangChain abstractions.
- Model: `deepseek-chat` (primary) or `deepseek-v4-flash` (graph track). Temperature varies: 0 for scoring, 0.6–0.8 for chat.

## Key idioms

- The app track files are prefixed with numbers (`4app.py`, `6persisitent.py`) reflecting their development day. The graph track files are `1graph*.py` — not day-ordered.
- `data/` is gitignored per `.gitignore` (last line: `"data/"`). User session JSONs and SQLite DBs live here.
- The `.vscode/settings.json` hardcodes the conda env path — don't change it unless the env moves.
- `6persisitent.py` (note: typo in filename — "persisitent") is the current production Gradio app with multi-user JSON persistence.
