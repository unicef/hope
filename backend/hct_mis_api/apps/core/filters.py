import json
from datetime import datetime, date, timedelta

from django.forms import Field, IntegerField, DecimalField
from django_filters import Filter


def _clean_data_for_range_field(value, field):
    if value:
        clean_data = {}
        values = json.loads(value)
        if isinstance(values, dict):
            for field_name, field_value in values.items():
                clean_data[field_name] = field().clean(field_value)
        return clean_data or None
    else:
        return None


class IntegerRangeField(Field):
    def clean(self, value):
        return _clean_data_for_range_field(value, IntegerField)


class DecimalRangeField(Field):
    def clean(self, value):
        return _clean_data_for_range_field(value, DecimalField)


class BaseRangeFilter(Filter):
    field_class = None

    def filter(self, qs, values):
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


class DecimalRangeFilter(BaseRangeFilter):
    field_class = DecimalRangeField


def filter_age(field_name, qs, min, max):
    current = datetime.now().date()
    lookup_expr = "range"
    values = None
    if min is not None and max is not None:
        lookup_expr = "range"
        # min year +1 , day-1
        max_date = date(current.year - min, current.month, current.day,)
        min_date = date(current.year - max - 1, current.month, current.day,)
        min_date = min_date + timedelta(days=1)
        values = (min_date, max_date)
    elif min is not None and max is None:
        lookup_expr = "lte"
        max_date = date(current.year - min, current.month, current.day,)
        values = max_date
    elif min is None and max is not None:
        lookup_expr = "gte"
        # min year -1 , day+1
        min_date = date(current.year - max - 1, current.month, current.day,)
        min_date = min_date + timedelta(days=1)
        values = min_date
    return qs.filter(**{f"{field_name}__{lookup_expr}": values})


class AgeRangeFilter(Filter):
    field_class = IntegerRangeField

    def filter(self, qs, values):
        if values:
            min_value = values.get("min")  # 20
            max_value = values.get("max")  # 21
            current = datetime.now().date()
            if min_value is not None and max_value is not None:
                self.lookup_expr = "range"
                # min year +1 , day-1
                max_date = date(current.year - min_value, current.month, current.day,)
                min_date = date(current.year - max_value - 1, current.month, current.day,)
                min_date = min_date + timedelta(days=1)
                values = (min_date, max_date)
            elif min_value is not None and max_value is None:
                self.lookup_expr = "lte"
                max_date = date(current.year - min_value, current.month, current.day,)
                values = max_date
            elif min_value is None and max_value is not None:
                self.lookup_expr = "gte"
                # min year -1 , day+1
                min_date = date(current.year - max_value - 1, current.month, current.day,)
                min_date = min_date + timedelta(days=1)
                values = min_date
        return super().filter(qs, values)


class IntegerFilter(Filter):
    """Custom Integer filter to parse Decimal values."""

    field_class = IntegerField
