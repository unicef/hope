import re

from transliterate import translit
from transliterate.utils import LanguageDetectionError
from unidecode import unidecode

from hope.models.individual import ascii_name_validator


def to_latin(text: str | None) -> str | None:
    """Transliterate name into Latin while preserving valid punctuation."""
    if text is None:
        return None

    try:
        latin_text = translit(text, reversed=True)
    except LanguageDetectionError:
        latin_text = unidecode(text)

    # Normalize apostrophes to standard '
    latin_text = re.sub(r"[`’‘]", "'", latin_text)

    # Keep letters, spaces, hyphens, apostrophes
    latin_text = re.sub(r"[^a-zA-Z\s\-']", " ", latin_text)

    # Normalize whitespace
    latin_text = re.sub(r"\s+", " ", latin_text).strip()

    # Validate
    ascii_name_validator(latin_text)

    return latin_text.title()
