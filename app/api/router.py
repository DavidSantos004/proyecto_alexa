from fastapi import APIRouter

from app.api.dependencies import build_chat_service

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/chat")
def chat(body: dict):
    service = build_chat_service()
    return service.process_message(body["message"])
