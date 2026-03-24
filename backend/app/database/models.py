"""
CRI-RSK Chatbot — Pydantic models for API requests/responses and DB records.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# --- Enums ---

class AgentType(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"


class MessageRole(str, Enum):
    USER = "user"
    BOT = "bot"


class QuestionStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"


class Language(str, Enum):
    FR = "fr"
    AR = "ar"
    EN = "en"


# --- Chat API ---

class ChatRequest(BaseModel):
    message: str
    agent_type: AgentType = AgentType.PUBLIC
    conversation_id: Optional[str] = None
    language: Optional[str] = None


class ButtonOption(BaseModel):
    """WhatsApp-style inline button."""
    label: str
    value: str
    emoji: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    message_id: str
    language: str
    agent_type: AgentType
    buttons: Optional[list[ButtonOption]] = None
    requires_otp: bool = False
    dossier_reference: Optional[str] = None
    otp_code: Optional[str] = None
    is_fallback: bool = False
    is_escalation: bool = False


# --- Conversations ---

class ConversationCreate(BaseModel):
    agent_type: AgentType
    user_phone: Optional[str] = None
    language: str = "fr"


class ConversationResponse(BaseModel):
    id: str
    agent_type: AgentType
    user_phone: Optional[str] = None
    started_at: datetime
    language: str


# --- Messages ---

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: MessageRole
    content: str
    created_at: datetime
    language: Optional[str] = None


# --- Ratings ---

class RatingCreate(BaseModel):
    message_id: str
    score: int = Field(..., ge=1, le=5)


class RatingResponse(BaseModel):
    id: str
    message_id: str
    score: int
    created_at: datetime


# --- OTP ---

class OtpRequest(BaseModel):
    dossier_reference: str


class OtpVerifyRequest(BaseModel):
    dossier_reference: str
    otp_code: str


class OtpResponse(BaseModel):
    message: str
    otp_sent: bool
    demo_otp: Optional[str] = None  # Visible in demo mode


class OtpVerifyResponse(BaseModel):
    verified: bool
    message: str
    dossier: Optional[dict] = None


# --- Dossiers ---

class DossierResponse(BaseModel):
    reference: str
    company_name: str
    project_type: str
    status: str
    current_step: Optional[str] = None
    total_steps: int
    completed_steps: int
    investor_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    history: list[dict] = []


# --- Incitations Flow ---

class IncitationStepResponse(BaseModel):
    """Response for interactive incitation flow."""
    question: str
    step: int
    total_steps: int
    options: list[ButtonOption]
    is_final: bool = False
    result: Optional[str] = None
