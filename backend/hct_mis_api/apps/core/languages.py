from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class Language:
    english: str
    code: str


LANGUAGES: List[Language] = [
    Language(english="English | English", code="en-us"),
    Language(english=" | عربي" + "Arabic", code="ar-ae"),
    Language(english="čeština | Czech", code="cs-cz"),
    Language(english="Deutsch", code="de-de"),
    Language(english="Español | Spanish", code="es-es"),
    Language(english="Français | French", code="fr-fr"),
    Language(english="Magyar | Hungarian", code="hu-hu"),
    Language(english="Italiano", code="it-it"),
    Language(english="Polskie | Polish", code="pl-pl"),
    Language(english="Português", code="pt-pt"),
    Language(english="Română", code="ro-ro"),
    Language(english="Русский | Russian", code="ru-ru"),
    Language(english="සිංහල | Sinhala", code="si-si"),
    Language(english="தமிழ் | Tamil", code="ta-ta"),
    Language(english="український | Ukrainian", code="uk-ua"),
    Language(english="हिंदी", code="hi-hi"),
]


class Languages:
    @classmethod
    def get_choices(cls) -> List[Dict[str, Any]]:
        return [
            {
                "label": {"English(EN)": language.code},
                "value": language.code,
            }
            for language in LANGUAGES
        ]

    @classmethod
    def get_tuple(cls) -> Tuple[Tuple[str, str], ...]:
        return tuple((lang.code, lang.code) for lang in LANGUAGES)

    @classmethod
    def filter_by_code(cls, name: str) -> List[Language]:
        return [language for language in LANGUAGES if name.lower() in language.code.lower()]
