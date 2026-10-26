from langchain_core.messages import HumanMessage

from app.modules.agents.graph.graph import build_graph


# Executes the Nexus AI agent graph for a specific conversation thread.
async def run_agent(message: str, thread_id: str, checkpointer) -> str:
    graph = build_graph(checkpointer=checkpointer)

    result = await graph.ainvoke(
        {
            "messages": [HumanMessage(content=message)],
        },
        config={
            "configurable": {
                "thread_id": thread_id,
            }
        },
    )

    return result["messages"][-1].content