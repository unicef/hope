from typing import Any

from django import forms
from django.contrib.postgres.fields import ArrayField


class ChoiceArrayField(ArrayField):
    def formfield(self, form_class: Any | None = None, **kwargs: Any) -> Any:
        if form_class is None:
            form_class = forms.MultipleChoiceField
        defaults = {
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)
        return super().formfield(form_class, **defaults)
