from rest_framework import serializers

from hope.models import NOT_DISABLED


class NullableChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data: str) -> str | None:  # type: ignore[override]
        if data == "":
            return None
        return super().to_internal_value(data)


class DisabilityChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data: str) -> str:  # type: ignore[override]
        if data == "":
            return NOT_DISABLED
        return super().to_internal_value(data)
