from decimal import ROUND_HALF_UP, Context, Decimal, InvalidOperation
from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Abs
from django.db.models.lookups import LessThan

CURRENCY_DECIMAL_PLACES = 10
CURRENCY_MAX_DIGITS = 30
CURRENCY_QUANTUM = Decimal("0.0000000001")
CURRENCY_MAX_ABSOLUTE_VALUE = Decimal(10) ** (CURRENCY_MAX_DIGITS - CURRENCY_DECIMAL_PLACES)


def currency_precision_check(*fields: str, name: str) -> models.CheckConstraint:
    condition = models.Q()
    for field in fields:
        condition &= models.Q(**{f"{field}__isnull": True}) | (
            models.Q(**{f"{field}__gte": 0}) & models.Q(LessThan(Abs(field), CURRENCY_MAX_ABSOLUTE_VALUE))
        )
    return models.CheckConstraint(condition=condition, name=name)


def normalize_currency_decimal(value: Any) -> Decimal:
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount < 0 or amount >= CURRENCY_MAX_ABSOLUTE_VALUE:
            raise InvalidOperation
        return amount.quantize(
            CURRENCY_QUANTUM,
            context=Context(prec=CURRENCY_MAX_DIGITS, rounding=ROUND_HALF_UP),
        )
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError("Enter a valid monetary amount with at most 20 digits before the decimal point.") from exc


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
