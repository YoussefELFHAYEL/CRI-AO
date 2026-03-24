"""
CRI-RSK Chatbot — Language detection service.
Detects French, Arabic, and English from user input.
"""

import logging
import re

from langdetect import detect, DetectorFactory

logger = logging.getLogger(__name__)

# Ensure consistent results
DetectorFactory.seed = 0

# Arabic Unicode range for quick check
_ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+")


def detect_language(text: str) -> str:
    """
    Detect the language of the input text.

    Returns 'ar', 'fr', or 'en'. Defaults to 'fr' on ambiguity.

    The function first checks for Arabic characters (since langdetect
    can struggle with short Arabic text), then falls back to langdetect.
    """
    if not text or not text.strip():
        return "fr"

    text = text.strip()

    # Quick check: if text contains significant Arabic characters, return 'ar'
    arabic_chars = _ARABIC_PATTERN.findall(text)
    total_arabic_len = sum(len(match) for match in arabic_chars)
    non_space_len = len(text.replace(" ", ""))

    if non_space_len > 0 and total_arabic_len / non_space_len > 0.3:
        return "ar"

    try:
        detected = detect(text)
        # Map langdetect codes to our supported languages
        if detected == "ar":
            return "ar"
        elif detected in ("en", "en-us", "en-gb"):
            return "en"
        elif detected in ("fr",):
            return "fr"
        else:
            # For unsupported languages, default to French
            return "fr"
    except Exception:
        logger.warning(f"Language detection failed for: {text[:50]}")
        return "fr"
