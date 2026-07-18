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
# OpenAI官方原生OPENAI SDK提供的对象类型；用于创建客户端对象
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
# 新增部分：用户名 + 文件持久化
# ============================================
DATA_DIR = "data"  # 存放每个用户对话记录的文件夹


def get_user_filepath(username):
    """
    根据用户名生成对应的文件路径，例如 data/张三.json
    每个用户名对应一个独立的json文件，互不干扰
    """
    os.makedirs(DATA_DIR, exist_ok=True)  # 文件夹不存在就创建，exist_ok=True避免文件夹已存在时报错
    return os.path.join(DATA_DIR, f"{username}.json")


# 保存用户会话记录
def save_user_session(username, history, state):
    """
    把当前的history和state保存到该用户对应的json文件里。
    注意：state里的'等待预警确认'字段不持久化——这是我们讨论过的，
    这个字段只是一次连续会话内的临时标记，关闭重开后应该重置为False，
    不应该让用户卡在"上次还没回应预警"的状态里。

    这里用"原子写入"的方式，而不是直接对正式文件写：
    1. 先把内容完整写进一个临时文件（文件名加 .tmp 后缀），不碰正式文件
    2. 确认临时文件已经完整写完之后，才用 os.replace() 把临时文件"改名"
       成正式文件名，这一步会替换掉旧文件
    原因：如果在"写入内容"这一步的中途，程序被打断（崩溃/断电/强制关闭），
    受影响的只是这个 .tmp 临时文件，正式文件这一刻完全没有被动过。

    这个函数返回一个布尔值（True/False），表示这次保存是否成功：
    - 写入过程中如果出现任何异常（比如磁盘满了、没有写入权限），
      不会让程序崩溃，而是捕获这个异常、返回False，
      把"要不要告诉用户、要不要重试"这个决定权交给调用这个函数的代码，
      让用户当前正在进行的对话不会被这种底层的存储问题打断。
    """
    state_to_save = {k: v for k, v in state.items() if k != '等待预警确认'}
    data = {"history": history, "state": state_to_save}
    filepath = get_user_filepath(username)
    tmp_filepath = filepath + ".tmp"

    try:
        with open(tmp_filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_filepath, filepath)
        return True
    except OSError as e:
        # OSError涵盖了大多数文件系统层面的问题：磁盘满了、没有权限、路径不合法等
        print(f"警告：用户 {username} 的本轮对话保存失败（原因：{e}）")
        return False


def load_user_session(username):
    """
    尝试读取该用户的历史记录。
    返回 (status, history, state) 三元组：
    - status == "new"       ：文件不存在，是真正的新用户
    - status == "corrupted" ：文件存在，但内容已经损坏，读取失败——
                              这种情况下，这个函数本身不会对文件做任何写入/修改/删除操作，
                              文件原封不动留在磁盘上，把"怎么处理"这个决定权交给调用方
    - status == "ok"        ：成功读取，history和state是恢复出来的真实内容
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
        # JSONDecodeError：文件内容不是合法的json格式（比如写了一半被中断）
        # KeyError：文件是合法json，但缺少"history"或"state"这两个必须的key
        # 这里只是读取失败、打印警告，绝对不会删除或者重新写入这个文件
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


def save_and_warn_if_failed(username, history, state):
    """
    调用save_user_session保存这一轮对话；如果保存失败（返回False），
    在history末尾追加一条温和的提示，告诉用户这一轮可能没有被保存下来，
    但不阻塞、不报错，用户依然可以正常继续输入、继续对话——
    只是这一轮的内容，万一现在关闭页面，可能会丢失。
    """
    saved_ok = save_user_session(username, history, state)
    if not saved_ok:
        history.append({
            "role": "assistant",
            "content": "（系统提示：刚才这一轮内容保存时遇到了一点问题，如果担心丢失，建议稍后重新发一次。不影响您继续对话。）"
        })


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
# 注意：chat_and_assess现在多了一个username参数，用于知道该把进度存到哪个文件
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

        save_and_warn_if_failed(username, history, state)  # 持久化：每轮结束都存一次，失败时追加提示，不阻塞对话
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

        save_and_warn_if_failed(username, history, state)  # 持久化：每轮结束都存一次，失败时追加提示，不阻塞对话
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

    save_and_warn_if_failed(username, history, state)  # 持久化：每轮结束都存一次，失败时追加提示，不阻塞对话
    return "", history, state


# ============================================
# 新增：用户进入会话时的处理逻辑
# ============================================
def enter_session(username):
    """
    用户输入名字并点击"进入"后触发。
    检查该用户名是否有历史记录：
    - 真正的新用户（status=="new"） → 新建记录
    - 有历史记录、读取成功（status=="ok"） → 恢复
    - 有历史记录、但读取失败（status=="corrupted"） → 停在登录区域，
      明确提示用户"检测到存档异常"，绝不调用save_user_session去覆盖这个文件名。
      旧文件因此被完整保留在磁盘上，不会因为用户接下来的任何操作被改写——
      因为程序根本不会再对这个文件名执行任何写入，直到这个问题被人工处理。
    """
    username = username.strip()
    if not username:
        # 用户没填名字就点了进入，给一个提示，不切换界面
        return (
            [{"role": "assistant", "content": "请先输入一个名字再进入～"}],
            None,
            "",
            gr.update(visible=True),       # 登录区域保持可见
            gr.update(interactive=False)   # 输入框不可用
        )

    status, saved_history, saved_state = load_user_session(username)

    if status == "ok":
        history, state = saved_history, saved_state

    elif status == "corrupted":
        # 关键：这里绝对不会调用save_user_session，也不会继续往下走。
        # 旧文件原封不动留在磁盘上，用户暂时无法继续使用这个用户名，
        # 直到管理员人工检查/修复了 data 文件夹里对应的文件。
        return (
            [{"role": "assistant", "content": (
                f"⚠️ 检测到「{username}」的存档文件存在异常，无法正常读取。\n"
                f"为避免覆盖丢失原有数据，该用户名暂时无法继续使用。\n"
                f"原始文件已被完整保留在 data 文件夹中，请联系管理员协助检查；"
                f"如果确认可以放弃之前的记录，可以换一个新的名字重新开始。"
            )}],
            None,
            "",
            gr.update(visible=True),
            gr.update(interactive=False)
        )

    else:  # status == "new"，真正的新用户，磁盘上原本就没有这个文件，新建是安全的
        history = [{"role": "assistant", "content": f"你好 {username}，我们来做一个PHQ-9心理健康测评。\n\n" + PHQ9_QUESTIONS[0]}]
        state = build_fresh_state()
        save_user_session(username, history, state)  # 新用户立即建档

    return (
        history,
        state,
        username,
        gr.update(visible=False),      # 进入成功后隐藏登录区域
        gr.update(interactive=True)    # 允许输入
    )


# --- 5. UI 界面 ---
with gr.Blocks() as demo:
    # 登录区域：输入用户名，登录后自动隐藏
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