from datetime import date, timedelta
from typing import TypeVar

from django.db.models import QuerySet
from django.forms import IntegerField
from django.utils import timezone
from django_filters import Filter

_QS = TypeVar("_QS", bound=QuerySet)


def filter_age[QS: QuerySet](field_name: str, qs: QS, min_age: int | None, max_age: int | None) -> QS:
    current = timezone.now().date()
    lookup_expr = "range"
    values: date | tuple[date, date]
    if min_age is not None and max_age is not None:
        lookup_expr = "range"
        # min year +1 , day-1
        max_date = current - timedelta(days=min_age * 365.25)
        min_date = current - timedelta(days=(max_age - 1) * 365.25) + timedelta(days=1)
        values = (min_date, max_date)
    elif min_age is not None and max_age is None:
        lookup_expr = "lte"
        values = current - timedelta(days=min_age * 365.25)
    elif min_age is None and max_age is not None:
        lookup_expr = "gte"
        # min year -1 , day+1
        values = current - timedelta(days=(max_age - 1) * 365.25) + timedelta(days=1)
    else:
        return qs
    return qs.filter(**{f"{field_name}__{lookup_expr}": values})


class IntegerFilter(Filter):
    """Custom Integer filter to parse Decimal values."""

    field_class = IntegerField
