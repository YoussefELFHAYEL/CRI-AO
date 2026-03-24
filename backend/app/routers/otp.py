"""
CRI-RSK Chatbot — OTP router for dossier verification.
"""

from fastapi import APIRouter

from app.database.models import (
    OtpRequest,
    OtpVerifyRequest,
    OtpResponse,
    OtpVerifyResponse,
)
from app.services.otp_service import generate_otp, verify_otp
from app.services.dossier_tracking import get_demo_dossier

router = APIRouter()


@router.post("/otp/generate", response_model=OtpResponse)
async def generate_otp_code(body: OtpRequest):
    """Generate an OTP code for dossier verification."""
    # Check if dossier exists
    dossier = get_demo_dossier(body.dossier_reference)
    if not dossier:
        return OtpResponse(
            message="Référence de dossier introuvable.",
            otp_sent=False,
        )

    otp_code = generate_otp(body.dossier_reference)

    return OtpResponse(
        message=(
            "Un code de vérification a été généré. "
            "Entrez le code à 6 chiffres."
        ),
        otp_sent=True,
        demo_otp=otp_code,  # Visible in demo mode
    )


@router.post("/otp/verify", response_model=OtpVerifyResponse)
async def verify_otp_code(body: OtpVerifyRequest):
    """Verify an OTP code and return dossier details."""
    result = verify_otp(body.dossier_reference, body.otp_code)

    if not result["verified"]:
        return OtpVerifyResponse(
            verified=False,
            message=result["message"],
        )

    dossier = get_demo_dossier(body.dossier_reference)
    return OtpVerifyResponse(
        verified=True,
        message="Vérification réussie.",
        dossier=dossier,
    )
