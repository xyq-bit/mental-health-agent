import os
#Python 的内置库，用于和操作系统（Operating System）打交道，比如读取系统变量、查找文件路径。
from openai import OpenAI
#第三方库，用来方便地调用支持 OpenAI 协议的所有 AI 接口（包括 DeepSeek）。
from dotenv import load_dotenv
#第三方库，专门用来加载 .env 文件。它能帮你把 .env 文件里的配置转变成 Python 程序可以直接读取的“环境变量”。
# 1. 加载 .env 文件中的环境变量（在项目根目录下搜寻 .env 文件，读取里面的所有内容，并放入 Python 的内存环境中，让你后续能用 os.getenv 取出来。）
load_dotenv()

# 2. 从环境变量中获取 API Key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("未找到 OPENAI_API_KEY，请确保 .env 文件配置正确且在项目根目录下")

# 3. 类实例化：初始化 DeepSeek 客户端
client = OpenAI(
    api_key=api_key, 
    base_url="https://api.deepseek.com"
)

print("正在向 DeepSeek 发送测试请求...")
#异常处理
try:
    # 4. 发送测试消息
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": "你是一个专业的心理咨询助手，负责协助构建心理健康智能体。"},#角色设定
            {"role": "user", "content": "你好！我已经成功切换到环境变量配置方式，能听到我说话吗？"}#第一轮输入
        ],
        stream=False#表示不逐字流式输出
    )

    # 5. 打印模型的回复
    print("\n连接成功！以下是 DeepSeek 的回复：")
    print("-" * 40)
    #提取回复中需要的内容
    print(response.choices[0].message.content)
    print("-" * 40)
    print("\n🎉 恭喜！Day 1 目标升级达成，环境变量配置已生效！")

except Exception as e:
    print(f"\n❌ 连接失败，错误信息如下：\n{e}")