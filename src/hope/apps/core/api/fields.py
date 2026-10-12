from datetime import date, datetime
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import QuerySet
from rest_framework import serializers

from hope.apps.core.fields import (
    CURRENCY_DECIMAL_PLACES,
    CURRENCY_MAX_DIGITS,
    HopeCurrencyField,
    normalize_currency_decimal,
)
from hope.apps.core.timezones import utc_date


class UTCDateField(serializers.DateField):
    """Serialize date values and legacy datetime-backed dates as YYYY-MM-DD."""

    def to_representation(self, value: date | datetime) -> str:
        return super().to_representation(utc_date(value))


class HopeCurrencyDecimalField(serializers.DecimalField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("max_digits", CURRENCY_MAX_DIGITS)
        kwargs.setdefault("decimal_places", CURRENCY_DECIMAL_PLACES)
        kwargs.setdefault("coerce_to_string", True)
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data: Any) -> Any:
        try:
            value = normalize_currency_decimal(data)
        except DjangoValidationError:
            self.fail("invalid")
        return super().to_internal_value(str(value))

    def to_representation(self, value: Any) -> Any:
        representation = super().to_representation(value)
        if isinstance(representation, str):
            whole, _, fractional = representation.partition(".")
            return f"{whole}.{fractional.rstrip('0').ljust(2, '0')}"
        return representation


class HopeCurrencyModelSerializer(serializers.ModelSerializer):
    serializer_field_mapping = {
        **serializers.ModelSerializer.serializer_field_mapping,
        HopeCurrencyField: HopeCurrencyDecimalField,
    }


class ScopedRelatedFieldMixin:
    """Narrows the queryset to the scope of the url path, so an id from outside of it fails like a nonexistent one.

    The field relies on two things: the view has to put the scope object in the serializer context
    under the `scope` key (`BusinessAreaMixin`/`ProgramMixin` do), and `scope_path` has to be a valid
    ORM path from the queryset model to that object (defaults to the `scope` name itself).
    """

    def __init__(self, *args: Any, scope: str = "business_area", scope_path: str | None = None, **kwargs: Any) -> None:
        self.scope = scope
        self.scope_path = scope_path or scope
        super().__init__(*args, **kwargs)

    def get_queryset(self) -> QuerySet:
        if self.scope not in self.context:
            raise KeyError(
                f"'{self.scope}' is missing from the serializer context;"
                f" the view has to provide it for {type(self).__name__}"
            )
        return super().get_queryset().filter(**{self.scope_path: self.context[self.scope]})


class ScopedRelatedField(ScopedRelatedFieldMixin, serializers.PrimaryKeyRelatedField):
    pass


class ScopedSlugRelatedField(ScopedRelatedFieldMixin, serializers.SlugRelatedField):
    pass
