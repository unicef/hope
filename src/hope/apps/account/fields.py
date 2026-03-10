from typing import Any

from django import forms
from django.contrib.postgres.fields import ArrayField


class ChoiceArrayField(ArrayField):
    def formfield(self, form_class: type[forms.Field] | None = None, choices_form_class: type[forms.ChoiceField] | None = None, **kwargs: Any) -> Any:
        kwargs["choices"] = self.base_field.choices
        return super(ArrayField, self).formfield(
            form_class=form_class or forms.MultipleChoiceField,
            choices_form_class=choices_form_class,
            **kwargs,
        )
