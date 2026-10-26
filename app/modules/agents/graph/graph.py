from langgraph.graph import END, START, StateGraph

from app.modules.agents.graph.nodes.llm_node import llm_node
from app.modules.agents.graph.state import ChatState


def build_graph(checkpointer=None):
    builder = StateGraph(ChatState)

    builder.add_node("llm", llm_node)

    builder.add_edge(START, "llm")
    builder.add_edge("llm", END)

    return builder.compile(checkpointer=checkpointer)