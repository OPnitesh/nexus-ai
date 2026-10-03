from langgraph.graph import END, START, StateGraph

from app.modules.agents.graph.state import ChatState


def build_graph(checkpointer=None):
    builder = StateGraph(ChatState)
    builder.add_node("start", lambda state: state)
    builder.add_edge(START, "start")
    builder.add_edge("start", END)
    return builder.compile(checkpointer=checkpointer)
