"""
CRI-RSK Chatbot — Dossier tracking flow service.
Manages the multi-step flow: trigger → ask reference → OTP → display dossier.

States per conversation:
  - awaiting_reference: user needs to enter dossier reference
  - awaiting_otp: user needs to enter OTP code
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Demo dossier data (loaded once at startup)
# ---------------------------------------------------------------------------

_DEMO_DOSSIERS: dict[str, dict] = {}
_DATA_LOADED = False


def _load_demo_dossiers() -> None:
    """Load demo dossiers from JSON file."""
    global _DATA_LOADED
    if _DATA_LOADED:
        return

    data_file = Path(__file__).resolve().parent.parent.parent / "data" / "demo_dossiers.json"
    if data_file.exists():
        with open(data_file, "r", encoding="utf-8") as f:
            dossiers = json.load(f)
        for d in dossiers:
            _DEMO_DOSSIERS[d["reference"].upper()] = d
        logger.info(f"Loaded {len(_DEMO_DOSSIERS)} demo dossiers")
    else:
        logger.warning(f"Demo dossiers file not found: {data_file}")

    _DATA_LOADED = True


# Eagerly load
try:
    _load_demo_dossiers()
except Exception as e:
    logger.error(f"Failed to load demo dossiers: {e}")


# ---------------------------------------------------------------------------
# Flow state management
# ---------------------------------------------------------------------------

# Per-conversation tracking state
_tracking_state: dict[str, dict] = {}


# Trigger patterns
TRACKING_TRIGGERS = [
    r"suiv.*dossier",
    r"[ée]tat.*dossier",
    r"where\s*is\s*my\s*(?:file|case|dossier)",
    r"track.*(?:file|case|dossier)",
    r"تتبع\s*ملف",
    r"حالة\s*ملف",
    r"consulter.*dossier",
    r"v[ée]rifier.*dossier",
    r"numéro.*dossier",
    r"référence.*dossier",
    r"INV-\d{4}-\d{3,4}",  # Directly providing a reference should trigger it too
]

_TRACKING_PATTERN = re.compile(
    "|".join(TRACKING_TRIGGERS), re.IGNORECASE
)

# Reference pattern (INV-YYYY-NNN or INV-YYYY-NNNN)
_REF_PATTERN = re.compile(r"\bINV-\d{4}-\d{3,4}\b", re.IGNORECASE)


def is_tracking_query(message: str) -> bool:
    """Check if the message triggers the dossier tracking flow."""
    return bool(_TRACKING_PATTERN.search(message))


def is_in_tracking_flow(conversation_id: str) -> bool:
    """Check if a conversation is currently in the tracking flow."""
    return conversation_id in _tracking_state


def get_tracking_state(conversation_id: str) -> Optional[dict]:
    """Get the current tracking state for a conversation."""
    return _tracking_state.get(conversation_id)


def process_tracking_step(
    message: str,
    conversation_id: str,
    language: str = "fr",
) -> dict:
    """
    Process a step in the dossier tracking flow.

    Returns dict with:
      - response: str (bot message)
      - requires_otp: bool
      - dossier_reference: Optional[str]
      - otp_code: Optional[str] (demo mode only)
      - is_complete: bool
      - dossier: Optional[dict]
    """
    state = _tracking_state.get(conversation_id)

    # --- STEP 1: New tracking request — ask for reference ---
    if state is None or is_tracking_query(message):
        # Check if reference is already in the message
        ref_match = _REF_PATTERN.search(message)
        if ref_match:
            # User provided reference directly — skip to OTP
            reference = ref_match.group(0).upper()
            return _handle_reference_provided(conversation_id, reference, language)

        _tracking_state[conversation_id] = {
            "step": "awaiting_reference",
            "reference": None,
        }

        return {
            "response": _ask_reference_message(language),
            "requires_otp": False,
            "dossier_reference": None,
            "otp_code": None,
            "is_complete": False,
            "dossier": None,
        }

    # --- STEP 2: Awaiting reference number ---
    if state["step"] == "awaiting_reference":
        ref_match = _REF_PATTERN.search(message)
        if not ref_match:
            return {
                "response": _invalid_reference_message(language),
                "requires_otp": False,
                "dossier_reference": None,
                "otp_code": None,
                "is_complete": False,
                "dossier": None,
            }

        reference = ref_match.group(0).upper()
        return _handle_reference_provided(conversation_id, reference, language)

    # --- STEP 3: Awaiting OTP code ---
    if state["step"] == "awaiting_otp":
        reference = state["reference"]
        otp_input = message.strip()

        # Verify OTP
        from app.services.otp_service import verify_otp
        result = verify_otp(reference, otp_input)

        if result["verified"]:
            # Success — show dossier
            dossier = _DEMO_DOSSIERS.get(reference)
            del _tracking_state[conversation_id]

            if dossier:
                return {
                    "response": _format_dossier_detail(dossier, language),
                    "requires_otp": False,
                    "dossier_reference": reference,
                    "otp_code": None,
                    "is_complete": True,
                    "dossier": dossier,
                }
            else:
                return {
                    "response": _dossier_not_found_message(reference, language),
                    "requires_otp": False,
                    "dossier_reference": reference,
                    "otp_code": None,
                    "is_complete": True,
                    "dossier": None,
                }
        else:
            # Failed verification
            if result["attempts_remaining"] <= 0:
                del _tracking_state[conversation_id]
                return {
                    "response": result["message"],
                    "requires_otp": False,
                    "dossier_reference": reference,
                    "otp_code": None,
                    "is_complete": True,
                    "dossier": None,
                }

            return {
                "response": result["message"],
                "requires_otp": True,
                "dossier_reference": reference,
                "otp_code": None,
                "is_complete": False,
                "dossier": None,
            }

    # Unknown state — clean up
    del _tracking_state[conversation_id]
    return {
        "response": "Une erreur est survenue. Veuillez réessayer.",
        "requires_otp": False,
        "dossier_reference": None,
        "otp_code": None,
        "is_complete": True,
        "dossier": None,
    }


def _handle_reference_provided(
    conversation_id: str, reference: str, language: str
) -> dict:
    """Handle when a valid reference is provided — generate OTP."""
    _load_demo_dossiers()

    # Check if dossier exists
    if reference not in _DEMO_DOSSIERS:
        if conversation_id in _tracking_state:
            del _tracking_state[conversation_id]
        return {
            "response": _dossier_not_found_message(reference, language),
            "requires_otp": False,
            "dossier_reference": reference,
            "otp_code": None,
            "is_complete": True,
            "dossier": None,
        }

    # Generate OTP
    from app.services.otp_service import generate_otp
    otp_code = generate_otp(reference)

    _tracking_state[conversation_id] = {
        "step": "awaiting_otp",
        "reference": reference,
    }

    return {
        "response": _otp_sent_message(reference, language),
        "requires_otp": True,
        "dossier_reference": reference,
        "otp_code": otp_code,  # For demo display
        "is_complete": False,
        "dossier": None,
    }


# ---------------------------------------------------------------------------
# Message templates
# ---------------------------------------------------------------------------


def _ask_reference_message(language: str) -> str:
    messages = {
        "fr": (
            "📋 **Suivi de dossier**\n\n"
            "Pour consulter l'état de votre dossier, "
            "veuillez saisir votre numéro de référence.\n\n"
            "📝 Format : **INV-2024-001**"
        ),
        "ar": (
            "📋 **تتبع الملف**\n\n"
            "لعرض حالة ملفك، "
            "يرجى إدخال رقم المرجع الخاص بك.\n\n"
            "📝 الصيغة : **INV-2024-001**"
        ),
        "en": (
            "📋 **Dossier Tracking**\n\n"
            "To check the status of your file, "
            "please enter your reference number.\n\n"
            "📝 Format: **INV-2024-001**"
        ),
    }
    return messages.get(language, messages["fr"])


def _invalid_reference_message(language: str) -> str:
    messages = {
        "fr": (
            "❌ Référence invalide. Le format attendu est **INV-2024-001**.\n\n"
            "Veuillez réessayer."
        ),
        "ar": "❌ مرجع غير صالح. الصيغة المتوقعة هي **INV-2024-001**.\n\nيرجى المحاولة مرة أخرى.",
        "en": "❌ Invalid reference. Expected format is **INV-2024-001**.\n\nPlease try again.",
    }
    return messages.get(language, messages["fr"])


def _otp_sent_message(reference: str, language: str) -> str:
    messages = {
        "fr": (
            f"🔐 **Vérification de sécurité**\n\n"
            f"Dossier **{reference}** trouvé.\n"
            f"Pour sécuriser l'accès, un code OTP à 6 chiffres a été généré.\n\n"
            f"📱 Entrez le code de vérification :"
        ),
        "ar": (
            f"🔐 **التحقق الأمني**\n\n"
            f"تم العثور على الملف **{reference}**.\n"
            f"تم إنشاء رمز OTP مكون من 6 أرقام.\n\n"
            f"📱 أدخل رمز التحقق :"
        ),
        "en": (
            f"🔐 **Security Verification**\n\n"
            f"Dossier **{reference}** found.\n"
            f"A 6-digit OTP code has been generated for security.\n\n"
            f"📱 Enter the verification code:"
        ),
    }
    return messages.get(language, messages["fr"])


def _dossier_not_found_message(reference: str, language: str) -> str:
    messages = {
        "fr": (
            f"❌ Dossier **{reference}** introuvable.\n\n"
            "Vérifiez votre numéro de référence et réessayez.\n"
            "📞 En cas de problème : 05 37 77 64 00"
        ),
        "ar": (
            f"❌ الملف **{reference}** غير موجود.\n\n"
            "تحقق من رقم المرجع وحاول مرة أخرى.\n"
            "📞 في حالة وجود مشكلة: 05 37 77 64 00"
        ),
        "en": (
            f"❌ Dossier **{reference}** not found.\n\n"
            "Please check your reference number and try again.\n"
            "📞 Need help? Call: 05 37 77 64 00"
        ),
    }
    return messages.get(language, messages["fr"])


def _format_dossier_detail(dossier: dict, language: str) -> str:
    """Format detailed dossier view matching the spec format."""
    ref = dossier["reference"]
    nom = dossier["nom"]
    projet = dossier["projet"]
    ville = dossier["ville"]
    statut = dossier["statut"]
    etape = dossier["etape"]
    date_depot = dossier["date_depot"]
    derniere_maj = dossier["derniere_maj"]
    societe = dossier.get("societe", "")
    investissement = dossier.get("investissement", "")

    status_emoji = {
        "Validé": "✅",
        "En cours d'examen": "🔄",
        "En attente": "⏳",
        "Rejeté": "❌",
    }.get(statut, "📋")

    # Build history
    history_lines = ""
    historique = dossier.get("historique", [])
    if historique:
        history_lines = "\n\n📜 **Historique :**"
        for entry in historique[-5:]:
            date = entry.get("date", "")
            action = entry.get("action", "")
            note = entry.get("note", "")
            history_lines += f"\n  • {date} — {action}"
            if note:
                history_lines += f" ({note})"

    return f"""📋 **Votre Dossier**

🔢 Référence : **{ref}**
👤 Porteur : {nom}
🏢 Société : {societe}
📁 Projet : {projet}
📍 Localisation : {ville}
💰 Investissement : {investissement}

━━━━━━━━━━━━━━━━
📊 **STATUT ACTUEL**

{status_emoji} **{statut}**
📅 Déposé le : {date_depot}
🔄 Dernière mise à jour : {derniere_maj}
📍 Étape actuelle : {etape}
━━━━━━━━━━━━━━━━{history_lines}

💡 Besoin d'aide ? Contactez votre conseiller CRI-RSK
📞 05 37 77 64 00 | 📧 contact@rabatinvest.ma"""


def get_demo_dossier(reference: str) -> Optional[dict]:
    """Get a demo dossier by reference (used by OTP router too)."""
    _load_demo_dossiers()
    return _DEMO_DOSSIERS.get(reference.upper())


def get_all_demo_dossiers() -> list[dict]:
    """Get all demo dossiers (used by internal agent)."""
    _load_demo_dossiers()
    return list(_DEMO_DOSSIERS.values())
