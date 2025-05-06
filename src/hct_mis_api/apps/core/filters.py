import json
from datetime import date, timedelta
from typing import Any, Callable

from django.db.models import QuerySet
from django.forms import (
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    Field,
    IntegerField,
)
from django.utils import timezone

from dateutil.parser import parse
from django_filters import Filter, FilterSet

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import decode_id_string


def _clean_data_for_range_field(value: Any, field: Callable) -> dict | None:
    if value:
        clean_data = {}
        values = json.loads(value)
        if isinstance(values, dict):
            for field_name, field_value in values.items():
                field_instance = field()
                if isinstance(field_instance, DateTimeField | DateField):
                    if field_value is None:
                        continue
                    field_value = parse(field_value, fuzzy=True)
                if isinstance(field_instance, IntegerField) and not field_value:
                    continue
                clean_data[field_name] = field_instance.clean(field_value)
        return clean_data or None
    return None


class IntegerRangeField(Field):
    def clean(self, value: Any) -> dict | None:
        return _clean_data_for_range_field(value, IntegerField)


class DecimalRangeField(Field):
    def clean(self, value: Any) -> dict | None:
        return _clean_data_for_range_field(value, DecimalField)


class DateTimeRangeField(Field):
    def clean(self, value: Any) -> dict | None:
        return _clean_data_for_range_field(value, DateTimeField)


class DateRangeField(Field):
    def clean(self, value: Any) -> dict | None:
        return _clean_data_for_range_field(value, DateField)


class BaseRangeFilter(Filter):
    field_class: type[Field] | None = None

    def filter(self, qs: QuerySet, values: tuple) -> QuerySet:
        if values:
            min_value = values.get("min")
            max_value = values.get("max")
            if min_value is not None and max_value is not None:
                self.lookup_expr = "range"
                values = (min_value, max_value)
            elif min_value is not None and max_value is None:
                self.lookup_expr = "gte"
                values = min_value
            elif min_value is None and max_value is not None:
                self.lookup_expr = "lte"
                values = max_value

        return super().filter(qs, values)


class IntegerRangeFilter(BaseRangeFilter):
    field_class = IntegerRangeField


class DateTimeRangeFilter(BaseRangeFilter):
    field_class = DateTimeRangeField


class DateRangeFilter(BaseRangeFilter):
    field_class = DateRangeField


class DecimalRangeFilter(BaseRangeFilter):
    field_class = DecimalRangeField


def filter_age(field_name: str, qs: QuerySet, min_age: int | None, max_age: int | None) -> QuerySet:
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


class AgeRangeFilter(Filter):
    field_class = IntegerRangeField

    def filter(self, qs: QuerySet, values: date | tuple[date, date]) -> QuerySet:
        if values:
            min_value = values.get("min")  # 20
            max_value = values.get("max")  # 21
            current = timezone.now().date()
            if min_value is not None and max_value is not None:
                self.lookup_expr = "range"
                # min year +1 , day-1
                max_date = date(
                    current.year - min_value,
                    current.month,
                    current.day,
                )
                min_date = date(
                    current.year - max_value - 1,
                    current.month,
                    current.day,
                )
                min_date = min_date + timedelta(days=1)
                values = (min_date, max_date)
            elif min_value is not None and max_value is None:
                self.lookup_expr = "lte"
                max_date = date(
                    current.year - min_value,
                    current.month,
                    current.day,
                )
                values = max_date
            elif min_value is None and max_value is not None:
                self.lookup_expr = "gte"
                # min year -1 , day+1
                min_date = date(
                    current.year - max_value - 1,
                    current.month,
                    current.day,
                )
                min_date = min_date + timedelta(days=1)
                values = min_date
        return super().filter(qs, values)


class IntegerFilter(Filter):
    """Custom Integer filter to parse Decimal values."""

    field_class = IntegerField


class BusinessAreaSlugFilter(Filter):
    field_class = CharField

    def filter(self, qs: QuerySet, business_area_slug: str) -> QuerySet:
        if not business_area_slug:
            return qs
        ba = BusinessArea.objects.only("id").get(slug=business_area_slug)
        if business_area_slug:
            return qs.filter(business_area_id=ba.id)
        return qs


class GlobalProgramFilterMixin(FilterSet):
    @property
    def qs(self) -> QuerySet:
        program_id = self.request.headers.get("Program")
        return super().qs.filter(program_id=decode_id_string(program_id))
