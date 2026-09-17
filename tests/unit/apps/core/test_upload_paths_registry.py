"""Checks that the project as a whole still conforms to the upload path resolver."""

from typing import Any

from django.apps import apps
from django.db import models
import pytest

from hope.apps.core.upload_paths import (
    BUSINESS_AREA_SLUG_PATH,
    OWNER_PATH,
    PROGRAM_PATH,
    upload_path,
)
from hope.models.program import Program

MODELS_STORING_AN_UPLOADED_FILE = {
    "accountability.Survey",
    "core.FileTemp",
    "core.StorageFile",
    "core.XLSXKoboTemplate",
    "grievance.GrievanceDocument",
    "household.Document",
    "household.Household",
    "household.Individual",
    "household.XlsxUpdateFile",
    "payment.PaymentPlanSupportingDocument",
    "periodic_data_update.PDUXlsxUpload",
    "registration_data.ImportData",
    "registration_data.KoboImportData",
    "sanction_list.UploadedXLSXFile",
    "universal_update_script.UniversalUpdate",
}

# A Kobo questionnaire template and a sanction list screening batch have no business area and no
# programme to be filed under, so `_global` is where they belong.
MODELS_WITHOUT_A_BUSINESS_AREA_OR_PROGRAMME = {"core.XLSXKoboTemplate", "sanction_list.UploadedXLSXFile"}

# An account attachment is filed per individual and account by an `upload_to` of its own.
FIELDS_WITH_THEIR_OWN_LAYOUT = {"payment.AccountAttachment.file"}


def _models_storing_an_uploaded_file() -> set[type[models.Model]]:
    """Ask the app registry which models actually store a file, so a new one cannot go unnoticed.

    Reads `concrete_fields`, not `local_fields`, so a model inheriting the field through a
    multi-table parent is listed in its own right rather than hidden behind the parent that
    declares it.
    """
    return {
        model._meta.concrete_model
        for model in apps.get_models()
        for field in model._meta.concrete_fields
        if isinstance(field, models.FileField) and field.upload_to is upload_path
    }


def _labels_of(model: type[models.Model]) -> set[str]:
    """The model's own label and its parents', because an entry registered for a parent covers a
    multi-table child such as `KoboImportData`, which carries a label of its own.
    """
    meta = model._meta.concrete_model._meta
    return {ancestor._meta.label for ancestor in (meta.model, *meta.all_parents)}


def _field_at(label: str, path: str) -> Any:
    """Walk a resolver path field by field, so a typo in any segment raises `FieldDoesNotExist`.

    A misspelt path is silent in production: `nested_getattr` swallows it, the resolver finds no
    scope and the file lands under `_unassigned` instead of where it belongs.
    """
    meta = apps.get_model(label)._meta
    *relations, last = path.split(".")
    for relation in relations:
        meta = meta.get_field(relation).related_model._meta
    return meta.get_field(last)


@pytest.mark.parametrize(("label", "path"), sorted(PROGRAM_PATH.items()))
def test_every_program_path_ends_at_the_programme(label: str, path: str) -> None:
    assert _field_at(label, path).related_model is Program


@pytest.mark.parametrize(("label", "path"), sorted(OWNER_PATH.items()))
def test_every_owner_path_ends_at_a_relation(label: str, path: str) -> None:
    """An owner is another object for the resolver to read in turn, not a value."""
    assert _field_at(label, path).is_relation


@pytest.mark.parametrize(("label", "path"), sorted(BUSINESS_AREA_SLUG_PATH.items()))
def test_every_business_area_slug_path_ends_at_the_slug(label: str, path: str) -> None:
    """A path stopping a segment short, at the business area itself, hands the resolver an object
    where it expects text.
    """
    assert isinstance(_field_at(label, path), models.CharField)


def test_every_file_field_uploads_through_the_resolver() -> None:
    """A file field declared with any other `upload_to` writes outside the folder structure, unless listed."""
    skipping_the_resolver = {
        f"{field.model._meta.label}.{field.name}"
        for model in apps.get_models()
        for field in model._meta.local_fields
        if isinstance(field, models.FileField) and field.upload_to is not upload_path
    }

    assert skipping_the_resolver == FIELDS_WITH_THEIR_OWN_LAYOUT


def test_every_model_storing_an_uploaded_file_is_listed_here() -> None:
    """A mismatch means a model started or stopped storing uploads without anyone noticing."""
    assert {model._meta.label for model in _models_storing_an_uploaded_file()} == MODELS_STORING_AN_UPLOADED_FILE


def test_only_the_scopeless_models_have_no_scope_declared() -> None:
    """A model with no scope declared files every upload into the shared `_global` folder."""
    # A model has a scope declared when one of the three registries covers it, under its own label
    # or an ancestor's, or when it carries the attribute a default path starts from. A declared
    # route is not a guarantee that it resolves against a real object.
    registered = {*PROGRAM_PATH, *OWNER_PATH, *BUSINESS_AREA_SLUG_PATH}

    scopeless = {
        model._meta.label
        for model in _models_storing_an_uploaded_file()
        if not _labels_of(model) & registered and not hasattr(model, "program") and not hasattr(model, "business_area")
    }

    assert scopeless == MODELS_WITHOUT_A_BUSINESS_AREA_OR_PROGRAMME
