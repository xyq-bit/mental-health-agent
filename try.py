import os
from dotenv import load_dotenv

# 打印一下当前的绝对路径
print(f"当前 Python 正在寻找 .env 的路径: {os.path.abspath('.env')}")

# 强制加载
load_dotenv(dotenv_path=os.path.abspath('.env'))

api_key = os.getenv("DEEPSEEK_API_KEY")
print(f"读取到的 Key 内容: {api_key}")