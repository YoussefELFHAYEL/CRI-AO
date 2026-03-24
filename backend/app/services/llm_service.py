"""
CRI-RSK Chatbot — LLM service.
Wrapper around Google Gemini for response generation.
"""

import logging
from typing import Optional

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


def _get_client(api_key: str) -> genai.Client:
    """Create a Gemini client."""
    return genai.Client(api_key=api_key)


async def generate_response(
    query: str,
    context: str,
    system_prompt: str,
    language: str,
    llm_model: str = "gemini-2.5-flash",
    api_key: str = "",
    conversation_history: Optional[list[dict]] = None,
) -> dict:
    """
    Generate a response using Gemini with RAG context.

    Args:
        query: User's question
        context: Retrieved context from RAG pipeline
        system_prompt: System prompt for the agent
        language: Detected language
        llm_model: Gemini model name
        api_key: Gemini API key
        conversation_history: Previous messages for context

    Returns:
        Dict with 'response' and 'is_fallback' flag.
    """
    client = _get_client(api_key)

    # Build conversation contents
    contents = []

    # Add conversation history (last 6 messages max)
    if conversation_history:
        recent = conversation_history[-6:]
        for msg in recent:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])],
                )
            )

    # Build the user message with context
    if context.strip():
        user_content = (
            f"Contexte de la base de connaissances :\n"
            f"---\n{context}\n---\n\n"
            f"Question de l'utilisateur : {query}"
        )
    else:
        user_content = f"Question de l'utilisateur : {query}"

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_content)],
        )
    )

    try:
        response = client.models.generate_content(
            model=llm_model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
                max_output_tokens=1500,
            ),
        )

        response_text = response.text.strip() if response.text else ""

        # Check if the response indicates no information was found
        is_fallback = _is_fallback_response(response_text, language)

        if is_fallback:
            response_text = _get_fallback_message(language)

        return {
            "response": response_text,
            "is_fallback": is_fallback,
        }

    except Exception as e:
        logger.error(f"Gemini generation failed: {e}")
        return {
            "response": _get_fallback_message(language),
            "is_fallback": True,
        }


def _is_fallback_response(response: str, language: str) -> bool:
    """
    Detect if the LLM's response indicates it doesn't have the information.
    Uses keyword matching to catch common "I don't know" patterns.
    """
    fallback_indicators = [
        # French
        "je n'ai pas trouvé",
        "je ne dispose pas",
        "je n'ai pas d'information",
        "pas trouvé d'information",
        "je ne suis pas en mesure",
        "pas dans ma base",
        "aucune information",
        # Arabic
        "لم أجد",
        "لا أملك معلومات",
        "لا تتوفر لدي",
        "ليس لدي معلومات",
        # English
        "i don't have information",
        "i couldn't find",
        "no information available",
        "i'm unable to find",
        "not in my knowledge",
    ]
    response_lower = response.lower()
    return any(
        indicator in response_lower for indicator in fallback_indicators
    )


def _get_fallback_message(language: str) -> str:
    """Return the appropriate fallback message by language."""
    fallbacks = {
        "fr": (
            "Je n'ai pas trouvé d'information précise sur ce sujet. "
            "Pour une réponse personnalisée, contactez le CRI-RSK :\n"
            "📞 05 37 77 64 00\n"
            "📧 contact@rabatinvest.ma"
        ),
        "ar": (
            "لم أجد معلومات دقيقة حول هذا الموضوع.\n"
            "للتواصل مع مركز الاستثمار الجهوي:\n"
            "📞 05 37 77 64 00\n"
            "📧 contact@rabatinvest.ma"
        ),
        "en": (
            "I couldn't find precise information on this topic. "
            "Please contact CRI-RSK directly:\n"
            "📞 05 37 77 64 00\n"
            "📧 contact@rabatinvest.ma"
        ),
    }
    return fallbacks.get(language, fallbacks["fr"])
