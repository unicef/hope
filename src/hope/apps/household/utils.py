import re

from transliterate import translit
from transliterate.utils import LanguageDetectionError
from unidecode import unidecode

from hope.models.individual import ascii_name_validator


def to_latin(text: str | None) -> str | None:
    """Transliterate name into Latin.

    translit is using for Cyrillic
    unidecode for Arabic and other.
    """
    if text is None:
        return None

    try:
        latin_text = translit(text)
    except LanguageDetectionError:
        latin_text = unidecode(text)
    # clean up
    latin_text = re.sub(r"[`'’‘]", "", latin_text)
    latin_text = re.sub(r"[^a-zA-Z\s]", " ", latin_text)
    latin_text = re.sub(r"\s+", " ", latin_text).strip()
    # validate
    try:
        ascii_name_validator(latin_text)
    except ValueError as e:
        raise ValueError(e.message) from e

    return latin_text.title()
