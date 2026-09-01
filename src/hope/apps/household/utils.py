import re

from transliterate import translit
from transliterate.utils import LanguageDetectionError
from unidecode import unidecode

from hope.models.individual import ascii_name_validator

NAME_TO_LATIN_FIELDS = {
    "given_name": "given_name_latin",
    "middle_name": "middle_name_latin",
    "family_name": "family_name_latin",
    "full_name": "full_name_latin",
}


def to_latin(text: str | None) -> str | None:
    if text is None:
        return None

    try:
        latin_text = translit(text, reversed=True)
    except LanguageDetectionError:
        latin_text = unidecode(text)

    latin_text = re.sub(r"[`’‘]", "'", latin_text)
    latin_text = re.sub(r"[^a-zA-Z\s\-']", " ", latin_text)
    latin_text = re.sub(r"\s+", " ", latin_text).strip()
    latin_text = latin_text.strip(" '-")
    ascii_name_validator(latin_text)

    return latin_text.title()
