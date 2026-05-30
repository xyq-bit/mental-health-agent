import os
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv


# 1. 加载 .env 文件中的环境变量
load_dotenv()

# 2. 从环境变量中获取 API Key
api_key = os.getenv("DEEPSEEK_API_KEY")
# 1. 配置 DeepSeek API（这里会自动读取或手动填入你 Day 1 下发的 sk-04c7f...）
# 建议在终端中 set OPENAI_API_KEY=your_key，或者在这里临时明文写入进行测试
os.environ["OPENAI_API_KEY"] = os.getenv("DEEPSEEK_API_KEY", api_key)
os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com"  # 或者是 https://api.deepseek.com/v1

# 2. 初始化 DeepSeek 聊天模型
# 保持 0.7 的创造力，既能保持共情能力，又不会过于脱轨
llm = ChatOpenAI(
    model_name="deepseek-chat",
    temperature=0.7
)

# 3. 初始化记忆体（用于在内存中自动管理对话上下文）
memory = ConversationBufferMemory()

# 4. 构建经典对话链
# verbose=True 是个工程小技巧，能让你在控制台直观看到 LangChain 是如何把“历史记录”悄悄塞给 Prompt 的
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True  
)

print("==================================================")
print("🧠 多模态心理健康 Agent - Day 2 多轮对话测试启动")
print("提示：输入 'exit' 或 'quit' 可退出程序")
print("==================================================\n")

while True:
    try:
        user_input = input("用户: ")
        if user_input.strip().lower() in ['exit', 'quit']:
            print("\n对话结束。别忘了把上面的精彩多轮对话截图保存！")
            break
            
        if not user_input.strip():
            continue
            
        # 激活对话链
        response = conversation.predict(input=user_input)
        print(f"Agent: {response}\n")
        
    except KeyboardInterrupt:
        print("\n程序强行终止。")
        break
    except Exception as e:
        print(f"❌ 发生错误: {e}\n")