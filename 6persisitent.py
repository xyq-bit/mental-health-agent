import os
import re
import json
import gradio as gr
import openai
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# --- 1. 加载环境变量 ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("未找到 OPENAI_API_KEY，请检查 .env 文件是否配置正确")

# --- 2. 配置与初始化 ---
os.environ["OPENAI_API_KEY"] = api_key
os.environ["OPENAI_BASE_URL"] = "https://api.deepseek.com"

# LangChain这个框架提供的对象类型（ChatOpenAI这个类）。它专门配合LCEL那条路线使用
llm = ChatOpenAI(
    model_name="deepseek-chat",
    temperature=0.8,
    openai_api_key=api_key,
    openai_api_base="https://api.deepseek.com"
)
# OpenAI官方原生SDK提供的对象类型；用于创建客户端对象
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
    "9. 脑海中曾冒出过'不如死掉算了'或'用某种方式伤害自己'的念头？"
]

Q9_INDEX = 8

CRISIS_WARNING_TEXT = (
    "⚠️ 我注意到你刚才提到了一些关于伤害自己的想法。这些感受很沉重，但你不是一个人在面对它们。\n"
    "如果你现在有强烈的自伤冲动，请立即联系当地的心理危机干预热线，或前往最近的医院急诊。\n"
    "我会一直在这里陪着你，我们可以继续聊聊你现在的感受。"
)

# ============================================
# 用户名 + 文件持久化
# ============================================
DATA_DIR = "data"  # 存放每个用户对话记录的文件夹


