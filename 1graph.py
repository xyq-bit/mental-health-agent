"""
心理健康 Agent - Day 22-23 骨架代码
对应《心理健康Agent_Day22-23_更新版》文档第四节
用途：验证路由路径，节点内部为占位逻辑
"""
#Python 的内置库，用于和操作系统（Operating System）打交道，比如读取系统变量、查找文件路径。
import os
import json
from langgraph.graph import StateGraph, START, END
#负责把 LangGraph 的运行状态持久化保存到 SQLite 数据库
from langgraph.checkpoint.sqlite import SqliteSaver  
from typing import TypedDict, List, Optional
#第三方库，用来方便地调用支持 OpenAI 协议的所有 AI 接口（包括 DeepSeek）。
from openai import OpenAI
#第三方库，专门用来加载 .env 文件。它能帮你把 .env 文件里的配置转变成 Python 程序可以直接读取的“环境变量”。
from dotenv import load_dotenv
from typing import Annotated, List

# 1. 读取 .env 文件中的环境变量并写入当初程序的系统环境变量——os.environ文件（程序启动时，操作系统会把当前系统的环境变量复制一份到environ文件，程序执行时候只会去environ文件内找）
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

PHQ9_QUESTIONS = [
    "",
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

# ── State ──────────────────────────────────────────
def append_messages(old: List[dict], new: List[dict]) -> List[dict]:
    if len(new) > 0 and new[0].get("__reset__"):
        # 替换模式：去掉标记头，直接返回剩余内容
        return new[1:]
    return old + new

class AgentState(TypedDict):
    username: str
    user_data_path: str       #留作以后扩展，暂时不需要
    phase: int                # 0=登录 1=测评 2=危机 3=自由对话
    waiting: bool             # False=该问新题  True=该给答案打分/等待危机回复
    q_idx: int
    total_score: int
    q9_score: int
    crisis_flag: bool
    #reducer是一个状态更新机制，接收两个参数（旧值、新值），返回一个新值”的 Python 函数
    #定义一个名为 messages 的状态变量并对其进行注释Annotated[基础类型, 附加信息1, 附加信息2, ...]，
    #它的类型是一个“字典列表”（存储聊天记录），
    #如果没有reducer默认是覆盖；现在指定它的更新规则为“追加（add_messages）”，而不是“覆盖”。
    messages: Annotated[List[dict], append_messages] 
    assessment_result: Optional[str]
    long_term_summary: Optional[str]


# ── 节点占位函数 ────────────────────────────────────

def node_init(state: AgentState) -> dict:
    if state["phase"] == 0:
        print(f"欢迎新用户 {state['username']}")
        return {"phase": 1}
    else:
        # 老用户，什么都不改，直接透传
        return {}

def node_memory_compress(state: AgentState):
    messages = state["messages"]
    old_messages = messages[:15]
    remain_messages = messages[15:]

    old_text = "\n".join(
        [f"{m['role']}:{m['content']}" for m in old_messages]
    )

    prompt = f"""请总结以下心理咨询历史。缩减到50字左右
要求：
- 保留用户重要心理状态
- 保留长期事件
- 保留用户习惯和偏好
- 删除无意义聊天

历史：
{old_text}
"""
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    summary = response.choices[0].message.content

    # 用 __reset__ 标记通知 reducer 执行替换而不是追加
    return {
        "messages": [{"__reset__": True}] + remain_messages,
        "long_term_summary": summary
    }

def node_continue(state: AgentState) -> dict:
    return {}

def node_question(state: AgentState) -> dict:
    print(f"[question] q_idx={state['q_idx']}")
    print(f"{PHQ9_QUESTIONS[state['q_idx']]}")
    return {
        "waiting": True,
        "messages":  [ {"role": "assistant", "content": f"{PHQ9_QUESTIONS[state['q_idx']]}"}]
    }


def node_score(state: AgentState) -> dict:
    q_idx = state["q_idx"]
    question_text = PHQ9_QUESTIONS[q_idx]
    user_answer = state["messages"][-1]["content"]

    prompt = f"""你是 PHQ-9 量表打分助手。
题目：{question_text}
用户回答：{user_answer}

PHQ-9 评分标准：
0 = 完全没有
1 = 有几天
2 = 超过一半的天数
3 = 几乎每天

只输出一个数字（0/1/2/3），不要输出任何其他内容。"""
    
    try:
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
    except Exception as e:
        raise RuntimeError(f"LLM打分失败，请重试: {e}")

    try:
        score = int(response.choices[0].message.content.strip())
        score = max(0, min(3, score))
    except ValueError:
        raise RuntimeError(f"LLM返回值无法解析，请重试: {response.choices[0].message.content}")

    new_total = state["total_score"] + score
    new_q9 = score if q_idx == 9 else state["q9_score"]

    print(f"[score] 第{q_idx}题得分={score} total={new_total}")
    return {
        "waiting": False,
        "total_score": new_total,
        "q9_score": new_q9,
    }


def node_next(state: AgentState) -> dict:
    
    return {"q_idx": state["q_idx"] + 1}


def node_crisis_warning(state: AgentState) -> dict:
    print("[crisis_warning]:了解到您有自杀倾向，能告诉我你为什么会这么想吗")
    return {"crisis_flag": True, "phase": 2, "waiting": True,
            "messages": 
            [{"role": "assistant", "content": "[crisis_warning]: 了解到您有自杀倾向，能告诉我你为什么会这么想吗？"}]
         }



def node_crisis_reply(state: AgentState) -> dict:
    crisis_warning=state["messages"][-2]["content"]
    user_answer = state["messages"][-1]["content"]
    prompt = f"""你是心理疏导助手。用户现在有了自杀想法，
    以下是对话记录：
    "role": "assistant", "content": "{crisis_warning}"
    "role": "user","content":"{user_answer}"
     请给用户安慰回答，让用户不要有自杀想法。简明扼要说
    """   
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
    except Exception as e:
        raise RuntimeError(f"LLM回复预警失败，请重试: {e}")  
    reply = response.choices[0].message.content
    print(f"[crisis_reply]:{reply}")
    return {
            "waiting":False,
            "crisis_flag": False,
            "messages":[{"role":"assistant","content":f"{reply}"}]
            }


def node_assessment_end(state: AgentState) -> dict:
    print(f"[assessment_end] total_score={state['total_score']}")
    print("接下来我们开始自由对话吧")
    return {
        "phase": 3,
        "assessment_result": f"总分{state['total_score']}分",
       
        }


def node_chat(state: AgentState) -> dict:
    system_msg = {"role": "system", "content": f"""(你是一个心理健康支持助手。
              用户刚完成了PHQ-9测评，结果是：{state["assessment_result"]}。
              长期记忆摘要：{state["long_term_summary"]})；回复要简明扼要，50字以内"""}
   
    try:
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[system_msg] + state["messages"],
            temperature=0.6,
        )
    except Exception as e:
        raise RuntimeError(f"自由对话阶段LLM回复失败erro:{e}")
    reply = response.choices[0].message.content
    print(reply)
    return {
        "messages": [{"role": "assistant", "content":reply} ]
    }


