from types import SimpleNamespace

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import SuspiciousFileOperation
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models, transaction
from freezegun import freeze_time
import pytest

from extras.test_utils.factories import FlexibleAttributeGroupFactory, IndividualFactory, UniversalUpdateFactory
from hope.models import FlexibleAttributeGroup, Individual, UniversalUpdate
from hope.models.utils import (
    HorizontalChoiceArrayField,
    SignatureMixin,
    replace_upload,
    save_unique_upload,
)


@pytest.fixture
def flexible_attribute_group():
    return FlexibleAttributeGroupFactory()


@pytest.fixture
def universal_update() -> UniversalUpdate:
    return UniversalUpdateFactory()


@pytest.fixture
def legacy_template_name() -> str:
    """A name stored before the field had an upload_to, as the pre-migration rows hold it."""
    return default_storage.save("template.xlsx", ContentFile(b"legacy"))


@pytest.fixture
def legacy_prefixed_template_name() -> str:
    """A name under the prefix but not in the generated shape — what a bare prefix check would misread."""
    return default_storage.save("universal_update/template.xlsx", ContentFile(b"legacy"))


@pytest.fixture
def individual() -> Individual:
    return IndividualFactory()


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


def test_save_unique_upload_nests_the_file_under_the_prefix() -> None:
    with freeze_time("2026-07-28"):
        saved_name = save_unique_upload(ContentFile(b"123"), "flex_field_image", "photo.jpg")

    assert saved_name.startswith("flex_field_image/2026/07/")
    assert saved_name.count("/") == 4
    assert saved_name.endswith("/photo.jpg")


def test_save_unique_upload_keeps_two_files_with_the_same_name_apart() -> None:
    first_name = save_unique_upload(ContentFile(b"first"), "flex_field_image", "photo.jpg")
    second_name = save_unique_upload(ContentFile(b"second"), "flex_field_image", "photo.jpg")

    assert first_name != second_name
    assert default_storage.open(first_name).read() == b"first"
    assert default_storage.open(second_name).read() == b"second"


def test_save_unique_upload_strips_unsafe_characters_from_the_name() -> None:
    saved_name = save_unique_upload(ContentFile(b"123"), "flex_field_image", "a b:c+d.jpg")

    assert saved_name.endswith("/a_bcd.jpg")


def test_save_unique_upload_rejects_a_traversing_name() -> None:
    with pytest.raises(SuspiciousFileOperation):
        save_unique_upload(ContentFile(b"123"), "flex_field_image", "../../escaped.jpg")


@pytest.mark.django_db
def test_replace_upload_stores_a_file_on_an_empty_field(universal_update: UniversalUpdate) -> None:
    replace_upload(universal_update.template_file, "template.xlsx", ContentFile(b"first"))

    assert universal_update.template_file.name.startswith("universal_update/")
    assert universal_update.template_file.read() == b"first"


@pytest.mark.django_db
def test_replace_upload_deletes_the_file_it_replaces(
    universal_update: UniversalUpdate, django_capture_on_commit_callbacks
) -> None:
    universal_update.template_file.save("template.xlsx", ContentFile(b"first"))
    previous_name = universal_update.template_file.name

    with django_capture_on_commit_callbacks(execute=True):
        replace_upload(universal_update.template_file, "template.xlsx", ContentFile(b"second"))

    assert universal_update.template_file.name != previous_name
    assert not default_storage.exists(previous_name)
    assert universal_update.template_file.read() == b"second"


@pytest.mark.django_db
def test_replace_upload_keeps_a_legacy_flat_name(
    universal_update: UniversalUpdate,
    legacy_template_name: str,
    django_capture_on_commit_callbacks,
) -> None:
    universal_update.template_file = legacy_template_name
    universal_update.save()

    with django_capture_on_commit_callbacks(execute=True):
        replace_upload(universal_update.template_file, "template.xlsx", ContentFile(b"second"))

    assert default_storage.exists(legacy_template_name)
    assert universal_update.template_file.name.startswith("universal_update/")
    assert universal_update.template_file.read() == b"second"


@pytest.mark.django_db
def test_replace_upload_keeps_a_legacy_name_that_only_shares_the_prefix(
    universal_update: UniversalUpdate,
    legacy_prefixed_template_name: str,
    django_capture_on_commit_callbacks,
) -> None:
    universal_update.template_file = legacy_prefixed_template_name
    universal_update.save()

    with django_capture_on_commit_callbacks(execute=True):
        replace_upload(universal_update.template_file, "template.xlsx", ContentFile(b"second"))

    assert default_storage.exists(legacy_prefixed_template_name)
    assert universal_update.template_file.read() == b"second"


@pytest.mark.django_db
def test_replace_upload_keeps_the_previous_file_of_a_field_without_a_unique_upload_path(
    individual: Individual, django_capture_on_commit_callbacks
) -> None:
    individual.photo.save("photo.jpg", ContentFile(b"first"))
    previous_name = individual.photo.name

    with django_capture_on_commit_callbacks(execute=True):
        replace_upload(individual.photo, "photo.jpg", ContentFile(b"second"))

    assert individual.photo.name != previous_name
    assert default_storage.exists(previous_name)
    assert individual.photo.read() == b"second"


@pytest.mark.django_db
def test_replace_upload_does_not_fail_when_the_previous_file_cannot_be_deleted(
    universal_update: UniversalUpdate, django_capture_on_commit_callbacks, mocker
) -> None:
    universal_update.template_file.save("template.xlsx", ContentFile(b"first"))
    previous_name = universal_update.template_file.name
    mocked_delete = mocker.patch.object(
        universal_update.template_file.storage,
        "delete",
        side_effect=OSError("storage is unreachable"),
    )

    with django_capture_on_commit_callbacks(execute=True):
        replace_upload(universal_update.template_file, "template.xlsx", ContentFile(b"second"))

    mocked_delete.assert_called_once_with(previous_name)
    assert universal_update.template_file.read() == b"second"


@pytest.mark.django_db(transaction=True)
def test_replace_upload_keeps_the_previous_file_when_the_transaction_rolls_back(
    universal_update: UniversalUpdate,
) -> None:
    universal_update.template_file.save("template.xlsx", ContentFile(b"first"))
    previous_name = universal_update.template_file.name

    with transaction.atomic():
        replace_upload(universal_update.template_file, "template.xlsx", ContentFile(b"second"))
        transaction.set_rollback(True)

    assert default_storage.exists(previous_name)
