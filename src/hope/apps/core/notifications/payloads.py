from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, kw_only=True)
class EmailPayload:
    recipients: list[str]
    context: dict[str, Any]
    cc: list[str] = field(default_factory=list)