def get_user_filepath(username):
    """
    根据用户名生成对应的文件路径，例如 data/张三.json
    每个用户名对应一个独立的json文件，互不干扰
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{username}.json")


def save_user_session(username, history, state):
    """
    把当前的history和state保存到该用户对应的json文件里。
    注意：state里的'等待预警确认'字段不持久化，关闭重开后应该重置为False，
    不应该让用户卡在"上次还没回应预警"的状态里。
    """
    state_to_save = {k: v for k, v in state.items() if k != '等待预警确认'}
    data = {"history": history, "state": state_to_save}
    filepath = get_user_filepath(username)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_user_session(username):
    """
    尝试读取该用户的历史记录。
    返回值是 (status, history, state) 三元组，status有三种可能：
    - "new"       ：文件不存在，是真正的新用户
    - "corrupted" ：文件存在但内容损坏（不是合法json，或缺少必要字段）——
                    这种情况绝不能直接当作新用户去覆盖，必须让调用方知道
                    "这里曾经有数据，只是读不出来了"，由调用方决定怎么处理，
                    文件本身保持原样，不在这里做任何写入动作。
    - "ok"        ：成功读取，history和state是恢复出来的真实内容
    """
    filepath = get_user_filepath(username)
    if not os.path.exists(filepath):
        return "new", None, None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        history = data["history"]
        state = data["state"]
    except (json.JSONDecodeError, KeyError) as e:
        # JSONDecodeError：文件内容不是合法的json格式（比如写了一半）
        # KeyError：文件是合法json，但缺少"history"或"state"这两个key（结构不对）
        print(f"警告：用户 {username} 的存档文件损坏，无法读取（原因：{e}）")
        return "corrupted", None, None

    # 恢复时重新补上'等待预警确认'这个字段，固定设为False（不持久化这个字段，所以每次恢复都是False）
    state['等待预警确认'] = False
    return "ok", history, state


def build_fresh_state():
    """新用户的初始state，集中在一处定义，避免多处重复写、容易遗漏字段"""
    return {
        'q_idx': 0,
        'total_score': 0,
        'q9_score': 0,
        'is_finished': False,
        '测评摘要': None,
        '自由对话历史': [],
        '长期记忆摘要': None,
        '等待预警确认': False
    }


# --- 3. LCEL 测评链 ---
system_template = """你是一位专业的心理评估助手。请根据用户的回答评估分数(0-3)并给出温和的共情回复。
输出格式严格为：
得分: [数字]
反馈: [温和回复]"""
prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("human", "{question}\n用户回答：{user_answer}")
])
chain = prompt | llm


def generate_summary(messages_to_summarize):
    summary_prompt = (
        "请把以下对话内容总结成2-3句话的要点摘要，保留对理解用户情绪和处境最重要的信息：\n\n"
        + "\n".join([f"{m['role']}: {m['content']}" for m in messages_to_summarize])
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": summary_prompt}]
    )
    return response.choices[0].message.content


def calculate_risk_level(total_score, q9_score):
    if total_score > 19 or q9_score >= 1:
        if q9_score >= 1:
            level = "重度抑郁倾向（含自杀风险信号，需特别关注）"
        else:
            level = "重度抑郁倾向"
    elif total_score >= 15:
        level = "中重度抑郁倾向"
    elif total_score >= 10:
        level = "中度抑郁倾向"
    elif total_score >= 5:
        level = "轻度抑郁倾向"
    else:
        level = "没有明显抑郁倾向"
    return level


# --- 4. 核心逻辑 ---
def chat_and_assess(user_input, history, state, username):
    if state is None:
        state = build_fresh_state()

    if state['等待预警确认']:
        state['等待预警确认'] = False

        crisis_followup_prompt = (
            "你是一位专业的心理健康咨询师。用户刚刚被提醒关注自身安全（因为测评中显示出自伤/自杀的风险信号），"
            "现在用户做出了如下回应，请给予温和、真诚的共情回复，不要重复说教，"
            "如果用户的回应仍然显示出明显的危险信号，请再次温和地建议寻求专业帮助：\n\n"
            f"用户的回应：{user_input}"
        )
        # openai原生回应
        followup_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": crisis_followup_prompt}]
        )
        followup_text = followup_response.choices[0].message.content

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": followup_text})

        state['is_finished'] = True
        risk_level = calculate_risk_level(state['total_score'], state['q9_score'])
        state['测评摘要'] = f"总分{state['total_score']}分，评估为{risk_level}"

        history.append({
            "role": "assistant",
            "content": f"测评完成！总分 {state['total_score']}。评估结果：{risk_level}。现在我们可以自由交流了。"
        })

        save_user_session(username, history, state)
        return "", history, state

    if state['is_finished']:
        long_term_note = ""
        if state['长期记忆摘要']:
            long_term_note = f"\n此前对话的要点回顾：{state['长期记忆摘要']}"

        system_content = (
            f"你是一位专业的心理健康咨询师，请共情引导。"
            f"用户刚完成PHQ-9测评，测评结果为：{state['测评摘要']}。"
            f"请结合此信息进行共情对话，如果用户透露出自伤或自杀的想法，请立刻温和地引导其寻求专业帮助。"
            f"{long_term_note}"
        )

        messages = (
            [{"role": "system", "content": system_content}]
            + state['自由对话历史']
            + [{"role": "user", "content": user_input}]
        )

        response = client.chat.completions.create(model="deepseek-chat", messages=messages)
        bot_response = response.choices[0].message.content

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": bot_response})

        state['自由对话历史'].append({"role": "user", "content": user_input})
        state['自由对话历史'].append({"role": "assistant", "content": bot_response})

        if len(state['自由对话历史']) > 50:
            oldest_messages = state['自由对话历史'][:25]
            new_summary_piece = generate_summary(oldest_messages)

            if state['长期记忆摘要'] is None:
                state['长期记忆摘要'] = new_summary_piece
            else:
                state['长期记忆摘要'] = state['长期记忆摘要'] + "\n" + new_summary_piece

            state['自由对话历史'] = state['自由对话历史'][25:]

        save_user_session(username, history, state)
        return "", history, state

    # 测评阶段
    q_idx = state['q_idx']
    response = chain.invoke({"question": PHQ9_QUESTIONS[q_idx], "user_answer": user_input})
    ai_output = response.content

    score_match = re.search(r"得分:\s*([0-3])", ai_output)
    feedback_match = re.search(r"反馈:\s*([\s\S]*)", ai_output)
    score = int(score_match.group(1)) if score_match else 0
    feedback = feedback_match.group(1).strip() if feedback_match else "收到您的回答。"

    if q_idx == Q9_INDEX:
        state['q9_score'] = score

    state['total_score'] += score
    state['q_idx'] += 1

    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": feedback})

    q9_triggered_warning = (q_idx == Q9_INDEX and score >= 1)
    if q9_triggered_warning:
        history.append({"role": "assistant", "content": CRISIS_WARNING_TEXT})

    if state['q_idx'] < len(PHQ9_QUESTIONS):
        next_q = PHQ9_QUESTIONS[state['q_idx']]
        history.append({"role": "assistant", "content": f"下一题：{next_q}"})
    else:
        if q9_triggered_warning:
            state['等待预警确认'] = True
        else:
            state['is_finished'] = True
            risk_level = calculate_risk_level(state['total_score'], state['q9_score'])
            state['测评摘要'] = f"总分{state['total_score']}分，评估为{risk_level}"

            history.append({
                "role": "assistant",
                "content": f"测评完成！总分 {state['total_score']}。评估结果：{risk_level}。现在我们可以自由交流了。"
            })

    save_user_session(username, history, state)
    return "", history, state


# ============================================
# 用户进入会话时的处理逻辑
# ============================================
def enter_session(username):
    """
    用户输入名字并点击"进入"后触发。
    检查该用户名是否有历史记录：
    - 真正的新用户 → 新建记录
    - 有历史记录、读取成功 → 恢复
    - 有历史记录、但读取失败（文件损坏） → 绝不能直接当新用户处理并覆盖文件！
      这种情况下，原始文件依然完整保留在磁盘上，只是先用一条提示告诉用户
      "检测到存档异常"，不会自动新建/覆盖，避免误删可能还能人工恢复的数据。
    """
    username = username.strip()
    if not username:
        return (
            [{"role": "assistant", "content": "请先输入一个名字再进入～"}],
            None,
            "",
            gr.update(visible=True),
            gr.update(interactive=False)
        )

    status, saved_history, saved_state = load_user_session(username)

    if status == "ok":
        history, state = saved_history, saved_state

    elif status == "corrupted":
        # 关键：这里绝对不调用 save_user_session，不能用空记录去覆盖这个文件。
        # 文件本身原封不动留在磁盘上，只是这次没能正常读出来。
        return (
            [{"role": "assistant", "content": (
                f"⚠️ 检测到「{username}」的存档文件存在异常，无法正常读取。\n"
                f"为避免覆盖丢失原有数据，暂停在此处。\n"
                f"如果您确认可以放弃之前的记录、重新开始，请换一个新的名字重新进入；"
                f"如果这是重要数据，请联系管理员协助检查 data 文件夹中对应的文件。"
            )}],
            None,
            "",
            gr.update(visible=True),
            gr.update(interactive=False)
        )

    else:  # status == "new"，真正的新用户
        history = [{"role": "assistant", "content": f"你好 {username}，我们来做一个PHQ-9心理健康测评。\n\n" + PHQ9_QUESTIONS[0]}]
        state = build_fresh_state()
        save_user_session(username, history, state)  # 新用户立即建档，这里覆盖是安全的——本来就没有旧数据

    return (
        history,
        state,
        username,
        gr.update(visible=False),
        gr.update(interactive=True)
    )


# --- 5. UI 界面 ---
with gr.Blocks() as demo:
    # 登录区域：输入用户名
    with gr.Column(visible=True) as login_area:
        gr.Markdown("### 请输入您的名字以开始/继续测评")
        username_input = gr.Textbox(label="您的名字", placeholder="例如：张三")
        enter_btn = gr.Button("进入", variant="primary")

    # 聊天组件始终可见（避免 Gradio 6 hidden→visible 的 loading bug）
    chatbot = gr.Chatbot(label="心理咨询", value=[])
    msg = gr.Textbox(interactive=False, placeholder="请先登录后使用...")

    state = gr.State()           # 测评/对话的状态数据
    username_state = gr.State()  # 记住当前登录的用户名

    enter_btn.click(
        enter_session,
        inputs=[username_input],
        outputs=[chatbot, state, username_state, login_area, msg]
    )

    msg.submit(
        chat_and_assess,
        inputs=[msg, chatbot, state, username_state],
        outputs=[msg, chatbot, state]
    )

if __name__ == "__main__":
    demo.launch()