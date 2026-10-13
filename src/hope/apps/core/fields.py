from decimal import ROUND_HALF_UP, Context, Decimal, InvalidOperation
from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.db import models

CURRENCY_DECIMAL_PLACES = 10
CURRENCY_MAX_DIGITS = 30
CURRENCY_QUANTUM = Decimal("0.0000000001")


def normalize_currency_decimal(value: Any) -> Decimal:
    try:
        amount = Decimal(str(value))
        if not amount.is_finite():
            raise InvalidOperation
        return amount.quantize(
            CURRENCY_QUANTUM,
            context=Context(prec=CURRENCY_MAX_DIGITS, rounding=ROUND_HALF_UP),
        )
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError("Enter a valid monetary amount with at most 20 digits before the decimal point.") from exc


class HopeCurrencyFormField(forms.DecimalField):
    def to_python(self, value: Any) -> Any:
        parsed = super().to_python(value)
        return normalize_currency_decimal(parsed) if parsed is not None else None


class HopeCurrencyField(models.DecimalField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("max_digits", CURRENCY_MAX_DIGITS)
        kwargs.setdefault("decimal_places", CURRENCY_DECIMAL_PLACES)
        super().__init__(*args, **kwargs)

    def db_type(self, connection: Any) -> str:
        return "numeric"

    def to_python(self, value: Any) -> Decimal | None:
        if value is None:
            return None
        return normalize_currency_decimal(value)

    def from_db_value(self, value: Any, expression: Any, connection: Any) -> Decimal | None:
        return self.to_python(value)

    def formfield(self, **kwargs: Any) -> forms.Field | None:
        kwargs.setdefault("form_class", HopeCurrencyFormField)
        return super().formfield(**kwargs)
