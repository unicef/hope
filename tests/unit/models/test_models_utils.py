from types import SimpleNamespace

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models
import pytest

from extras.test_utils.factories import FlexibleAttributeGroupFactory
from hope.models import FlexibleAttributeGroup
from hope.models.utils import HorizontalChoiceArrayField, SignatureMixin


@pytest.fixture
def flexible_attribute_group():
    return FlexibleAttributeGroupFactory()


@pytest.mark.django_db
def test_soft_deletion_tree_model_hard_delete_removes_row(flexible_attribute_group):
    flexible_attribute_group.delete(soft=False)

    assert not FlexibleAttributeGroup.all_objects.filter(id=flexible_attribute_group.id).exists()


def test_update_signature_hash_requires_signature_fields():
    with pytest.raises(ValueError, match="Define 'signature_fields' in class for SignatureMixin"):
        SignatureMixin.update_signature_hash(SimpleNamespace())


def test_horizontal_choice_array_field_formfield_builds_multiple_choice_field():
    field = HorizontalChoiceArrayField(
        models.CharField(max_length=3, choices=[("A", "Letter A"), ("B", "Letter B")]),
        verbose_name="letters",
    )

    form_field = field.formfield()

    assert isinstance(form_field, forms.MultipleChoiceField)
    assert isinstance(form_field.widget, FilteredSelectMultiple)
    assert list(form_field.choices) == [("A", "Letter A"), ("B", "Letter B")]
