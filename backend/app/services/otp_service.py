"""
CRI-RSK Chatbot — OTP service backed by Upstash Redis.
Generates 6-digit codes with 5-minute TTL and 3-attempt limit.

Uses Upstash REST API (httpx) — no heavy redis-py driver needed.
"""

import random
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Will be set from config at init time
_UPSTASH_URL: str = ""
_UPSTASH_TOKEN: str = ""

OTP_TTL_SECONDS = 300  # 5 minutes
MAX_ATTEMPTS = 3


def init_otp_service(upstash_url: str, upstash_token: str) -> None:
    """Initialize with Upstash credentials. Call once at startup."""
    global _UPSTASH_URL, _UPSTASH_TOKEN
    _UPSTASH_URL = upstash_url.rstrip("/")
    _UPSTASH_TOKEN = upstash_token
    logger.info("OTP service initialized with Upstash Redis")


def _redis_cmd(*args: str) -> Optional[dict]:
    """Execute a single Redis command via Upstash REST API."""
    if not _UPSTASH_URL or not _UPSTASH_TOKEN:
        logger.warning("Upstash not configured — falling back to in-memory")
        return None

    # Build URL path: /command/arg1/arg2/...
    path = "/" + "/".join(str(a) for a in args)
    url = _UPSTASH_URL + path

    try:
        resp = httpx.get(
            url,
            headers={"Authorization": f"Bearer {_UPSTASH_TOKEN}"},
            timeout=5.0,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Upstash Redis error: {e}")
        return None


# ---------------------------------------------------------------------------
# Fallback in-memory store (used if Upstash is not configured)
# ---------------------------------------------------------------------------
import time

_mem_store: dict[str, tuple[str, float]] = {}
_mem_attempts: dict[str, int] = {}


def generate_otp(dossier_reference: str) -> str:
    """
    Generate a 6-digit OTP code for a dossier reference.
    Stores it in Redis with a 5-minute TTL.
    Returns the generated code.
    """
    otp_code = f"{random.randint(100000, 999999)}"
    ref = dossier_reference.upper()

    if _UPSTASH_URL and _UPSTASH_TOKEN:
        # Store OTP in Redis
        _redis_cmd("SET", f"otp:{ref}", otp_code, "EX", str(OTP_TTL_SECONDS))
        # Reset attempt counter
        _redis_cmd("SET", f"otp_attempts:{ref}", "0", "EX", str(OTP_TTL_SECONDS))
    else:
        # In-memory fallback
        _mem_store[ref] = (otp_code, time.time() + OTP_TTL_SECONDS)
        _mem_attempts[ref] = 0

    logger.info(
        f"OTP generated for {ref}: {otp_code} "
        f"(expires in {OTP_TTL_SECONDS}s)"
    )
    return otp_code


def verify_otp(dossier_reference: str, otp_code: str) -> dict:
    """
    Verify an OTP code for a dossier reference.
    Returns dict with:
      - verified: bool
      - message: str
      - attempts_remaining: int
    """
    ref = dossier_reference.upper()

    if _UPSTASH_URL and _UPSTASH_TOKEN:
        return _verify_redis(ref, otp_code)
    else:
        return _verify_memory(ref, otp_code)


def _verify_redis(ref: str, otp_code: str) -> dict:
    """Verify OTP using Upstash Redis."""
    # Check attempt count
    attempts_resp = _redis_cmd("GET", f"otp_attempts:{ref}")
    attempts = int(attempts_resp.get("result", 0) or 0) if attempts_resp else 0

    if attempts >= MAX_ATTEMPTS:
        logger.warning(f"Max OTP attempts reached for {ref}")
        # Clean up
        _redis_cmd("DEL", f"otp:{ref}")
        _redis_cmd("DEL", f"otp_attempts:{ref}")
        return {
            "verified": False,
            "message": "Nombre maximum de tentatives atteint. Veuillez régénérer un code.",
            "attempts_remaining": 0,
        }

    # Get stored OTP
    otp_resp = _redis_cmd("GET", f"otp:{ref}")
    stored_code = otp_resp.get("result") if otp_resp else None

    if not stored_code:
        logger.warning(f"No OTP found or expired for {ref}")
        return {
            "verified": False,
            "message": "Code expiré ou introuvable. Veuillez régénérer un code.",
            "attempts_remaining": 0,
        }

    if otp_code != stored_code:
        # Increment attempts
        _redis_cmd("INCR", f"otp_attempts:{ref}")
        remaining = MAX_ATTEMPTS - attempts - 1
        logger.warning(f"Invalid OTP for {ref}, {remaining} attempts remaining")
        return {
            "verified": False,
            "message": f"Code incorrect. {remaining} tentative(s) restante(s).",
            "attempts_remaining": remaining,
        }

    # Valid — clean up
    _redis_cmd("DEL", f"otp:{ref}")
    _redis_cmd("DEL", f"otp_attempts:{ref}")
    logger.info(f"OTP verified successfully for {ref}")
    return {
        "verified": True,
        "message": "Vérification réussie.",
        "attempts_remaining": MAX_ATTEMPTS,
    }


def _verify_memory(ref: str, otp_code: str) -> dict:
    """Verify OTP using in-memory fallback."""
    attempts = _mem_attempts.get(ref, 0)

    if attempts >= MAX_ATTEMPTS:
        _mem_store.pop(ref, None)
        _mem_attempts.pop(ref, None)
        return {
            "verified": False,
            "message": "Nombre maximum de tentatives atteint. Veuillez régénérer un code.",
            "attempts_remaining": 0,
        }

    stored = _mem_store.get(ref)
    if not stored:
        return {
            "verified": False,
            "message": "Code expiré ou introuvable. Veuillez régénérer un code.",
            "attempts_remaining": 0,
        }

    stored_code, expiry = stored
    if time.time() > expiry:
        _mem_store.pop(ref, None)
        _mem_attempts.pop(ref, None)
        return {
            "verified": False,
            "message": "Code expiré. Veuillez régénérer un code.",
            "attempts_remaining": 0,
        }

    if otp_code != stored_code:
        _mem_attempts[ref] = attempts + 1
        remaining = MAX_ATTEMPTS - attempts - 1
        return {
            "verified": False,
            "message": f"Code incorrect. {remaining} tentative(s) restante(s).",
            "attempts_remaining": remaining,
        }

    # Valid — clean up
    _mem_store.pop(ref, None)
    _mem_attempts.pop(ref, None)
    return {
        "verified": True,
        "message": "Vérification réussie.",
        "attempts_remaining": MAX_ATTEMPTS,
    }


def cleanup_expired() -> None:
    """Remove all expired OTPs from the in-memory store."""
    now = time.time()
    expired = [
        ref for ref, (_, expiry) in _mem_store.items() if now > expiry
    ]
    for ref in expired:
        _mem_store.pop(ref, None)
        _mem_attempts.pop(ref, None)
