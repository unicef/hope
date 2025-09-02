from enum import Enum, auto, unique
from typing import Any


@unique
class Grant(Enum):
    def _generate_next_value_(self: str, start: int, count: int, last_values: list[Any]) -> Any:  # type: ignore # FIXME: signature differs from superclass
        return self

    API_READ_ONLY = auto()
    API_RDI_UPLOAD = auto()
    API_RDI_CREATE = auto()

    API_PROGRAM_CREATE = auto()

    @classmethod
    def choices(cls) -> tuple[tuple[Any, Any], ...]:
        return tuple((i.value, i.value) for i in cls)
