from unittest.mock import MagicMock

from django.core.exceptions import ValidationError
import pytest

from hope.apps.household.const import HEAD
from hope.contrib.aurora.services.generic_registration_service import (
    ACCOUNT_FIELD,
    DOCUMENT_FIELD,
    EXTRA_FIELD,
    INDIVIDUAL_FIELD,
    PRIMARY_COLLECTOR,
    SECONDARY_COLLECTOR,
    GenericRegistrationService,
)


@pytest.fixture
def service():
    mock_registration = MagicMock()
    return GenericRegistrationService(mock_registration)


@pytest.fixture
def make_individual():
    def _factory(relationship=""):
        individual = MagicMock()
        individual.relationship = relationship
        return individual

    return _factory


# ---------------------------------------------------------------------------
# _apply_mapped_value
# ---------------------------------------------------------------------------


def test_individual_field_sets_value_on_dict():
    my_dict = {}
    GenericRegistrationService._apply_mapped_value(my_dict, INDIVIDUAL_FIELD, "given_name", "John")
    assert my_dict["given_name"] == "John"


def test_individual_field_overwrites_existing_value():
    my_dict = {"given_name": "OldName"}
    GenericRegistrationService._apply_mapped_value(my_dict, INDIVIDUAL_FIELD, "given_name", "NewName")
    assert my_dict["given_name"] == "NewName"


def test_document_field_creates_new_doc_entry():
    my_dict = {"documents": {}}
    GenericRegistrationService._apply_mapped_value(my_dict, DOCUMENT_FIELD, "doc_tax-document_number", "ABC123")
    assert my_dict["documents"]["doc_tax"]["document_number"] == "ABC123"


def test_document_field_updates_existing_doc_entry():
    my_dict = {"documents": {"doc_tax": {"key": "tax_id"}}}
    GenericRegistrationService._apply_mapped_value(my_dict, DOCUMENT_FIELD, "doc_tax-document_number", "ABC123")
    assert my_dict["documents"]["doc_tax"]["key"] == "tax_id"
    assert my_dict["documents"]["doc_tax"]["document_number"] == "ABC123"


def test_document_field_parses_field_with_dash():
    my_dict = {"documents": {}}
    GenericRegistrationService._apply_mapped_value(my_dict, DOCUMENT_FIELD, "doc_birth-key", "birth_certificate")
    assert my_dict["documents"]["doc_birth"]["key"] == "birth_certificate"


def test_document_field_multiple_documents():
    my_dict = {"documents": {}}
    GenericRegistrationService._apply_mapped_value(my_dict, DOCUMENT_FIELD, "doc_tax-key", "tax_id")
    GenericRegistrationService._apply_mapped_value(my_dict, DOCUMENT_FIELD, "doc_birth-key", "birth_certificate")
    assert my_dict["documents"]["doc_tax"]["key"] == "tax_id"
    assert my_dict["documents"]["doc_birth"]["key"] == "birth_certificate"


def test_account_field_sets_value():
    my_dict = {ACCOUNT_FIELD: {}}
    GenericRegistrationService._apply_mapped_value(my_dict, ACCOUNT_FIELD, "bank_name", "UNICEF Bank")
    assert my_dict[ACCOUNT_FIELD]["bank_name"] == "UNICEF Bank"


def test_account_field_multiple_fields():
    my_dict = {ACCOUNT_FIELD: {}}
    GenericRegistrationService._apply_mapped_value(my_dict, ACCOUNT_FIELD, "bank_name", "UNICEF Bank")
    GenericRegistrationService._apply_mapped_value(my_dict, ACCOUNT_FIELD, "number", "12345")
    assert my_dict[ACCOUNT_FIELD]["bank_name"] == "UNICEF Bank"
    assert my_dict[ACCOUNT_FIELD]["number"] == "12345"


def test_extra_field_sets_value():
    my_dict = {"extra": {}}
    GenericRegistrationService._apply_mapped_value(my_dict, EXTRA_FIELD, "custom_field", "custom_value")
    assert my_dict["extra"]["custom_field"] == "custom_value"


def test_extra_field_multiple_fields():
    my_dict = {"extra": {}}
    GenericRegistrationService._apply_mapped_value(my_dict, EXTRA_FIELD, "field_a", "value_a")
    GenericRegistrationService._apply_mapped_value(my_dict, EXTRA_FIELD, "field_b", "value_b")
    assert my_dict["extra"]["field_a"] == "value_a"
    assert my_dict["extra"]["field_b"] == "value_b"


def test_unknown_model_does_not_modify_dict():
    my_dict = {"extra": {}, "documents": {}, ACCOUNT_FIELD: {}}
    original = {k: dict(v) for k, v in my_dict.items()}
    GenericRegistrationService._apply_mapped_value(my_dict, "unknown_model", "field", "value")
    assert my_dict == original


