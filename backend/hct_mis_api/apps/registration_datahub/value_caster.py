import abc
from datetime import date, datetime
from typing import Any, List, Optional, Union

from dateutil.parser import parse

from hct_mis_api.apps.core.field_attributes.fields_types import (
    TYPE_BOOL,
    TYPE_DATE,
    TYPE_DECIMAL,
    TYPE_INTEGER,
    TYPE_SELECT_MANY,
    TYPE_SELECT_ONE,
    TYPE_STRING,
)


class BaseValueCaster(abc.ABC):
    def __init__(self, next_caster: Optional["BaseValueCaster"] = None):
        self._next_caster = next_caster

    @abc.abstractmethod
    def can_process(self, field: Any) -> bool:
        pass

    @abc.abstractmethod
    def process(self, field: Any, value: Any) -> Any:
        pass

    def cast(self, field: Any, value: Any) -> Any:
        if self.can_process(field):
            return self.process(field, value)
        return self._next_caster.cast(field, value)


class StringValueCaster(BaseValueCaster):
    def can_process(self, field: Any) -> bool:
        return field["type"] == TYPE_STRING

    def process(self, field: Any, value: Any) -> str:
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return str(value)


class IntegerValueCaster(BaseValueCaster):
    def can_process(self, field: Any) -> bool:
        return field["type"] == TYPE_INTEGER

    def process(self, field: Any, value: Any) -> int:
        return int(value)


class DecimalValueCaster(BaseValueCaster):
    def can_process(self, field: Any) -> bool:
        return field["type"] == TYPE_DECIMAL

    def process(self, field: Any, value: Any) -> float:
        return float(value)


class SelectManyValueCaster(BaseValueCaster):
    def can_process(self, field: Any) -> bool:
        return field["type"] == TYPE_SELECT_MANY

    def process(self, field: Any, value: Any) -> List:
        if custom_cast_method := field.get("custom_cast_value"):
            return custom_cast_method(input_value=value)

        choices = [x.get("value") for x in field["choices"]]

        if "," in value:
            values = value.split(",")
        elif ";" in value:
            values = value.split(";")
        else:
            values = value.split(" ")
        valid_choices: List = []
        for single_choice in values:
            if isinstance(single_choice, str):
                without_trailing_whitespace = single_choice.strip()
                if without_trailing_whitespace in choices:
                    valid_choices.append(without_trailing_whitespace)
                    continue
                upper_value = without_trailing_whitespace.upper()
                if upper_value in choices:
                    valid_choices.append(upper_value)
                    continue

            if single_choice not in choices:
                try:
                    valid_choices.append(int(single_choice))
                except ValueError:
                    valid_choices.append(str(single_choice))
        return valid_choices


class SelectOneValueCaster(BaseValueCaster):
    def can_process(self, field: Any) -> bool:
        return field["type"] == TYPE_SELECT_ONE

    def process(self, field: Any, value: Any) -> Optional[Union[int, str]]:
        if custom_cast_method := field.get("custom_cast_value"):
            return custom_cast_method(input_value=value)

        choices = [x.get("value") for x in field["choices"]]

        if field.get("xlsx_field").endswith(("_i_f", "_h_f")):
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            value = str(value)
        if isinstance(value, str):
            without_trailing_whitespace = value.strip()
            if without_trailing_whitespace in choices:
                return without_trailing_whitespace

            upper_value = without_trailing_whitespace.upper()
            if upper_value in choices:
                return upper_value

        if value not in choices:
            try:
                return int(value)
            except ValueError:
                return str(value)

        return None


class DateValueCaster(BaseValueCaster):
    def can_process(self, field: Any) -> bool:
        return field["type"] == TYPE_DATE

    def process(self, field: Any, value: Union[date, datetime, str]) -> Union[date, datetime]:
        if isinstance(value, (date, datetime)):
            return value

        if isinstance(value, str):
            return parse(value)


class BooleanValueCaster(BaseValueCaster):
    def can_process(self, field: Any) -> bool:
        return field["type"] == TYPE_BOOL

    def process(self, field: Any, value: Union[bool, str]) -> Union[bool, str]:
        if isinstance(value, str):
            if value.lower() == "false":
                return False
            elif value.lower() == "true":
                return True
        return value


class DefaultValueCaster(BaseValueCaster):
    def can_process(self, field: Any) -> bool:
        return True

    def process(self, field: Any, value: Any) -> Any:
        return value
