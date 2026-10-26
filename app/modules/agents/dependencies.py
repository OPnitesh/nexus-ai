from fastapi import Request
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver


# Returns the application-wide LangGraph checkpointer.
def get_checkpointer(request: Request) -> AsyncPostgresSaver:
    return request.app.state.checkpointer