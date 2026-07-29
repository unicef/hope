from pathlib import Path
from types import SimpleNamespace
from typing import Any

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import SuspiciousFileOperation
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models
from freezegun import freeze_time
import pytest

from extras.test_utils.factories import FlexibleAttributeGroupFactory
from hope.models import FlexibleAttributeGroup
from hope.models.utils import (
    HorizontalChoiceArrayField,
    SignatureMixin,
    save_unique_upload,
)


@pytest.fixture
def flexible_attribute_group():
    return FlexibleAttributeGroupFactory()


@pytest.fixture
def media_root(settings: Any, tmp_path: Path) -> Path:
    settings.MEDIA_ROOT = str(tmp_path)
    return tmp_path


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


def test_save_unique_upload_nests_the_file_under_the_prefix(media_root: Path) -> None:
    with freeze_time("2026-07-28"):
        saved_name = save_unique_upload(ContentFile(b"123"), "flex_field_image", "photo.jpg")

    assert saved_name.startswith("flex_field_image/2026/07/")
    assert saved_name.count("/") == 4
    assert saved_name.endswith("/photo.jpg")


def test_save_unique_upload_keeps_two_files_with_the_same_name_apart(media_root: Path) -> None:
    first_name = save_unique_upload(ContentFile(b"first"), "flex_field_image", "photo.jpg")
    second_name = save_unique_upload(ContentFile(b"second"), "flex_field_image", "photo.jpg")

    assert first_name != second_name
    assert default_storage.open(first_name).read() == b"first"
    assert default_storage.open(second_name).read() == b"second"


def test_save_unique_upload_strips_unsafe_characters_from_the_name(media_root: Path) -> None:
    saved_name = save_unique_upload(ContentFile(b"123"), "flex_field_image", "a b:c+d.jpg")

    assert saved_name.endswith("/a_bcd.jpg")


def test_save_unique_upload_rejects_a_traversing_name(media_root: Path) -> None:
    with pytest.raises(SuspiciousFileOperation):
        save_unique_upload(ContentFile(b"123"), "flex_field_image", "../../escaped.jpg")
