import json
from datetime import datetime, date, timedelta

from django.forms import Field, IntegerField
from django_filters import Filter, OrderingFilter


class RangeField(Field):
    def clean(self, value):
        if value:
            clean_data = {}
            values = json.loads(value)
            if isinstance(values, dict):
                for field_name, field_value in values.items():
                    clean_data[field_name] = IntegerField().clean(field_value)
            return clean_data or None
        else:
            return None


class IntegerRangeFilter(Filter):
    field_class = RangeField

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


def filter_age(field_name, qs, min, max):
    current = datetime.now().date()
    lookup_expr = "range"
    values = None
    if min is not None and max is not None:
        lookup_expr = "range"
        # year +1 , day-1
        max_date = date(current.year - min + 1, current.month, current.day,)
        max_date = max_date - timedelta(days=1)
        min_date = date(current.year - max, current.month, current.day,)
        values = (min_date, max_date)
    elif min is not None and max is None:
        lookup_expr = "lte"
        # year +1 , day-1
        max_date = date(current.year - min + 1, current.month, current.day,)
        max_date = max_date - timedelta(days=1)
        values = max_date
    elif min is None and max is not None:
        lookup_expr = "gte"
        min_date = date(current.year - max, current.month, current.day,)
        values = min_date
    return qs.filter(**{f"{field_name}__{lookup_expr}": values})


class AgeRangeFilter(Filter):
    field_class = RangeField

    def filter(self, qs, values):
        if values:
            min_value = values.get("min")  # 10
            max_value = values.get("max")  # 20
            current = datetime.now().date()
            if min_value is not None and max_value is not None:
                self.lookup_expr = "range"
                # year +1 , day-1
                max_date = date(
                    current.year - min_value + 1, current.month, current.day,
                )
                max_date = max_date - timedelta(days=1)
                min_date = date(
                    current.year - max_value, current.month, current.day,
                )
                values = (min_date, max_date)
            elif min_value is not None and max_value is None:
                self.lookup_expr = "lte"
                # year +1 , day-1
                max_date = date(
                    current.year - min_value + 1, current.month, current.day,
                )
                max_date = max_date - timedelta(days=1)
                values = max_date
            elif min_value is None and max_value is not None:
                self.lookup_expr = "gte"
                min_date = date(
                    current.year - max_value, current.month, current.day,
                )
                values = min_date

        return super().filter(qs, values)


class IntegerFilter(Filter):
    """Custom Integer filter to parse Decimal values."""

    field_class = IntegerField
