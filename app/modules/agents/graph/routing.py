from app.modules.agents.graph.state import ChatState


def route(state: ChatState) -> str:
    return "__end__"
