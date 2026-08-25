from datetime import date, datetime

from rest_framework import serializers

from hope.apps.core.timezones import utc_date


class UTCDateField(serializers.DateField):
    """Serialize date values and legacy datetime-backed dates as YYYY-MM-DD."""

    def to_representation(self, value: date | datetime) -> str:
        return super().to_representation(utc_date(value))
