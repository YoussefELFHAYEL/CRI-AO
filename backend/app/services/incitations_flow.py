"""
CRI-RSK Chatbot — Interactive incitations flow.
Dynamic decision tree backed by real JSON incitation data.

Architecture:
- _all_incitations.json is loaded once at startup into _INCITATIONS_DB
- META files (secteurs, tailles, locations) are loaded into lookup dicts
- User selections at each step (sector, size, location) are intersected
  to produce a filtered list of matching incitations
- Top 5 results are displayed with a "and X more" footer
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Optional

from app.database.models import ButtonOption, IncitationStepResponse

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data loading (once at import time)
# ---------------------------------------------------------------------------

_INCITATIONS_JSON_DIR = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..",
    "knowledge_base", "rabat invest", "invest_in_rsk", "incitations_json",
)

# All incitations keyed by ID
_INCITATIONS_DB: dict[str, dict] = {}

# META indexes: sector -> set(INC-IDs), taille -> set(INC-IDs), location -> set(INC-IDs)
_META_SECTEURS: dict[str, set[str]] = {}
_META_TAILLES: dict[str, set[str]] = {}
_META_LOCATIONS: dict[str, set[str]] = {}

_DATA_LOADED = False


def _load_incitations_data() -> None:
    """Load _all_incitations.json and META files into memory."""
    global _DATA_LOADED
    if _DATA_LOADED:
        return

    base = Path(_INCITATIONS_JSON_DIR).resolve()
    logger.info(f"Loading incitations data from {base}")

    # 1) Load all incitations
    all_file = base / "_all_incitations.json"
    if all_file.exists():
        with open(all_file, "r", encoding="utf-8") as f:
            all_data = json.load(f)
        for inc in all_data:
            _INCITATIONS_DB[inc["id"]] = inc
        logger.info(f"Loaded {len(_INCITATIONS_DB)} incitations")
    else:
        logger.warning(f"_all_incitations.json not found at {all_file}")

    # 2) Load META indexes
    def _load_meta(filename: str) -> dict[str, set[str]]:
        path = base / filename
        if not path.exists():
            logger.warning(f"META file not found: {path}")
            return {}
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return {k: set(v) for k, v in raw.items()}

    global _META_SECTEURS, _META_TAILLES, _META_LOCATIONS
    _META_SECTEURS = _load_meta("META-001_secteurs.json")
    _META_TAILLES = _load_meta("META-002_tailles.json")
    _META_LOCATIONS = _load_meta("META-003_locations.json")

    logger.info(
        f"META loaded: {len(_META_SECTEURS)} secteurs, "
        f"{len(_META_TAILLES)} tailles, "
        f"{len(_META_LOCATIONS)} locations"
    )
    _DATA_LOADED = True


# Eagerly load on import
try:
    _load_incitations_data()
except Exception as e:
    logger.error(f"Failed to load incitations data: {e}")

# ---------------------------------------------------------------------------
# In-memory state for incitation flow per conversation
# ---------------------------------------------------------------------------
_flow_state: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# Trigger patterns
# ---------------------------------------------------------------------------
INCITATION_TRIGGERS = [
    r"incitation",
    r"incitatif",
    r"aide",
    r"subvention",
    r"exon[ée]ration",
    r"avantage.*fiscal",
    r"incentive",
    r"tax.*benefit",
    r"حوافز",
    r"إعفاء",
    r"💰\s*incitation",
]

_TRIGGER_PATTERN = re.compile(
    "|".join(INCITATION_TRIGGERS), re.IGNORECASE
)

# ---------------------------------------------------------------------------
# Decision tree structure — hardcoded buttons, dynamic filtering
# ---------------------------------------------------------------------------
INCITATION_TREE = {
    "step_1": {
        "question": "Quel est votre secteur d'activité ?",
        "options": [
            ButtonOption(label="🏭 Industrie", value="industrie", emoji="🏭"),
            ButtonOption(label="💼 Services", value="services", emoji="💼"),
            ButtonOption(label="🌿 Agriculture", value="agriculture", emoji="🌿"),
            ButtonOption(label="💻 Tech/Numérique", value="tech", emoji="💻"),
            ButtonOption(label="🏗️ BTP", value="btp", emoji="🏗️"),
            ButtonOption(label="🛒 Commerce", value="commerce", emoji="🛒"),
        ],
    },
    "step_2": {
        "question": "Quelle est la taille de votre entreprise ?",
        "options": [
            ButtonOption(
                label="👤 TPE (moins de 10 employés)",
                value="tpe",
                emoji="👤",
            ),
            ButtonOption(
                label="🏢 PME (10 à 200 employés)",
                value="pme",
                emoji="🏢",
            ),
            ButtonOption(
                label="🏭 Grande Entreprise (plus de 200)",
                value="ge",
                emoji="🏭",
            ),
        ],
    },
    "step_3": {
        "question": "Quelle est votre localisation ?",
        "options": [
            ButtonOption(label="📍 Rabat", value="rabat", emoji="📍"),
            ButtonOption(label="📍 Salé", value="sale", emoji="📍"),
            ButtonOption(label="📍 Kénitra", value="kenitra", emoji="📍"),
            ButtonOption(label="📍 Autre", value="toute_region", emoji="📍"),
        ],
    },
}

MAX_RESULTS = 5

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_incitation_query(message: str) -> bool:
    """Check if the message triggers the incitations flow."""
    return bool(_TRIGGER_PATTERN.search(message))


def is_in_flow(conversation_id: str) -> bool:
    """Check if a conversation is currently in the incitations flow."""
    return conversation_id in _flow_state


def get_incitation_step(
    message: str, conversation_id: str
) -> IncitationStepResponse:
    """
    Get the current step in the incitations flow for a conversation.
    Handles both initial triggers, selections, and back navigation.
    """
    state = _flow_state.get(conversation_id)
    msg = message.lower().strip()

    # New flow — start from step 1
    if state is None or is_incitation_query(msg):
        _flow_state[conversation_id] = {"step": 1, "selections": []}
        step_data = INCITATION_TREE["step_1"]
        return IncitationStepResponse(
            question="🏠 *Accueil > Incitations*\n\n" + step_data["question"],
            step=1,
            total_steps=3,
            options=step_data["options"] + [ButtonOption(label="🔙 Retour", value="retour", emoji="🔙")],
        )

    # Handle 'retour' logic
    if msg == 'retour':
        if state["step"] > 1:
            state["step"] -= 1
            if len(state["selections"]) > 0:
                state["selections"].pop()
        else:
            # Cancel flow entirely
            del _flow_state[conversation_id]
            return IncitationStepResponse(
                question="Flow d'incitations annulé. Retour au menu principal.",
                step=0,
                total_steps=3,
                options=[],
                is_final=True,
                result="Annulé"
            )
    else:
        # Move forward
        state["selections"].append(msg)
        state["step"] += 1

    current_step = state["step"]

    # Build breadcrumbs
    def _map_label(val: str) -> str:
        # Quick map back to human label
        for step_k, step_v in INCITATION_TREE.items():
            for opt in step_v["options"]:
                if opt.value == val:
                    return opt.label.split(" ")[-1]  # roughly get the text without emoji
        return val.capitalize()

    breadcrumb = "🏠 *Accueil > Incitations*"
    if len(state["selections"]) > 0:
        breadcrumb += " > " + " > ".join([_map_label(s) for s in state["selections"]])

    if current_step <= 3:
        step_data = INCITATION_TREE[f"step_{current_step}"]
        return IncitationStepResponse(
            question=f"{breadcrumb}\n\n" + step_data["question"],
            step=current_step,
            total_steps=3,
            options=step_data["options"] + [ButtonOption(label="🔙 Retour", value="retour", emoji="🔙")],
        )

    # Flow complete — generate result from real data
    selections = state["selections"][:3]
    secteur = selections[0] if len(selections) > 0 else ""
    taille = selections[1] if len(selections) > 1 else ""
    location = selections[2] if len(selections) > 2 else ""

    result = _filter_incitations(secteur, taille, location)

    # Clear flow state
    del _flow_state[conversation_id]

    return IncitationStepResponse(
        question=f"{breadcrumb}\n\n{result}",
        step=3,
        total_steps=3,
        options=[],
        is_final=True,
        result=result,
    )


# ---------------------------------------------------------------------------
# Filtering engine
# ---------------------------------------------------------------------------


def _filter_incitations(secteur: str, taille: str, location: str) -> str:
    """
    Filter incitations by intersecting META indexes.
    Returns formatted response string.
    """
    # Ensure data is loaded
    _load_incitations_data()

    # Get candidate IDs from each dimension
    secteur_ids = _META_SECTEURS.get(secteur, set())
    taille_ids = _META_TAILLES.get(taille, set())
    location_ids = _META_LOCATIONS.get(location, set())

    # Handle "toute_region" — union of all locations
    if location == "toute_region" and not location_ids:
        location_ids = set()
        for ids in _META_LOCATIONS.values():
            location_ids |= ids

    # Intersection of all three dimensions
    if secteur_ids and taille_ids and location_ids:
        matching_ids = secteur_ids & taille_ids & location_ids
    elif secteur_ids and taille_ids:
        matching_ids = secteur_ids & taille_ids
    elif secteur_ids:
        matching_ids = secteur_ids
    else:
        # Fallback: all incitations
        matching_ids = set(_INCITATIONS_DB.keys())

    if not matching_ids:
        return _no_results_message(secteur, taille, location)

    # Get full incitation objects
    matching = [
        _INCITATIONS_DB[inc_id]
        for inc_id in matching_ids
        if inc_id in _INCITATIONS_DB
    ]

    # Sort: incitations with montant_ou_taux first, then by name
    matching.sort(
        key=lambda x: (
            0 if x.get("montant_ou_taux") else 1,
            x.get("nom", ""),
        )
    )

    total = len(matching)
    display = matching[:MAX_RESULTS]

    # Build formatted response
    secteur_label = {
        "industrie": "Industrie",
        "services": "Services",
        "agriculture": "Agriculture",
        "tech": "Tech/Numérique",
        "btp": "BTP",
        "commerce": "Commerce",
    }.get(secteur, secteur.capitalize())

    taille_label = {
        "tpe": "TPE",
        "pme": "PME",
        "ge": "Grande Entreprise",
    }.get(taille, taille.upper())

    location_label = {
        "rabat": "Rabat",
        "sale": "Salé",
        "kenitra": "Kénitra",
        "toute_region": "Toute la région RSK",
    }.get(location, location.capitalize())

    lines = [
        f"🎯 **Incitations disponibles pour votre profil :**",
        f"📌 Secteur : {secteur_label} | Taille : {taille_label} | Zone : {location_label}",
        f"📊 **{total} incitation(s) trouvée(s)**\n",
    ]

    for i, inc in enumerate(display, 1):
        nom = inc.get("nom_court") or inc.get("nom", "Sans nom")
        # Truncate long names
        if len(nom) > 80:
            nom = nom[:77] + "..."
        desc = inc.get("description_courte", "")
        # Take first line of description
        desc_short = desc.split("\n")[0][:120] if desc else ""
        montant = inc.get("montant_ou_taux", "")
        duree = inc.get("duree", "")
        org = inc.get("organisation", {}).get("nom", "")

        lines.append(f"✅ **{i}. {nom}**")
        if desc_short:
            lines.append(f"   → {desc_short}")
        if montant:
            lines.append(f"   💰 Montant/Taux : {montant}")
        if duree:
            lines.append(f"   ⏱️ Durée : {duree}")
        if org:
            lines.append(f"   🏛️ Organisme : {org}")
        lines.append("")  # blank line between entries

    if total > MAX_RESULTS:
        lines.append(
            f"📌 **Et {total - MAX_RESULTS} autres incitations disponibles.**"
        )

    lines.append(
        "\n📞 Pour un accompagnement personnalisé, contactez le CRI-RSK :\n"
        "📞 05 37 77 64 00 | 📧 contact@rabatinvest.ma"
    )

    return "\n".join(lines)


def _no_results_message(secteur: str, taille: str, location: str) -> str:
    """Fallback message when no incitations match the filters."""
    return (
        "🔍 Aucune incitation spécifique trouvée pour votre combinaison exacte.\n\n"
        "**Recommandations :**\n"
        "• Contactez directement un conseiller CRI-RSK pour un accompagnement personnalisé\n"
        "• Certaines incitations nationales peuvent s'appliquer à votre cas\n\n"
        "📞 05 37 77 64 00 | 📧 contact@rabatinvest.ma"
    )
