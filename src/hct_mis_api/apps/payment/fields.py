from typing import Any

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.postgres.fields import ArrayField


class DynamicChoiceField(forms.MultipleChoiceField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Set the choices callable to be evaluated later
        kwargs.pop("base_field", None)
        kwargs.pop("max_length", None)
        choices = kwargs.pop("choices_callable", ())
        super().__init__(choices=choices, **kwargs)


class DynamicChoiceArrayField(ArrayField):
    def __init__(self, base_field: Any, *args: Any, **kwargs: Any) -> None:
        self.choices_callable = kwargs.pop("choices_callable", None)
        super().__init__(base_field, *args, **kwargs)

    def formfield(self, **kwargs: Any) -> forms.Field:  # type: ignore
        widget = FilteredSelectMultiple(self.verbose_name, False)
        defaults = {
            "form_class": DynamicChoiceField,
            "widget": widget,
            "choices_callable": self.choices_callable,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
