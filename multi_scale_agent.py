import os
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化 DeepSeek 客户端
api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

if not api_key:
    raise ValueError("未检测到 DEEPSEEK_API_KEY，请检查环境变量或 .env 文件配置！")

client = OpenAI(api_key=api_key, base_url=base_url)

# --- 标准量表定义 ---
PHQ9_QUESTIONS = [
    "1. 做任何事都提不起劲或没有乐趣？",
    "2. 感到心情低落、沮丧或绝望？",
    "3. 入睡困难、易醒或嗜睡？",
    "4. 感到疲倦或没有活力？",
    "5. 食欲不振或吃得太多？",
    "6. 觉得自己很糟、很失败，或让自己及家人失望？",
    "7. 思考或看报纸电视时，注意力很难集中？",
    "8. 动作或说话速度缓慢到别人都注意到了？或者相反，烦躁不安地到处走动？",
    "9. 常常有自我伤害或一了百了的想法？"
]

GAD7_QUESTIONS = [
    "1. 感到紧张、焦虑或急躁？",
    "2. 无法停止或控制担忧？",
    "3. 对各种各样的事情担忧过多？",
    "4. 很头疼，很难放松下来？",
    "5. 烦躁不安，以至于无法安静坐着？",
    "6. 容易被激怒或变得烦躁？",
    "7. 感到似乎有什么可怕的事情发生而害怕？"
]

SCORE_MAP = {"没有": 0, "有几天": 1, "一半以上时间": 2, "几乎天天": 3}


class MultiScaleMentalAgent:
    def __init__(self):
        # 状态生命周期: screening(分类分流) -> testing(量表答题) -> chat(自由心理对话)
        self.mode = "screening"
        self.current_scale = None   # "PHQ-9" 或 "GAD-7"
        self.questions = []         # 当前激活的题目库
        self.current_index = 0      # 当前题目索引
        self.scores = []            # 用户得分历史
        self.scale_report = ""      # 保存初筛报告文本

    def classify_intent(self, user_input: str) -> str:
        """调用 DeepSeek API 进行轻量级文本意图分类"""
        prompt = f"""
        你是一个专业的心理健康初筛助手。请分析用户输入的一段话，判断用户表现出的主要主观困扰更符合“抑郁倾向”还是“焦虑倾向”。
        
        用户的话: "{user_input}"
        
        请严格只输出以下三个标签之一，不要包含任何其他多余标点或解释：
        - DEPRESSION (如果用户提到：低落、提不起劲、没动力、悲伤、绝望、想哭、觉得自己很失败等)
        - ANXIETY (如果用户提到：紧张、害怕、焦虑、胡思乱想、静不下心、心慌、停不下来担忧等)
        - UNKNOWN (如果无法明确判断，或属于普通寒暄)
        """
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=10
            )
            return response.choices[0].message.content.strip().upper()
        except Exception as e:
            print(f"[警告] DeepSeek API 调用失败，启动降级容错机制: {e}")
            return "UNKNOWN"

    def chat_with_llm(self, user_input: str, history) -> str:
        """测评结束后的自由心理疏导对话"""
        # 构建适合心理咨询的系统提示词
        system_prompt = f"""
        你是一个温暖、充满同理心、专业的心理咨询师。
        刚才用户已经完成了 {self.current_scale} 心理初筛量表，测试结果提示存在【{self.scale_report_level}】。
        
        请遵守以下咨询原则：
        1. 保持倾听和高度共情，认可用户的痛苦和不容易，不要生硬地讲大道理。
        2. 使用开放式提问，引导用户说出内心的真实感受和生活压力源。
        3. 语言要轻柔、温暖、安全。如果用户有严重自残想法，请温柔地给与危机干预并建议寻求医院现实帮助。
        """
        
        # 将 Gradio 的标准历史记录转换为 OpenAI API 格式
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # 追加当前用户的输入
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.7,  # 提升聊天阶段的语言丰富度
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"抱歉，我刚才走神了，能请你再说一遍吗？(错误信息: {e})"

    def process_message(self, user_input: str, history) -> str:
        """控制流主函数"""
        user_input = user_input.strip()
        
        if self.mode != "chat" and not user_input:
            return "请对当前题目做出回应，您可以回答：【没有】、【有几天】、【一半以上时间】或【几乎天天】。"

        # 阶段 1：分类初筛分流路由
        if self.mode == "screening":
            intent = self.classify_intent(user_input)
            if intent == "ANXIETY":
                self.current_scale = "GAD-7"
                self.questions = GAD7_QUESTIONS
                self.mode = "testing"
                return (f"听起来你此刻被这些紧绷和担忧的感觉拉扯着，真的很不容易。\n\n"
                        f"接下来为了更客观地了解，我们将进入 **GAD-7 焦虑量表** 的评估。\n"
                        f"**【答题规范】** 请根据您**过去两周**的实际情况，选择以下一句话回答：\n"
                        f"👉 *没有 / 有几天 / 一半以上时间 / 几乎天天*\n\n"
                        f"现在开始第一题：\n{self.questions[0]}")
            else:
                self.current_scale = "PHQ-9"
                self.questions = PHQ9_QUESTIONS
                self.mode = "testing"
                return (f"感谢你愿意向我吐露这些沉重和无力的感受。这需要很大的勇气。\n\n"
                        f"为了更好地支持你，接下来我们通过 **PHQ-9 抑郁量表** 来做个初筛。\n"
                        f"**【答题规范】** 请根据您**过去两周**的实际情况，选择以下一句话回答：\n"
                        f"👉 *没有 / 有几天 / 一半以上时间 / 几乎天天*\n\n"
                        f"现在开始第一题：\n{self.questions[0]}")

        # 阶段 2：量表循环问答控制流
        elif self.mode == "testing":
            matched_score = 0
            for keyword, score_value in SCORE_MAP.items():
                if keyword in user_input:
                    matched_score = score_value
                    break
            
            self.scores.append(matched_score)
            self.current_index += 1
            
            if self.current_index < len(self.questions):
                return self.questions[self.current_index]
            else:
                # 答题结束，生成报告并无缝切换至自由聊天状态
                self.mode = "chat"
                total_score = sum(self.scores)
                return self.generate_report(total_score)

        # 阶段 3：自由心理对话模式（接管后续所有的输入）
        elif self.mode == "chat":
            return self.chat_with_llm(user_input, history)

        return "系统处于未知状态。"

    def generate_report(self, total_score: int) -> str:
        """生成初筛报告并锁定等级状态"""
        if self.current_scale == "PHQ-9":
            if total_score >= 20: level = "重度抑郁倾向"
            elif total_score >= 15: level = "中重度抑郁倾向"
            elif total_score >= 10: level = "中度抑郁倾向"
            elif total_score >= 5: level = "轻度抑郁倾向"
            else: level = "无抑郁倾向"
        else:
            if total_score >= 15: level = "重度焦虑倾向"
            elif total_score >= 10: level = "中度焦虑倾向"
            elif total_score >= 5: level = "轻度焦虑倾向"
            else: level = "无焦虑倾向"
            
        self.scale_report_level = level  # 注入缓存供 LLM 角色认知使用
        
        return (f"### 📊 {self.current_scale} 心理健康初筛报告\n"
                f"--- \n"
                f"**测评总分**：`{total_score} 分` \n"
                f"**初步评估结果**：属于 **【{level}】**\n\n"
                f"--- \n"
                f"🧠 **[已为您开启自由倾诉通道]** \n"
                f"看着这个分数，你心里也许会有一些沉重。没关系，现在所有的量表已经测完了。接下来，你可以把我当成你的私人树洞，自由地和我聊聊任何让你感到困扰、委屈或痛苦的人和事。我会一直在这里听着。")


