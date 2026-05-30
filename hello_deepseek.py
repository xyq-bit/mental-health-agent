import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. 加载 .env 文件中的环境变量
load_dotenv()

# 2. 从环境变量中获取 API Key
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("未找到 DEEPSEEK_API_KEY，请确保 .env 文件配置正确且在项目根目录下")

# 3. 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=api_key, 
    base_url="https://api.deepseek.com"
)

print("正在向 DeepSeek 发送测试请求...")

try:
    # 4. 发送测试消息
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个专业的心理咨询助手，负责协助构建心理健康智能体。"},
            {"role": "user", "content": "你好！我已经成功切换到环境变量配置方式，能听到我说话吗？"}
        ],
        stream=False
    )

    # 5. 打印模型的回复
    print("\n连接成功！以下是 DeepSeek 的回复：")
    print("-" * 40)
    print(response.choices[0].message.content)
    print("-" * 40)
    print("\n🎉 恭喜！Day 1 目标升级达成，环境变量配置已生效！")

except Exception as e:
    print(f"\n❌ 连接失败，错误信息如下：\n{e}")