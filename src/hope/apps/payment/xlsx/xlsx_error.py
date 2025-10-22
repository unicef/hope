import dataclasses


@dataclasses.dataclass(frozen=True)
class XlsxError:
    sheet: str
    coordinates: str | None
    message: str
