from typing import Any

from django import forms
from django.contrib.postgres.fields import ArrayField


class ChoiceArrayField(ArrayField):
    def formfield(
        self,
        form_class: type[forms.Field] | None = ...,
        choices_form_class: type[forms.ChoiceField] | None = ...,
        **kwargs: Any,
    ) -> Any:
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)  # type: ignore[arg-type]
