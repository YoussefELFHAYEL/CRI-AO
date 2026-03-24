"""
CRI-RSK Chatbot — Database operations using psycopg2.
Directly connects to Supabase PostgreSQL at aws-1-eu-central-1.pooler.supabase.com.
"""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
from functools import lru_cache

from app.config import get_settings

logger = logging.getLogger(__name__)

# Direct connection to the database (best for psycopg2)
DATABASE_URL = "postgresql://postgres.gaxngnkvfquwfbshzkcd:,R?7w7tTZq$Y5eE@aws-1-eu-central-1.pooler.supabase.com:5432/postgres"

@lru_cache()
def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        return conn
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        raise e


# --- Conversations ---

def create_conversation(
    agent_type: str,
    language: str = "fr",
    user_phone: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new conversation record."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO conversations (agent_type, language, user_phone) VALUES (%s, %s, %s) RETURNING *",
            (agent_type, language, user_phone)
        )
        return cur.fetchone()


def get_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
    """Get a conversation by ID."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM conversations WHERE id = %s", (conversation_id,))
        return cur.fetchone()


# --- Messages ---

def save_message(
    conversation_id: str,
    role: str,
    content: str,
    language: Optional[str] = None,
) -> Dict[str, Any]:
    """Save a message to the database."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO messages (conversation_id, role, content, language) VALUES (%s, %s, %s, %s) RETURNING *",
            (conversation_id, role, content, language)
        )
        return cur.fetchone()


def get_conversation_messages(conversation_id: str) -> List[Dict[str, Any]]:
    """Get all messages for a conversation, ordered by creation time."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM messages WHERE conversation_id = %s ORDER BY created_at ASC",
            (conversation_id,)
        )
        return cur.fetchall()


# --- Ratings ---

def save_rating(message_id: str, score: int) -> Dict[str, Any]:
    """Save a rating for a message."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO ratings (message_id, score) VALUES (%s, %s) RETURNING *",
            (message_id, score)
        )
        return cur.fetchone()


# --- Unknown Questions ---

def save_unknown_question(
    question: str, suggested_answer: Optional[str] = None
) -> Dict[str, Any]:
    """Save a question that the bot couldn't answer."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO unknown_questions (question, suggested_answer, status) VALUES (%s, %s, 'pending') RETURNING *",
            (question, suggested_answer)
        )
        return cur.fetchone()


# --- Demo Dossiers ---

def get_dossier_by_reference(reference: str) -> Optional[Dict[str, Any]]:
    """Look up a demo dossier by its reference code."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM demo_dossiers WHERE UPPER(reference) = %s",
            (reference.upper(),)
        )
        return cur.fetchone()


def get_dossiers_by_status(status: str) -> List[Dict[str, Any]]:
    """Get demo dossiers filtered by status."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM demo_dossiers WHERE status = %s", (status,))
        return cur.fetchall()


def get_all_dossiers() -> List[Dict[str, Any]]:
    """Get all demo dossiers."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM demo_dossiers ORDER BY created_at DESC")
        return cur.fetchall()


# --- Demo Statistics ---

def get_statistics(period: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get demo statistics, optionally filtered by period."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        if period:
            cur.execute("SELECT * FROM demo_statistics WHERE period = %s", (period,))
        else:
            cur.execute("SELECT * FROM demo_statistics")
        return cur.fetchall()


# --- FAQ Validated ---

def get_validated_faqs(
    language: Optional[str] = None,
    category: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get validated FAQ entries."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        sql = "SELECT * FROM faq_validated WHERE 1=1"
        params = []
        if language:
            sql += " AND language = %s"
            params.append(language)
        if category:
            sql += " AND category = %s"
            params.append(category)
        cur.execute(sql, tuple(params))
        return cur.fetchall()


# --- Contacts ---

def save_contact(
    name: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    company: Optional[str] = None,
    sector: Optional[str] = None,
    source: str = "chatbot",
) -> Dict[str, Any]:
    """Save a new contact."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO contacts (name, phone, email, company, sector, source) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
            (name, phone, email, company, sector, source)
        )
        return cur.fetchone()

# --- ADMIN API ENDPOINTS ---

def get_unknown_questions(status: str = "pending") -> List[Dict[str, Any]]:
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM unknown_questions WHERE status = %s ORDER BY created_at DESC", (status,))
        return cur.fetchall()

def update_unknown_question(qid: str, status: str, suggested_answer: Optional[str] = None) -> Dict[str, Any]:
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "UPDATE unknown_questions SET status = %s, suggested_answer = COALESCE(%s, suggested_answer) WHERE id = %s RETURNING *",
            (status, suggested_answer, qid)
        )
        return cur.fetchone()

def get_all_messages(limit: int = 1000) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM messages ORDER BY created_at DESC LIMIT %s", (limit,))
        return cur.fetchall()

def update_dossier_status(qid: str, status: str) -> Dict[str, Any]:
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("UPDATE demo_dossiers SET status = %s WHERE id = %s RETURNING *", (status, qid))
        return cur.fetchone()

