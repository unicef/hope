from typing import Any

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


class CountryWorkspaceIdConditionalMixin:
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs = super().validate(attrs)
        if self.context.get("is_coming_from_cw") and not attrs.get("country_workspace_id"):
            raise serializers.ValidationError(
                {"country_workspace_id": "This field is required for RDIs uploaded by Country Workspace"}
            )
        return attrs
