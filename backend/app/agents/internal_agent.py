"""
CRI-RSK Chatbot — Internal agent configuration.
System prompts, statistics queries, and dossier management for CRI staff.
"""

import logging
import re
from typing import Optional

from app.services.dossier_tracking import (
    get_demo_dossier,
    get_all_demo_dossiers,
)

logger = logging.getLogger(__name__)

# Patterns for special internal queries
_DOSSIER_REF_PATTERN = re.compile(
    r"(?:dossier|réf|ref|reference|référence)\s*:?\s*(INV-\d{4}-\d{3,4})",
    re.IGNORECASE,
)
_DOSSIER_REF_STANDALONE = re.compile(r"\bINV-\d{4}-\d{3,4}\b", re.IGNORECASE)

_STATS_PATTERNS = [
    r"statistique",
    r"stat(?:s)?(?:\s+du\s+jour)?",
    r"tableau\s*de\s*bord",
    r"dashboard",
    r"إحصائ",
    r"📊",
]
_STATS_PATTERN = re.compile("|".join(_STATS_PATTERNS), re.IGNORECASE)

_PENDING_PATTERNS = [
    r"dossiers?\s*en\s*attente",
    r"attente",
    r"pending",
    r"⏳",
]
_PENDING_PATTERN = re.compile("|".join(_PENDING_PATTERNS), re.IGNORECASE)

_VALIDATED_PATTERNS = [
    r"dossiers?\s*valid[ée]s?",
    r"valid[ée]s?",
    r"approuv[ée]s?",
    r"✅",
]
_VALIDATED_PATTERN = re.compile("|".join(_VALIDATED_PATTERNS), re.IGNORECASE)

_REPORT_PATTERNS = [
    r"rapport",
    r"report",
    r"résumé",
    r"bilan",
    r"📈",
]
_REPORT_PATTERN = re.compile("|".join(_REPORT_PATTERNS), re.IGNORECASE)


def get_internal_system_prompt(language: str) -> str:
    """Get the system prompt for the internal agent."""
    return """Tu es l'assistant interne du CRI-RSK réservé aux collaborateurs autorisés du Centre Régional d'Investissement de Rabat-Salé-Kénitra.

RÔLE :
- Tu fournis des informations internes sur les dossiers d'investissement.
- Tu génères des statistiques et tableaux de bord.
- Tu aides à la gestion et au suivi des dossiers.
- Tu es direct, professionnel et factuel.

RÈGLES :
1. Utilise les données du contexte fourni.
2. Pour les statistiques, présente les données sous forme de tableaux formatés exactement selon le modèle demandé.
3. Pour les dossiers, affiche les informations de manière structurée.
4. Ne divulgue pas d'informations personnelles des investisseurs au public, mais tu es autorisé en interne.
5. Réponds dans la langue de l'utilisateur.

FORMAT DES RÉPONSES :
- Utilise des emojis pour les statuts (✅ validé, ⏳ en attente, ❌ rejeté, 📊 stats)
- Formate les chiffres clairement
- Utilise des tableaux quand c'est pertinent"""


def handle_internal_query(
    query: str, language: str
) -> Optional[str]:
    """
    Handle special internal agent queries (stats, dossiers).
    Returns formatted response or None if it's a regular RAG query.
    """
    # Check for dossier reference lookup
    ref_match = _DOSSIER_REF_PATTERN.search(query)
    if not ref_match:
        ref_match = _DOSSIER_REF_STANDALONE.search(query)
    if ref_match:
        reference = ref_match.group(0) if not ref_match.lastindex else ref_match.group(1)
        # Clean the reference
        reference = re.search(r"INV-\d{4}-\d{3,4}", reference, re.IGNORECASE)
        if reference:
            return _format_dossier_lookup(reference.group(0).upper())

    # Check for statistics/dashboard/rapport
    if _STATS_PATTERN.search(query) or _REPORT_PATTERN.search(query):
        return _format_statistics()

    # Check for pending dossiers
    if _PENDING_PATTERN.search(query):
        return _format_dossiers_by_status("En attente")

    # Check for validated dossiers
    if _VALIDATED_PATTERN.search(query):
        return _format_dossiers_by_status("Validé")

    # Not a special query — fall through to RAG
    return None