# ── 路由函数 ────────────────────────────────────────

def ifcompress_router(state:AgentState) -> str:
#在init后，入口前添加一个判断是否对话历史过长的逻辑
    if len(state["messages"]) > 30:
        return "memory_compress"
    else: 
        return "continue"
    
def entry_router(state: AgentState) -> str:
    
     
    ph, wt = state["phase"], state["waiting"]
    
    if ph == 1 and wt==False:
        return "question"
    if ph == 1 and wt==True:
        return "score"
#由于langgraph的节点执行是原子操作，所以不会出现 phase==2 and waiting==False；便去除了这个分支
    if ph == 2 and wt:
        return "crisis_reply"
    if ph == 3:
        return "chat"


def score_router(state: AgentState) -> str:
    if state["q9_score"] >= 1 and state["q_idx"]==9:
        return "crisis_warning"
    if state["q9_score"] == 0 and state["q_idx"] >= 9 :
        return "assessment_end"
    return "next"


# ── 图构建 ──────────────────────────────────────────

builder = StateGraph(AgentState)

builder.add_node("init", node_init)
builder.add_node("memory_compress",node_memory_compress)
builder.add_node("continue",node_continue)
builder.add_node("question", node_question)
builder.add_node("score", node_score)
builder.add_node("next", node_next)
builder.add_node("crisis_warning", node_crisis_warning)
builder.add_node("crisis_reply", node_crisis_reply)
builder.add_node("assessment_end", node_assessment_end)
builder.add_node("chat", node_chat)

builder.add_edge(
    START,
    "init"
)
builder.add_conditional_edges(
    "init",
    ifcompress_router,
    {
         "memory_compress": "memory_compress",
         "continue": "continue",  
    }
)
builder.add_conditional_edges(
    "memory_compress",
    entry_router,
    {
        "question": "question",
        "score": "score",
        "crisis_reply": "crisis_reply",
        "chat": "chat",
    },
)
builder.add_conditional_edges(
    "continue",
    entry_router,
    {
        "question": "question",
        "score": "score",
        "crisis_reply": "crisis_reply",
        "chat": "chat",
    },
)


builder.add_edge("question", END)

builder.add_conditional_edges(
    "score",
    score_router,
    {
        "next": "next",
        "assessment_end": "assessment_end",
        "crisis_warning": "crisis_warning",
    },
)

builder.add_edge("next", "question")
builder.add_edge("crisis_warning", END)
builder.add_edge("crisis_reply", "assessment_end")
builder.add_edge("assessment_end", END)
builder.add_edge("chat", END)

with SqliteSaver.from_conn_string("data/mental_agent.db") as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)
    
    png_bytes = graph.get_graph().draw_mermaid_png()
    with open("mental_health_graph.png", "wb") as f:
        f.write(png_bytes)
    print("状态图已保存为 mental_health_graph.png")

    if __name__ == "__main__":
         username = "test_user_02"
         config = {"configurable": {"thread_id": username}}
         initial_state: AgentState = {
             "username": username,   
             "phase": 0,    #标记当前阶段
             "waiting": False,    #标记是否等待用户回复
             "q_idx": 1,          #题号
             "total_score": 0,     #总分
             "q9_score": 0,         #第九题分数
             "crisis_flag": False,     #自杀预警
             "messages": [],          #对话记录
             "assessment_result": "",     #测评结果
             "long_term_summary": "",      #长期记忆摘要
         }
    # 第一次invoke，问第1题
         result = graph.invoke(initial_state, config=config)

# 循环：用户回答 -> 打分+问下一题
         while True:
             current = graph.get_state(config)
            #自杀预警回复跑图
             if current.values["crisis_flag"] == True:
                 user_input = input("\n👤 用户: ")
                 try:
                    # 只传新消息，reducer 自动追加到 state
                    result = graph.invoke(
                        {"messages": [{"role": "user", "content": user_input}]},
                        config=config
                    )
                 except RuntimeError as e:
                     print(f"LLM回复出错：{e}")
                 continue  # 跳过下面的普通输入


             user_input = input("\n👤 用户: ")
            
             try:
                 # 只传新消息，reducer 自动追加到 state
                 result = graph.invoke(
                     {"messages": [{"role": "user", "content": user_input}]},
                     config=config
                 )
             except RuntimeError as e:
                 print(f"测评出错：{e}")
                 break
     