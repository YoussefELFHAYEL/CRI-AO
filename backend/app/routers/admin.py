from fastapi import APIRouter, HTTPException
from typing import Optional, List, Any, Dict
from pydantic import BaseModel
import sys

from app.database.supabase_client import (
    get_unknown_questions,
    update_unknown_question,
    get_all_messages,
    get_all_dossiers,
    update_dossier_status
)

router = APIRouter()

class QuestionUpdate(BaseModel):
    status: str
    suggested_answer: Optional[str] = None

class DossierUpdate(BaseModel):
    status: str

@router.get("/questions")
def admin_get_questions(status: str = "pending"):
    """Get all unknown questions of a certain status"""
    return get_unknown_questions(status)

@router.put("/questions/{qid}")
def admin_update_question(qid: str, body: QuestionUpdate):
    """Update status (validate/reject) and potentially save new answer"""
    res = update_unknown_question(qid, body.status, body.suggested_answer)
    if not res:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # If validated, we would typically push it to ChromaDB here.
    # For demo purposes, the DB update is enough.
    return res

@router.get("/messages")
def admin_get_messages():
    """Get recent messages for the table"""
    return get_all_messages()

@router.get("/dossiers")
def admin_get_dossiers():
    """Get all dossiers"""
    return get_all_dossiers()

@router.put("/dossiers/{qid}")
def admin_update_dossier(qid: str, body: DossierUpdate):
    """Update dossier status. The frontend will simulate push notification."""
    res = update_dossier_status(qid, body.status)
    if not res:
        raise HTTPException(status_code=404, detail="Dossier not found")
    return res

# Optional: Stats returning mocked aggregations for the frontend dashboard
@router.get("/stats")
def admin_get_stats():
    msgs = len(get_all_messages(limit=5000))
    dossiers = len(get_all_dossiers())
    return {
        "total_messages": msgs,
        "resolution_rate": "89.4%",
        "avg_rating": "4.6",
        "total_dossiers": dossiers
    }
