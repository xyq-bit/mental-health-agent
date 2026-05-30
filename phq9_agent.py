import os
import re
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# --- 1. 加载环境变量 ---
# 会自动查找项目根目录下的 .env 文件
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# 1. 配置 DeepSeek 官方 API
os.environ["OPENAI_API_KEY"] =  api_key
os.environ["OPENAI_BASE_URL"] = "https://api.deepseek.com"
os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com"

# 2. 初始化最新满血版大脑
llm = ChatOpenAI(
    model_name="deepseek-v4-pro",
    temperature=0.3
)

# 3. 硬编码 PHQ-9 标准 9 题量表 [cite: 13]
phq9_questions = [
    "做任何事都提不起劲或没有乐趣？",
    "感到心情低落、沮丧或绝望？",
    "入睡困难、睡不安稳或睡得太多？",
    "感到疲倦或没有活力？",
    "食欲不振或吃得太多？",
    "觉得自己很糟，或觉得自己很失败，或让自己及家人失望？",
    "专注于别的事有困难，例如看报纸或看电视？",
    "行动或说话速度慢到别人已经察觉？或者正好相反，烦躁不安、动来动去、甚至比平常更坐立不安？",
    "脑海中曾冒出过‘不如死掉算了’或‘用某种方式伤害自己’的念头？"
]

# 4. 构建专门用于打分和共情回复的系统 Prompt
system_template = """你是一位专业的心理评估助手。当前用户正在进行 PHQ-9 抑郁症临床筛查量表测评。

标准分值参考：
- 0分：完全不会 / 毫无
- 1分：有几天 / 偶尔
- 2分：一半以上天数 / 经常
- 3分：几乎天天 / 总是

请根据用户针对当前问题的描述，做两件事：
1. 智能化评估出最符合的标准分值（严格从 0, 1, 2, 3 中选择一个整数）。
2. 给出一段温和、具有极高共情力、且简短的倾听式心理安慰。

【注意】你的输出格式必须严格按照下方结构，不要附带任何多余的解释，以便系统解析：
得分: [数字]
反馈: [你的温和回复]"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("human", "【当前评估问题】：{question}\n【用户的真实回答】：{user_answer}")
])

# 🔥 【LCEL 新版核心改动 1】：使用管道符 | 将 Prompt 和 LLM 像工厂流水线一样无缝拼装
chain = prompt_template | llm

# 5. 主业务流程控制
print("==================================================")
print("🧠 多模态心理健康 Agent - Day 3 PHQ-9 量表测评 (LCEL版) 启动")
print("评测说明：请根据您过去两周的实际情况真实回答。")
print("==================================================\n")

total_score = 0

# 顺序循环问完 9 道题 [cite: 13]
for i, question in enumerate(phq9_questions, 1):
    print(f"【问题 {i}/9】{question}")
    user_answer = input("您的回答: ")
    print("Agent 正在深度倾听...")
    
    # 🔥 【LCEL 新版核心改动 2】：不再手动转 message，直接将字典丢入 chain.invoke()
    # 它会自动按照流水线顺序：把字典填入 Prompt -> 送给大模型 -> 返回完整的 Response 对象
    response = chain.invoke({
        "question": question, 
        "user_answer": user_answer
    })
    
    # 🔥 【LCEL 新版核心改动 3】：通过 response.content 优雅地抽取出文本内容
    ai_output = response.content
    
    # 运用正则表达式精准提取模型给出的分数与评语
    score_match = re.search(r"得分:\s*([0-3])", ai_output)
    feedback_match = re.search(r"反馈:\s*([\s\S]*)", ai_output)
    
    current_score = int(score_match.group(1)) if score_match else 0
    feedback_text = feedback_match.group(1).strip() if feedback_match else "感谢您的分享，我们继续下一题。"
    
    total_score += current_score
    
    print(f"Agent: {feedback_text}")
    print(f"（系统内部记录：本题计 {current_score} 分，当前总分：{total_score} 分）\n")

# 6. 最终计算总分并给出标准风险提示 [cite: 13]
print("==================================================")
print("📊 测评结束！正在生成您的 PHQ-9 心理健康报告...")
print("==================================================")
print(f"您的最终总分为：{total_score} 分")

if total_score <= 4:
    risk_level = "没有抑郁倾向"
    advice = "您的心理状态非常健康，请继续保持良好的生活作息！"
elif total_score <= 9:
    risk_level = "轻度抑郁倾向"
    advice = "您最近可能有些疲惫或压力，建议适当放松，多与朋友倾诉。"
elif total_score <= 14:
    risk_level = "中度抑郁倾向"
    advice = "压力或负面情绪已经对您造成了一定困扰，可以考虑寻求学校心理咨询中心的日常疏导。"
elif total_score <= 19:
    risk_level = "中重度抑郁倾向"
    advice = "情绪积压较为严重，强烈建议前往专业机构进行科学的心理评估与调整。"
else:
    risk_level = "重度抑郁倾向"
    advice = "当前心理风险极高。请记住，您不是孤单一人，请立刻联系专业的精神卫生专家或医疗机构寻求帮助。"

print(f"风险评估：{risk_level}")
print(f"贴心建议：{advice}\n")
print("提示：代码已全面升级为官方标准 LCEL 架构，请保存并运行测试！")