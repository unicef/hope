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
            if values.get("min") is not None and values.get("max") is not None:
                self.lookup_expr = "range"
                values = (values.get("min"), values.get("max"))
            elif values.get("min") is not None and values.get("max") is None:
                self.lookup_expr = "gte"
                values = values.get("min")
            elif values.get("min") is None and values.get("max") is not None:
                self.lookup_expr = "lte"
                values = values.get("max")

        return super().filter(qs, values)


class AgeRangeFilter(Filter):
    field_class = RangeField

    def filter(self, qs, values):
        if values:
            current = datetime.now().date()
            if values.get("min") is not None and values.get("max") is not None:
                self.lookup_expr = "range"
                min_date = date(
                    current.year - values.get("min"),
                    current.month,
                    current.day,
                )
                max_date = date(
                    current.year - values.get("max"),
                    current.month,
                    current.day,
                )
                values = (max_date, min_date)
            elif values.get("min") is not None and values.get("max") is None:
                self.lookup_expr = "lte"
                min_date = date(
                    current.year - values.get("min"),
                    current.month,
                    current.day,
                )
                values = min_date
            elif values.get("min") is None and values.get("max") is not None:
                self.lookup_expr = "gte"
                max_date = date(
                    current.year - values.get("max"),
                    current.month,
                    current.day,
                )
                values = max_date

        return super().filter(qs, values)
