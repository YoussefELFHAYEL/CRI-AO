"""
CRI-RSK Chatbot — Human escalation service.
Triggers escalation after 3 fallbacks or explicit keywords.
"""

import re

# Keywords that trigger immediate escalation (all languages)
ESCALATION_KEYWORDS = [
    # French
    r"agent\s*humain",
    r"parler\s*(à|a)\s*quelqu'?un",
    r"conseiller",
    r"humain",
    r"opérateur",
    # Arabic
    r"تحدث\s*مع\s*شخص",
    r"موظف",
    r"مساعدة\s*بشرية",
    # English
    r"human\s*agent",
    r"speak\s*to\s*someone",
    r"talk\s*to\s*a?\s*person",
    r"real\s*person",
]

_ESCALATION_PATTERN = re.compile(
    "|".join(ESCALATION_KEYWORDS), re.IGNORECASE
)

FALLBACK_THRESHOLD = 3


def check_escalation(message: str, fallback_count: int) -> bool:
    """
    Check if escalation should be triggered.
    Returns True if:
    - The user explicitly requests a human agent
    - The fallback count has reached the threshold
    """
    if fallback_count >= FALLBACK_THRESHOLD:
        return True

    if _ESCALATION_PATTERN.search(message):
        return True

    return False


def get_escalation_message(language: str) -> str:
    """Return the escalation message in the appropriate language."""
    ticket_id = f"{__import__('random').randint(1000, 9999):04d}"

    messages = {
        "fr": (
            "🚨 **Je ne peux pas répondre à cette question spécifique.** 🚨\n\n"
            "Je vous transfère à un de nos agents.\n"
            f"Votre numéro de ticket est le : **#TKT-2024-{ticket_id}**\n\n"
            "Un agent du CRI-RSK prendra le relais via WhatsApp d'ici 5 minutes."
        ),
        "ar": (
            "🚨 **لا يمكنني الإجابة على هذا السؤال المحدد.** 🚨\n\n"
            "سأقوم بنقل محادثتك إلى أحد عملائنا.\n"
            f"رقم التذكرة الخاص بك هو : **#TKT-2024-{ticket_id}**\n\n"
            "سيتولى أحد عملاء CRI-RSK المتابعة عبر WhatsApp في غضون 5 دقائق."
        ),
        "en": (
            "🚨 **I cannot answer this specific question.** 🚨\n\n"
            "I am transferring you to one of our agents.\n"
            f"Your ticket number is: **#TKT-2024-{ticket_id}**\n\n"
            "A CRI-RSK agent will take over via WhatsApp within 5 minutes."
        ),
    }

    return messages.get(language, messages["fr"])
