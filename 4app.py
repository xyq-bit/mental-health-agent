import os
import re
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

llm = ChatOpenAI(
    model_name="deepseek-chat",   # 统一成 deepseek-chat，和下面 client 调用的模型保持一致
    temperature=0.8,              # 从0.3调高，让每题的共情反馈措辞更有变化，不要太模板化
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
    "9. 脑海中曾冒出过'不如死掉算了'或'用某种方式伤害自己'的念头？"
]

# 第9题在列表里的下标。PHQ9_QUESTIONS[0]是第1题，所以第9题下标是8。
Q9_INDEX = 8

# 危机预警文案：写成固定的Python字符串，不依赖模型生成，
# 这样不管模型当时听不听话，这句话都100%会被加进对话。
CRISIS_WARNING_TEXT = (
    "⚠️ 我注意到你刚才提到了一些关于伤害自己的想法。这些感受很沉重，但你不是一个人在面对它们。\n"
    "如果你现在有强烈的自伤冲动，请立即联系当地的心理危机干预热线，或前往最近的医院急诊。\n"
    "我会一直在这里陪着你，我们可以继续聊聊你现在的感受。"
)

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
    """
    把一段对话历史交给模型，请它总结成一句话摘要。
    用于滑动窗口：删除旧对话之前，先把内容浓缩保存下来，避免模型"突然失忆"。
    """
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
    """
    计算风险等级。
    设计原则（这是我们讨论确认过的）：
    1. 总分>19，判定为重度抑郁——这是按总分的常规分级。
    2. 第9题（自杀意念）只要 >=1分，无论总分多少，都单独触发预警。
       这两个判断是"或"的关系，不要求同时满足。
    """
    if total_score > 19 or q9_score >= 1:
        # 注意：q9_score >= 1 单独就能让你进入这个分支，不需要总分也很高
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
def chat_and_assess(user_input, history, state):
    if state is None:
        # 这一句是兜底防护（我们之前讨论过的竞态条件场景），正常流程不会走到这里
        state = {
            'q_idx': 0,
            'total_score': 0,
            'q9_score': 0,
            'is_finished': False,
            '测评摘要': None,        # 测评结束前为空，测评结束时才会被赋值
            '自由对话历史': [],      # 专门给自由对话阶段用的历史，不混入测评阶段的9轮记录
            '长期记忆摘要': None,    # 滑动窗口删除旧对话前，把旧内容浓缩存在这里
            '等待预警确认': False    # 新增状态：第9题触发预警后，先暂停在这里，等用户回应
        }

    # ============================================
    # 新增分支：等待用户回应危机预警
    # 这个分支必须放在 is_finished 判断之前检查，因为这是一个"插队"的中间状态：
    # 第9题触发预警后，先卡在这里，不直接进入测评结束/自由对话，等用户回应一次再继续
    # ============================================
    if state['等待预警确认']:
        state['等待预警确认'] = False  # 用户已经回应了，清除这个等待状态，往下走正常流程

        # 这里不再用固定的一句话，改成真正调用模型，
        # 让回复真正针对用户这次说的具体内容，而不是每次都一样
        crisis_followup_prompt = (
            "你是一位专业的心理健康咨询师。用户刚刚被提醒关注自身安全（因为测评中显示出自伤/自杀的风险信号），"
            "现在用户做出了如下回应，请给予温和、真诚的共情回复，不要重复说教，"
            "如果用户的回应仍然显示出明显的危险信号，请再次温和地建议寻求专业帮助：\n\n"
            f"用户的回应：{user_input}"
        )
        followup_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": crisis_followup_prompt}]
        )
        followup_text = followup_response.choices[0].message.content

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": followup_text})

        # 用户回应完预警后，才真正完成测评收尾：计算风险等级、生成测评摘要
        state['is_finished'] = True
        risk_level = calculate_risk_level(state['total_score'], state['q9_score'])
        state['测评摘要'] = f"总分{state['total_score']}分，评估为{risk_level}"

        history.append({
            "role": "assistant",
            "content": f"测评完成！总分 {state['total_score']}。评估结果：{risk_level}。现在我们可以自由交流了。"
        })

        return "", history, state

    # ============================================
    # 自由对话阶段
    # ============================================
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

        # 这里不再传入完整的 history（那里面混着测评阶段的9轮机械问答），
        # 改成传 state['自由对话历史']，这个列表只包含自由对话阶段真实发生的对话
        messages = (
            [{"role": "system", "content": system_content}]
            + state['自由对话历史']
            + [{"role": "user", "content": user_input}]
        )

        response = client.chat.completions.create(model="deepseek-chat", messages=messages)
        bot_response = response.choices[0].message.content

        # 给Gradio界面显示用，这个不能省，否则用户在界面上看不到这一轮对话
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": bot_response})

        # 同时也要存进"自由对话历史"，这样下一轮调用模型时，模型才能记得这一轮说了什么
        state['自由对话历史'].append({"role": "user", "content": user_input})
        state['自由对话历史'].append({"role": "assistant", "content": bot_response})

        # 滑动窗口：自由对话历史超过50条消息时，把最早的25条总结成摘要后删除，
        # 避免无限增长导致token消耗越来越大（我们之前讨论过这个风险）。
        # 注意顺序：必须先调用generate_summary生成摘要，再删除，不能反过来——
        # 删除之后原始内容就没了，没法再总结。
        if len(state['自由对话历史']) > 50:
            oldest_messages = state['自由对话历史'][:25]
            new_summary_piece = generate_summary(oldest_messages)

            if state['长期记忆摘要'] is None:
                state['长期记忆摘要'] = new_summary_piece
            else:
                state['长期记忆摘要'] = state['长期记忆摘要'] + "\n" + new_summary_piece

            state['自由对话历史'] = state['自由对话历史'][25:]

        return "", history, state

    # ============================================
    # 测评阶段
    # ============================================
    q_idx = state['q_idx']
    response = chain.invoke({"question": PHQ9_QUESTIONS[q_idx], "user_answer": user_input})
    ai_output = response.content

    score_match = re.search(r"得分:\s*([0-3])", ai_output)
    feedback_match = re.search(r"反馈:\s*([\s\S]*)", ai_output)
    score = int(score_match.group(1)) if score_match else 0
    feedback = feedback_match.group(1).strip() if feedback_match else "收到您的回答。"

    # 单独记录第9题的分数，不管总分多少，这个分数都要被记住，用于后面单独判断
    if q_idx == Q9_INDEX:
        state['q9_score'] = score

    state['total_score'] += score
    state['q_idx'] += 1
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": feedback})

    # 第9题单独触发：只要这一题分数>=1，立刻插入危机预警文案，
    # 不等测评结束、不等总分算出来，当场触发，不依赖模型是否"愿意"生成这句话
    q9_triggered_warning = (q_idx == Q9_INDEX and score >= 1)
    if q9_triggered_warning:
        history.append({"role": "assistant", "content": CRISIS_WARNING_TEXT})

    if state['q_idx'] < len(PHQ9_QUESTIONS):
        next_q = PHQ9_QUESTIONS[state['q_idx']]
        history.append({"role": "assistant", "content": f"下一题：{next_q}"})
    else:
        # 9题全部问完了。
        # 如果第9题刚好触发了预警，不要立刻生成测评摘要并结束——
        # 先进入"等待预警确认"这个中间状态，停下来等用户回应一次，
        # 真正的测评收尾逻辑被挪到了上面"等待预警确认"那个分支里。
        if q9_triggered_warning:
            state['等待预警确认'] = True
        else:
            # 没有触发预警，按原来的逻辑直接收尾
            state['is_finished'] = True
            risk_level = calculate_risk_level(state['total_score'], state['q9_score'])
            state['测评摘要'] = f"总分{state['total_score']}分，评估为{risk_level}"

            history.append({
                "role": "assistant",
                "content": f"测评完成！总分 {state['total_score']}。评估结果：{risk_level}。现在我们可以自由交流了。"
            })

    return "", history, state


# --- 5. UI 界面 ---
def get_initial_state():
    return (
        [{"role": "assistant", "content": "你好，开始测评：" + PHQ9_QUESTIONS[0]}],
        {
            'q_idx': 0,
            'total_score': 0,
            'q9_score': 0,
            'is_finished': False,
            '测评摘要': None,
            '自由对话历史': [],
            '长期记忆摘要': None,
            '等待预警确认': False
        }
    )


with gr.Blocks() as demo:
    chatbot = gr.Chatbot(label="心理咨询")
    msg = gr.Textbox()
    state = gr.State()
    msg.submit(chat_and_assess, [msg, chatbot, state], [msg, chatbot, state])
    demo.load(get_initial_state, None, [chatbot, state])

if __name__ == "__main__":
    demo.launch()