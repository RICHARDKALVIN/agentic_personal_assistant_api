from fastapi import APIRouter
from app.schemas.chat_schemas import ChatRequest, ChatResponse
from app.services import chat_service

chat_router = APIRouter(prefix="/chat", tags=["chat"])

@chat_router.post("/",response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    return await chat_service.chat(chat_request)




