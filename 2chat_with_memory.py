import os
from dotenv import load_dotenv
#读取.env文件，将密钥加载到环境变量中
from langchain_community.chat_models import ChatOpenAI#引入OPENAI的对话模型接口
from langchain.chains import ConversationChain#专门用来管理对话流，将模型、记忆和输入串联起来，使得模型可以维持上下文对话。
from langchain.memory import ConversationBufferMemory#记忆存储器，把整个对话历史完整保存下来，并作为上下文传给大模型



# 1. 读取 .env 文件中的环境变量并写入os.environ文件
# （程序启动时，操作系统会把当前系统的环境变量复制一份到environ文件，程序执行时候只会去environ文件内找）
load_dotenv()

# 2. 从环境变量中获取 API Key，实际是deepseek的api
api_key = os.getenv("OPENAI_API_KEY")
# 1. 配置 DeepSeek API
#这里将os.environ文件中的OPENAI_API_KEY值设置成api_key的值
os.environ["OPENAI_API_KEY"] = api_key
#以上两行其实可以删除，因为我的environ文件中的参数名称就是OPENAI_API_KEY
os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com"  # 或者是 https://api.deepseek.com/v1

# 2. 实例化chatopenai 客户端接口-deepseek
# 0.7越大越随机（接受差解的概率）
llm = ChatOpenAI(
    model_name="deepseek-chat",
    temperature=0.7
)

# 3. 初始化记忆体（用于在内存中自动管理对话上下文）
memory = ConversationBufferMemory()

# 4. 构建经典对话链
# verbose=True 是个工程小技巧，能让你在控制台直观看到 LangChain 是如何把“历史记录”悄悄塞给 Prompt 的）
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