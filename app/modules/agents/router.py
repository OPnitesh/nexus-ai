from fastapi import APIRouter, Depends

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.modules.agents.dependencies import get_checkpointer
from app.modules.agents.schemas import ChatRequest, ChatResponse
from app.modules.agents.service import run_agent


router = APIRouter(prefix="/agents", tags=["Agents"])


# Accepts a message and executes it within a persistent conversation thread.
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    checkpointer: AsyncPostgresSaver = Depends(get_checkpointer),
) -> ChatResponse:
    response = await run_agent(
        message=request.message,
        thread_id=request.thread_id,
        checkpointer=checkpointer,
    )

    return ChatResponse(response=response)