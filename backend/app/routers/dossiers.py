"""
CRI-RSK Chatbot — Dossiers router.
"""

from fastapi import APIRouter

from app.services.dossier_tracking import (
    get_demo_dossier,
    get_all_demo_dossiers,
)

router = APIRouter()


@router.get("/dossiers")
async def list_dossiers(status: str = None):
    """List dossiers, optionally filtered by status."""
    all_dossiers = get_all_demo_dossiers()
    if status:
        return [d for d in all_dossiers if d.get("statut") == status]
    return all_dossiers


@router.get("/dossiers/{reference}")
async def get_dossier(reference: str):
    """Get a dossier by its reference code."""
    dossier = get_demo_dossier(reference)
    if not dossier:
        return {"error": "Dossier introuvable"}
    return dossier
