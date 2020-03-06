import json
from datetime import datetime, date

from django.forms import Field, IntegerField
from django_filters import Filter


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


class AgeRangeFilter(Filter):
    field_class = RangeField

    def filter(self, qs, values):
        if values:
            min_value = values.get("min")
            max_value = values.get("max")
            current = datetime.now().date()
            if min_value is not None and max_value is not None:
                self.lookup_expr = "range"
                min_date = date(
                    current.year - min_value, current.month, current.day,
                )
                max_date = date(
                    current.year - max_value, current.month, current.day,
                )
                values = (max_date, min_date)
            elif min_value is not None and max_value is None:
                self.lookup_expr = "lte"
                min_date = date(
                    current.year - min_value, current.month, current.day,
                )
                values = min_date
            elif min_value is None and max_value is not None:
                self.lookup_expr = "gte"
                max_date = date(
                    current.year - max_value, current.month, current.day,
                )
                values = max_date

        return super().filter(qs, values)
