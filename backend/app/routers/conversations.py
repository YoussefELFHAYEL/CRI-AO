"""
CRI-RSK Chatbot — Conversations router.
"""

from fastapi import APIRouter

from app.database.models import ConversationCreate, ConversationResponse
from app.database.supabase_client import (
    create_conversation,
    get_conversation,
    get_conversation_messages,
)

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse)
async def create_new_conversation(body: ConversationCreate):
    """Create a new conversation."""
    conversation = create_conversation(
        agent_type=body.agent_type.value,
        language=body.language,
        user_phone=body.user_phone,
    )
    return conversation


@router.get("/conversations/{conversation_id}")
async def get_conversation_detail(conversation_id: str):
    """Get conversation details with messages."""
    conversation = get_conversation(conversation_id)
    if not conversation:
        return {"error": "Conversation not found"}
    messages = get_conversation_messages(conversation_id)
    return {
        "conversation": conversation,
        "messages": messages,
    }
