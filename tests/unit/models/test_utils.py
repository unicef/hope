from django import forms
from django.db import models

from hope.models.utils import HorizontalChoiceArrayField


def test_horizontal_choice_array_field_formfield() -> None:
    base_field = models.CharField(max_length=20, choices=[("A", "Option A"), ("B", "Option B")])
    field = HorizontalChoiceArrayField(base_field=base_field, size=2)
    field.set_attributes_from_name("test_field")

    form_field = field.formfield()

    assert form_field is not None
    assert isinstance(form_field, forms.MultipleChoiceField)