# ---------------------------------------------------------------------------
# _assign_individual_roles
# ---------------------------------------------------------------------------


def test_head_assignment(service, make_individual):
    individual = make_individual(relationship=HEAD)
    head, pr_collector, sec_collector = service._assign_individual_roles(individual, {}, None, None, None)
    assert head is individual
    assert pr_collector is None
    assert sec_collector is None


def test_duplicate_head_raises_validation_error(service, make_individual):
    individual = make_individual(relationship=HEAD)
    existing_head = make_individual(relationship=HEAD)
    with pytest.raises(ValidationError, match="Head of Household already exist"):
        service._assign_individual_roles(individual, {}, existing_head, None, None)


def test_primary_collector_assignment(service, make_individual):
    individual = make_individual(relationship="SON_DAUGHTER")
    extra_data = {PRIMARY_COLLECTOR: "1"}
    head, pr_collector, sec_collector = service._assign_individual_roles(individual, extra_data, None, None, None)
    assert head is None
    assert pr_collector is individual
    assert sec_collector is None


def test_primary_collector_with_yes_string(service, make_individual):
    individual = make_individual(relationship="SON_DAUGHTER")
    extra_data = {PRIMARY_COLLECTOR: "y"}
    head, pr_collector, sec_collector = service._assign_individual_roles(individual, extra_data, None, None, None)
    assert pr_collector is individual


def test_duplicate_primary_collector_raises_validation_error(service, make_individual):
    individual = make_individual(relationship="SON_DAUGHTER")
    existing_pr_collector = make_individual()
    extra_data = {PRIMARY_COLLECTOR: "1"}
    with pytest.raises(ValidationError, match="Primary Collector already exist"):
        service._assign_individual_roles(individual, extra_data, None, existing_pr_collector, None)


def test_secondary_collector_assignment(service, make_individual):
    individual = make_individual(relationship="SON_DAUGHTER")
    extra_data = {SECONDARY_COLLECTOR: "1"}
    head, pr_collector, sec_collector = service._assign_individual_roles(individual, extra_data, None, None, None)
    assert head is None
    assert pr_collector is None
    assert sec_collector is individual


def test_duplicate_secondary_collector_raises_validation_error(service, make_individual):
    individual = make_individual(relationship="SON_DAUGHTER")
    existing_sec_collector = make_individual()
    extra_data = {SECONDARY_COLLECTOR: "1"}
    with pytest.raises(ValidationError, match="Secondary Collector already exist"):
        service._assign_individual_roles(individual, extra_data, None, None, existing_sec_collector)


def test_head_and_primary_collector_combined(service, make_individual):
    individual = make_individual(relationship=HEAD)
    extra_data = {PRIMARY_COLLECTOR: "y"}
    head, pr_collector, sec_collector = service._assign_individual_roles(individual, extra_data, None, None, None)
    assert head is individual
    assert pr_collector is individual
    assert sec_collector is None


def test_non_head_without_collector_flags(service, make_individual):
    individual = make_individual(relationship="SON_DAUGHTER")
    head, pr_collector, sec_collector = service._assign_individual_roles(individual, {}, None, None, None)
    assert head is None
    assert pr_collector is None
    assert sec_collector is None


def test_preserves_existing_head_when_not_head(service, make_individual):
    existing_head = make_individual(relationship=HEAD)
    individual = make_individual(relationship="SON_DAUGHTER")
    head, pr_collector, sec_collector = service._assign_individual_roles(individual, {}, existing_head, None, None)
    assert head is existing_head


def test_preserves_existing_collectors_when_no_flags(service, make_individual):
    existing_pr = make_individual()
    existing_sec = make_individual()
    individual = make_individual(relationship="SON_DAUGHTER")
    head, pr_collector, sec_collector = service._assign_individual_roles(
        individual, {}, None, existing_pr, existing_sec
    )
    assert pr_collector is existing_pr
    assert sec_collector is existing_sec


def test_primary_collector_false_does_not_assign(service, make_individual):
    individual = make_individual(relationship="SON_DAUGHTER")
    extra_data = {PRIMARY_COLLECTOR: "0"}
    head, pr_collector, sec_collector = service._assign_individual_roles(individual, extra_data, None, None, None)
    assert pr_collector is None


def test_secondary_collector_false_does_not_assign(service, make_individual):
    individual = make_individual(relationship="SON_DAUGHTER")
    extra_data = {SECONDARY_COLLECTOR: "0"}
    head, pr_collector, sec_collector = service._assign_individual_roles(individual, extra_data, None, None, None)
    assert sec_collector is None
