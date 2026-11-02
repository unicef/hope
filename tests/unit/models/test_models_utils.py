from types import SimpleNamespace

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models
from django.test.utils import isolate_apps
import pytest

from extras.test_utils.factories import FlexibleAttributeGroupFactory
from hope.models import FlexibleAttributeGroup, Payment
from hope.models.utils import HorizontalChoiceArrayField, LongNameIndex, SignatureMixin


@pytest.fixture
def flexible_attribute_group():
    return FlexibleAttributeGroupFactory()


@pytest.fixture
def payment():
    return Payment()


@pytest.mark.django_db
def test_soft_deletion_tree_model_hard_delete_removes_row(flexible_attribute_group):
    flexible_attribute_group.delete(soft=False)

    assert not FlexibleAttributeGroup.all_objects.filter(id=flexible_attribute_group.id).exists()


def test_update_signature_hash_requires_signature_fields():
    with pytest.raises(ValueError, match="Define 'signature_fields' in class for SignatureMixin"):
        SignatureMixin.update_signature_hash(SimpleNamespace())


def test_signature_normalizes_nested_dictionaries_independently_of_key_order():
    first = {
        "outer": {"second": 2, "first": 1},
        "value": "same",
    }
    second = {
        "value": "same",
        "outer": {"first": 1, "second": 2},
    }

    first_normalized = SignatureMixin._normalize(SimpleNamespace(), "data", first)
    second_normalized = SignatureMixin._normalize(SimpleNamespace(), "data", second)

    assert first_normalized == second_normalized


def test_signature_normalization_preserves_value_for_non_model_field(payment):
    assert payment._normalize("non_model_field", "value") == "value"


def test_horizontal_choice_array_field_formfield_builds_multiple_choice_field():
    field = HorizontalChoiceArrayField(
        models.CharField(max_length=3, choices=[("A", "Letter A"), ("B", "Letter B")]),
        verbose_name="letters",
    )

    form_field = field.formfield()

    assert isinstance(form_field, forms.MultipleChoiceField)
    assert isinstance(form_field.widget, FilteredSelectMultiple)
    assert list(form_field.choices) == [("A", "Letter A"), ("B", "Letter B")]


@pytest.mark.parametrize(
    ("index_class", "expected_error_ids"),
    [
        (models.Index, ["models.E034"]),
        (LongNameIndex, []),
    ],
)
@isolate_apps("hope.apps.core")
def test_index_name_at_postgres_identifier_limit_passes_check_only_for_long_name_index(index_class, expected_error_ids):
    class Sample(models.Model):  # noqa: DJ008
        class Meta:
            app_label = "core"
            indexes = [index_class(fields=["id"], name="a" * 63)]

    errors = Sample._check_indexes(databases=[])

    assert [error.id for error in errors] == expected_error_ids