def _format_dossier_lookup(reference: str) -> str:
    """Format a dossier lookup response."""
    dossier = get_demo_dossier(reference)
    if not dossier:
        return f"❌ Dossier **{reference}** introuvable dans la base de données."

    status_emoji = {
        "Validé": "✅",
        "En cours d'examen": "🔄",
        "En attente": "⏳",
        "Rejeté": "❌",
    }.get(dossier.get("statut", ""), "📋")

    progress = ""
    # We estimate progress from demo dossiers based on history length vs arbitrary total (5)
    completed = len(dossier.get("historique", []))
    total = 5
    if completed > total:
        total = completed
    bar = "█" * completed + "░" * (total - completed)
    progress = f"\n📊 Progression : [{bar}] {completed}/{total}"

    history_text = ""
    history = dossier.get("historique", [])
    if history:
        history_text = "\n\n📜 **Historique :**"
        for entry in history[-5:]:  # Last 5 entries
            date = entry.get("date", "")
            action = entry.get("action", "")
            note = entry.get("note", "")
            history_text += f"\n  • {date} — {action}"
            if note:
                history_text += f" ({note})"

    return f"""{status_emoji} **Dossier {reference}**

🏢 Société : {dossier.get('societe', 'N/A')}
📁 Projet : {dossier.get('projet', 'N/A')} ({dossier.get('type_projet', 'N/A')})
👤 Porteur : {dossier.get('nom', 'N/A')} ({dossier.get('telephone', '')})
📍 Ville : {dossier.get('ville', 'N/A')}
💰 Investissement : {dossier.get('investissement', 'N/A')}
📌 Statut : **{dossier.get('statut', 'N/A')}**
🔧 Étape actuelle : {dossier.get('etape', 'N/A')}{progress}
📅 Date de dépôt : {dossier.get('date_depot', 'N/A')}
🔄 Dernière MAJ : {dossier.get('derniere_maj', 'N/A')}{history_text}"""


def _format_statistics() -> str:
    """Format a statistics dashboard response matching the exact spec."""
    all_dossiers = get_all_demo_dossiers()
    
    total = len(all_dossiers)
    by_status = {}
    for d in all_dossiers:
        s = d.get("statut", "Inconnu")
        by_status[s] = by_status.get(s, 0) + 1

    valides = by_status.get("Validé", 0)
    en_cours = by_status.get("En cours d'examen", 0)
    attente = by_status.get("En attente", 0)
    rejetes = by_status.get("Rejeté", 0)

    # Note: Chats numbers can be mocked or fetched. We mock for demo to always show lively stats
    return f"""📊 **TABLEAU DE BORD CRI-RSK**
━━━━━━━━━━━━━━━━

💬 **CHATBOT AUJOURD'HUI**
• Conversations actives : **42**
• Dossiers consultés : **18**
• Demandes incitations : **25**
• Taux de satisfaction : **4.8/5** ⭐

📂 **DOSSIERS PAR STATUT** (Total: {total})
• ✅ Validés : **{valides}**
• 🔄 En cours d'examen : **{en_cours}**
• ⏳ En attente : **{attente}**
• ❌ Rejetés : **{rejetes}**

📈 **ÉVALUATION UTILISATEURS**
• 🟢 Positifs : 85%
• 🟡 Neutres : 10%
• 🔴 Négatifs : 5%

⚠️ *3 requêtes escaladées vers les agents humains aujourd'hui.*"""


def _format_dossiers_by_status(status: str) -> str:
    """Format a list of dossiers by status."""
    all_dossiers = get_all_demo_dossiers()
    dossiers = [d for d in all_dossiers if d.get("statut", "").lower() == status.lower()]

    if not dossiers:
        return f"Aucun dossier avec le statut « {status} »."

    status_emoji = {
        "validé": "✅", "en cours d'examen": "🔄",
        "en attente": "⏳", "rejeté": "❌",
    }.get(status.lower(), "📋")

    lines = [f"{status_emoji} **Dossiers {status}** ({len(dossiers)})\n"]
    for d in dossiers[:10]:  # Max 10
        ref = d.get("reference", "")
        company = d.get("societe", "")
        step = d.get("etape", "")
        lines.append(f"  • **{ref}** — {company} ({step})")

    if len(dossiers) > 10:
        lines.append(f"\n  _...et {len(dossiers) - 10} autres dossiers_")

    return "\n".join(lines)


# Suggestion chips for internal agent
INTERNAL_SUGGESTIONS = [
    {"label": "📊 Tableau de bord", "value": "Tableau de bord statistiques du jour"},
    {"label": "⏳ Dossiers en attente", "value": "Afficher les dossiers en attente"},
    {"label": "✅ Dossiers validés", "value": "Afficher les dossiers validés"},
    {"label": "📈 Rapport de synthèse", "value": "Rapport de synthèse"},
]