# --- Gradio 界面交互逻辑 ---
def create_ui():
    agent_instance = MultiScaleMentalAgent()
    initial_greeting = "你好！我是你的 AI 心理健康助手。最近有什么让你感到困扰的事情吗？或者，你今天的心情怎么样？可以和我聊聊吗？"
    agent_instance.mode = "screening"
    
    def chatbot_respond(user_message, history):
        if not user_message:
            return "", history
            
        # 传入 history 以便让自由对话模块继承多轮上下文
        agent_reply = agent_instance.process_message(user_message, history)
        
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": agent_reply})
        return "", history

    def reset_agent():
        nonlocal agent_instance
        agent_instance = MultiScaleMentalAgent()
        agent_instance.mode = "screening"
        return [{"role": "assistant", "content": initial_greeting}]

    with gr.Blocks(title="多模态心理健康 Agent 系统 V3") as demo:
        gr.Markdown("""
        # 🧠 多模态心理健康对话 Agent 系统 (Day 8 自由对话迭代版)
        本系统不仅支持由 **DeepSeek 驱动的双量表自动分流**，而且在测评结束后将**自动为您接通 AI 心理倾诉专属通道**，支持无限轮次的暖心对话与心理疏导。
        """)
        
        chatbot = gr.Chatbot(
            value=[{"role": "assistant", "content": initial_greeting}],
            height=500
        )
        
        with gr.Row():
            msg_input = gr.Textbox(
                placeholder="请输入感受、回答量表（没有/有几天等），或在测评结束后自由聊天...",
                scale=8,
                container=False
            )
            submit_btn = gr.Button("发送", variant="primary", scale=1)
            
        with gr.Row():
            reset_btn = gr.Button("🔄 重置评估方案", variant="secondary")
            
        gr.Examples(
            examples=["没有", "有几天", "一半以上时间", "几乎天天"],
            inputs=msg_input,
            label="💡 快捷作答辅助点击"
        )

        msg_input.submit(chatbot_respond, [msg_input, chatbot], [msg_input, chatbot])
        submit_btn.click(chatbot_respond, [msg_input, chatbot], [msg_input, chatbot])
        reset_btn.click(reset_agent, outputs=[chatbot])
        
    return demo


if __name__ == "__main__":
    app = create_ui()
    app.launch(
        server_name="127.0.0.1", 
        server_port=7860, 
        share=False,
        theme=gr.themes.Soft()
    )