"""
CRI-RSK Chatbot — Ratings router.
"""

from fastapi import APIRouter

from app.database.models import RatingCreate, RatingResponse
from app.database.supabase_client import save_rating

router = APIRouter()


@router.post("/ratings", response_model=RatingResponse)
async def create_rating(body: RatingCreate):
    """Submit a star rating for a bot message."""
    rating = save_rating(message_id=body.message_id, score=body.score)
    return rating
