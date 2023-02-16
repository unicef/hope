import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen=True)
class XlsxError:
    sheet: str
    coordinates: Optional[str]
    message: str
