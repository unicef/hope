from typing import Any

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.postgres.fields import ArrayField


class DynamicChoiceField(forms.MultipleChoiceField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.pop("base_field", None)
        kwargs.pop("max_length", None)

        choices_callable = kwargs.pop("choices_callable", None)
        if callable(choices_callable):
            choices = choices_callable()
        else:
            choices = choices_callable or ()

        super().__init__(*args, choices=choices, **kwargs)


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
