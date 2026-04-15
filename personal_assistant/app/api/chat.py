from fastapi import APIRouter
from app.schemas.chat_schemas import ChatRequest, ChatResponse
from app.services import chat_service
from langfuse.langchain import CallbackHandler
from app.trace.trace import langfuse

chat_router = APIRouter(prefix="/chat", tags=["chat"])

@chat_router.post("/",response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    handler = CallbackHandler()
    return await chat_service.chat(chat_request,handler)




