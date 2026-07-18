from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# TODO 1: 定义 State
# 提示：State 是一个 TypedDict，先只放一个字段就行，比如 messages
# 想一想：为什么要用 TypedDict 而不是普通的 dict 或 class？
class State(TypedDict):
      message:list
# TODO 2: 写一个最简单的 node 函数
# 提示：node 是一个函数，输入是 State，输出也是（一部分）State
# 先不接 API，直接 return 一句固定文本，验证流程能不能跑通
def hello_node1(state: State):
    return {"message":state["message"]+[4]}
def hello_node2(state: State):
    return {"message":state["message"]+[5]}
# TODO 3: 初始化图
graph_builder = StateGraph(State)

# TODO 4: 把 node 加进去，并且接好 START -> node -> END
# 提示：需要用到 add_node / add_edge
graph_builder.add_node("hello_node1",hello_node1)
graph_builder.add_node("hello_node2",hello_node2)
graph_builder.add_edge(START,"hello_node1")
graph_builder.add_edge("hello_node1","hello_node2")
graph_builder.add_edge("hello_node2",END)
# TODO 5: 编译
agent=graph_builder.compile()

# TODO 6: 跑一次
if __name__ == "__main__":
    result = agent.invoke({"message":[1,2,3]})  # graph.invoke(...)
    print(result)
    