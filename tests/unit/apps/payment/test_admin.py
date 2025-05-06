from django import forms
from django.test import TestCase

from hct_mis_api.apps.payment.admin import ArrayFieldWidget, CommaSeparatedArrayField


class ArrayFieldWidgetTests(TestCase):
    def setUp(self) -> None:
        self.widget = ArrayFieldWidget()

    def test_format_value_none(self) -> None:
        assert self.widget.format_value(None) == ""

    def test_format_value_list(self) -> None:
        assert self.widget.format_value(["apple", "banana", "cherry"]) == "apple\nbanana\ncherry"

    def test_format_value_string(self) -> None:
        assert self.widget.format_value("test") == "test"

    def test_value_from_datadict_empty(self) -> None:
        assert self.widget.value_from_datadict({}, {}, "field_name") == []

    def test_value_from_datadict_list(self) -> None:
        data = {"field_name": "apple\n  banana  \ncherry"}
        assert self.widget.value_from_datadict(data, {}, "field_name") == ["apple", "banana", "cherry"]


class CommaSeparatedArrayFieldTests(TestCase):
    def setUp(self) -> None:
        self.field = CommaSeparatedArrayField()

    def test_prepare_value_none(self) -> None:
        assert self.field.prepare_value(None) == ""

    def test_prepare_value_list(self) -> None:
        assert self.field.prepare_value(["apple", "banana", "cherry"]) == "apple\nbanana\ncherry"

    def test_to_python_empty(self) -> None:
        assert self.field.to_python("") == []

    def test_to_python_list(self) -> None:
        assert self.field.to_python(["apple", "banana"]) == ["apple", "banana"]

    def test_to_python_string(self) -> None:
        assert self.field.to_python("apple\nbanana\ncherry") == ["apple", "banana", "cherry"]

    def test_validate_valid(self) -> None:
        try:
            self.field.validate(["apple", "banana"])
        except forms.ValidationError:
            self.fail("validate() raised ValidationError unexpectedly!")
