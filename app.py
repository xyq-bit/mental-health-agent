import os
import re
import gradio as gr
import openai
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# --- 1. 加载环境变量 ---
# 会自动查找项目根目录下的 .env 文件
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# 检查是否成功获取到 Key
if not api_key:
    raise ValueError("未找到 DEEPSEEK_API_KEY，请检查 .env 文件是否配置正确")

# --- 2. 配置与初始化 ---
os.environ["OPENAI_API_KEY"] = api_key
os.environ["OPENAI_BASE_URL"] = "https://api.deepseek.com"

# 初始化模型
llm = ChatOpenAI(
    model_name="deepseek-v4-pro", 
    temperature=0.3, 
    openai_api_key=api_key, 
    openai_api_base="https://api.deepseek.com"
)
client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

PHQ9_QUESTIONS = [
    "1. 做任何事都提不起劲或没有乐趣？",
    "2. 感到心情低落、沮丧或绝望？",
    "3. 入睡困难、睡不安稳或睡得太多？",
    "4. 感到疲倦或没有活力？",
    "5. 食欲不振或吃得太多？",
    "6. 觉得自己很糟，或觉得自己很失败，或让自己及家人失望？",
    "7. 专注于别的事有困难，例如看报纸或看电视？",
    "8. 行动或说话速度慢到别人已经察觉？或者正好相反，烦躁不安、动来动去？",
    "9. 脑海中曾冒出过‘不如死掉算了’或‘用某种方式伤害自己’的念头？"
]

# --- 3. LCEL 测评链 ---
system_template = """你是一位专业的心理评估助手。请根据用户的回答评估分数(0-3)并给出温和的共情回复。
输出格式严格为：
得分: [数字]
反馈: [温和回复]"""
prompt = ChatPromptTemplate.from_messages([("system", system_template), ("human", "{question}\n用户回答：{user_answer}")])
chain = prompt | llm

# --- 4. 核心逻辑 ---
def chat_and_assess(user_input, history, state):
    if state is None:
        state = {'q_idx': 0, 'total_score': 0, 'is_finished': False}
    
    # 自由对话阶段
    if state['is_finished']:
        messages = [{"role": "system", "content": "你是一位专业的心理健康咨询师，请共情引导。"}] + history + [{"role": "user", "content": user_input}]
        response = client.chat.completions.create(model="deepseek-chat", messages=messages)
        bot_response = response.choices[0].message.content
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": bot_response})
        return "", history, state

    # 测评阶段
    q_idx = state['q_idx']
    response = chain.invoke({"question": PHQ9_QUESTIONS[q_idx], "user_answer": user_input})
    ai_output = response.content
    
    score_match = re.search(r"得分:\s*([0-3])", ai_output)
    feedback_match = re.search(r"反馈:\s*([\s\S]*)", ai_output)
    score = int(score_match.group(1)) if score_match else 0
    feedback = feedback_match.group(1).strip() if feedback_match else "收到您的回答。"
    
    state['total_score'] += score
    state['q_idx'] += 1
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": feedback})
    
    if state['q_idx'] < len(PHQ9_QUESTIONS):
        next_q = PHQ9_QUESTIONS[state['q_idx']]
        history.append({"role": "assistant", "content": f"下一题：{next_q}"})
    else:
        state['is_finished'] = True
        history.append({"role": "assistant", "content": f"测评完成！总分 {state['total_score']}。现在我们可以自由交流了。"})
        
    return "", history, state

# --- 5. UI 界面 ---
with gr.Blocks() as demo:
    chatbot = gr.Chatbot(label="心理咨询")
    msg = gr.Textbox()
    state = gr.State()
    msg.submit(chat_and_assess, [msg, chatbot, state], [msg, chatbot, state])
    demo.load(lambda: ([{"role": "assistant", "content": "你好，开始测评：" + PHQ9_QUESTIONS[0]}], {'q_idx': 0, 'total_score': 0, 'is_finished': False}), None, [chatbot, state])

if __name__ == "__main__":
    demo.launch()