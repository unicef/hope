from __future__ import annotations

from datetime import UTC, date, datetime, time
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from django.utils import timezone
import pytz

if TYPE_CHECKING:
    from hope.models import BusinessArea, User

UTC_TIMEZONE_NAME = "UTC"


def utc_date(value: date | datetime) -> date:
    """Return a date unchanged or take the UTC calendar date from a legacy datetime-backed date."""
    if isinstance(value, datetime):
        if timezone.is_aware(value):
            value = value.astimezone(UTC)
        return value.date()
    return value


def to_utc_midnight(value: date | datetime | str) -> datetime:
    """Normalize a date-like value to midnight UTC."""
    if isinstance(value, str):
        value = date.fromisoformat(value)
    return datetime.combine(utc_date(value), time.min, tzinfo=UTC)


def get_country_timezone_name(iso_code2: str | None) -> str:
    if not iso_code2:
        return UTC_TIMEZONE_NAME

    country_timezones = pytz.country_timezones.get(iso_code2.upper(), ())
    return country_timezones[0] if country_timezones else UTC_TIMEZONE_NAME


def resolve_timezone_name(*, user: User | None = None, business_area: BusinessArea | None = None) -> str:
    if user and user.timezone:
        return str(user.timezone)
    if business_area and business_area.timezone:
        return str(business_area.timezone)
    return UTC_TIMEZONE_NAME


def resolve_timezone(*, user: User | None = None, business_area: BusinessArea | None = None) -> ZoneInfo:
    return ZoneInfo(resolve_timezone_name(user=user, business_area=business_area))


def localize_datetime(
    value: datetime,
    *,
    user: User | None = None,
    business_area: BusinessArea | None = None,
    timezone_name: str | None = None,
) -> datetime:
    target_timezone = (
        ZoneInfo(timezone_name) if timezone_name else resolve_timezone(user=user, business_area=business_area)
    )
    return timezone.localtime(value, timezone=target_timezone)


def format_human_datetime(
    value: datetime,
    *,
    user: User | None = None,
    business_area: BusinessArea | None = None,
    timezone_name: str | None = None,
) -> str:
    timezone_name = timezone_name or resolve_timezone_name(user=user, business_area=business_area)
    localized_value = localize_datetime(value, timezone_name=timezone_name)
    hour = localized_value.strftime("%I").lstrip("0") or "0"
    return f"{localized_value.day} {localized_value:%B %Y} {hour}:{localized_value:%M %p} ({timezone_name})"


def local_date(
    *,
    user: User | None = None,
    business_area: BusinessArea | None = None,
    at: datetime | None = None,
) -> date:
    return timezone.localdate(at or timezone.now(), timezone=resolve_timezone(user=user, business_area=business_area))
