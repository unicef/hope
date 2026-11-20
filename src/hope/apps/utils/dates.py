from datetime import date, datetime


def normalize_date(value: datetime | date | str | None) -> str:
    """Return a date or datetime value as an ISO-format string for external payloads.

    Pass strings through unchanged and map ``None`` to an empty string, so callers can
    always embed the result in a JSON-serializable payload.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)
