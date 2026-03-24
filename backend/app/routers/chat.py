"""
CRI-RSK Chatbot — Chat router (main endpoint).
Handles the full chat flow: language detection, query transform,
RAG retrieval, incitations flow, OTP, escalation, and fallback.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Request

from app.database.models import (
    AgentType,
    ChatRequest,
    ChatResponse,
)
from app.database.supabase_client import (
    create_conversation,
    get_conversation,
    save_message,
    save_unknown_question,
    get_conversation_messages,
)
from app.services.language_detect import detect_language
from app.services.escalation import check_escalation, get_escalation_message
from app.services.incitations_flow import (
    is_incitation_query,
    is_in_flow,
    get_incitation_step,
)
from app.services.dossier_tracking import (
    is_tracking_query,
    is_in_tracking_flow,
    process_tracking_step,
)
from app.services.rag_pipeline import run_rag_pipeline

logger = logging.getLogger(__name__)

router = APIRouter()

# Track fallback counts per conversation (in-memory for demo)
_fallback_counts: dict[str, int] = {}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest):
    """
    Main chat endpoint.
    Processes user message through the RAG pipeline and returns a response.
    """
    settings = request.app.state.settings

    # 1. Detect language
    language = body.language or detect_language(body.message)

    # 2. Get or create conversation
    if body.conversation_id:
        conversation = get_conversation(body.conversation_id)
        if not conversation:
            conversation = create_conversation(
                agent_type=body.agent_type.value,
                language=language,
            )
    else:
        conversation = create_conversation(
            agent_type=body.agent_type.value,
            language=language,
        )

    conversation_id = conversation["id"]

    # 3. Save user message
    user_msg = save_message(
        conversation_id=conversation_id,
        role="user",
        content=body.message,
        language=language,
    )

    # 4. Check for human escalation trigger
    fallback_count = _fallback_counts.get(conversation_id, 0)
    if check_escalation(body.message, fallback_count):
        escalation_msg = get_escalation_message(language)
        bot_msg = save_message(
            conversation_id=conversation_id,
            role="bot",
            content=escalation_msg,
            language=language,
        )
        return ChatResponse(
            response=escalation_msg,
            conversation_id=conversation_id,
            message_id=bot_msg["id"],
            language=language,
            agent_type=body.agent_type,
            is_escalation=True,
        )

    # 5. Check for dossier tracking flow (public agent)
    #    Either a new trigger OR continuation of an existing tracking flow
    if body.agent_type == AgentType.PUBLIC and (
        is_tracking_query(body.message) or is_in_tracking_flow(conversation_id)
    ):
        tracking_result = process_tracking_step(
            message=body.message,
            conversation_id=conversation_id,
            language=language,
        )
        bot_msg = save_message(
            conversation_id=conversation_id,
            role="bot",
            content=tracking_result["response"],
            language=language,
        )
        return ChatResponse(
            response=tracking_result["response"],
            conversation_id=conversation_id,
            message_id=bot_msg["id"],
            language=language,
            agent_type=body.agent_type,
            requires_otp=tracking_result.get("requires_otp", False),
            dossier_reference=tracking_result.get("dossier_reference"),
            otp_code=tracking_result.get("otp_code"),
        )

    # 6. Check for incitations flow (public agent only)
    #    Either a new trigger OR continuation of an existing flow
    if body.agent_type == AgentType.PUBLIC and (
        is_incitation_query(body.message) or is_in_flow(conversation_id)
    ):
        step_response = get_incitation_step(body.message, conversation_id)
        bot_msg = save_message(
            conversation_id=conversation_id,
            role="bot",
            content=step_response.question,
            language=language,
        )
        return ChatResponse(
            response=step_response.question,
            conversation_id=conversation_id,
            message_id=bot_msg["id"],
            language=language,
            agent_type=body.agent_type,
            buttons=[
                {"label": opt.label, "value": opt.value, "emoji": opt.emoji}
                for opt in step_response.options
            ]
            if step_response.options
            else None,
        )

    # 6. Run RAG pipeline
    # Get conversation history for context
    history = get_conversation_messages(conversation_id)
    history_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in history[:-1]  # Exclude the just-saved user message
    ]

    rag_result = await run_rag_pipeline(
        query=body.message,
        agent_type=body.agent_type.value,
        language=language,
        settings=settings,
        vectorstore=request.app.state.vectorstore,
        bm25_index=request.app.state.bm25_index,
        bm25_docs=request.app.state.bm25_docs,
        conversation_history=history_messages,
    )

    # 7. Handle fallback
    is_fallback = rag_result.get("is_fallback", False)
    if is_fallback:
        _fallback_counts[conversation_id] = fallback_count + 1
        save_unknown_question(
            question=body.message,
            suggested_answer=rag_result.get("response"),
        )
    else:
        # Reset fallback counter on successful answer
        _fallback_counts[conversation_id] = 0

    # 8. Save bot response
    bot_msg = save_message(
        conversation_id=conversation_id,
        role="bot",
        content=rag_result["response"],
        language=language,
    )

    return ChatResponse(
        response=rag_result["response"],
        conversation_id=conversation_id,
        message_id=bot_msg["id"],
        language=language,
        agent_type=body.agent_type,
        is_fallback=is_fallback,
    )
