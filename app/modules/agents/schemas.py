from pydantic import BaseModel


# Defines the request and response contract for the agent API.
class ChatRequest(BaseModel):
    message: str
    thread_id: str


class ChatResponse(BaseModel):
    response: str