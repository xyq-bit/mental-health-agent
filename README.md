# mental-health-agent
# 多模态心理健康对话 Agent
基于 LangChain 的多模态心理健康咨询 Agent

本项目是一个基于 LangChain 和 DeepSeek API 构建的专业心理健康对话 Agent。旨在通过结构化对话辅助用户进行心理健康初步评估（如 PHQ-9 量表），并提供具备共情能力的反馈与支持。

## 🚀 项目亮点
* **智能测评逻辑**：集成 PHQ-9 量表评估逻辑，能够处理多轮对话并记录状态。
* **DeepSeek 驱动**：利用高性能 API 实现低延迟、高质量的心理咨询对话。
* **工程化设计**：采用 `.env` 环境变量安全管理，代码结构清晰，易于维护与扩展。
* **多模态演进**：项目处于持续开发中，后续将接入视觉情绪识别与垂直领域 RAG。

## 🛠 技术栈
- **核心框架**: LangChain, LangGraph
- **大模型**: DeepSeek-Chat (API)
- **前端交互**: Gradio
- **环境管理**: Conda (Python 3.11)

## 📦 项目结构
```text
mental-health-agent/
├── app.py              # 主程序（Gradio 界面）
├── examples/           # 开发过程中的 API/对话测试 Demo
├── requirements.txt    # 项目依赖清单
├── .env                # 环境变量（存放 API Key）
└── README.md           # 项目说明文档
