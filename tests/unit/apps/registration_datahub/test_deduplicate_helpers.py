"""Tests for DeduplicateTask extracted helper methods."""

from unittest.mock import MagicMock
import uuid

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.household.const import (
    DUPLICATE_IN_BATCH,
    UNIQUE_IN_BATCH,
)
from hope.apps.registration_datahub.tasks.deduplicate import DeduplicateTask, HardDocumentDeduplication
from hope.models import (
    BusinessArea,
    Program,
    RegistrationDataImport,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def task(business_area: BusinessArea, program: Program) -> DeduplicateTask:
    return DeduplicateTask(business_area.slug, str(program.id))


@pytest.fixture
def rdi(program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        status=RegistrationDataImport.DEDUPLICATION,
    )


@pytest.fixture
def pending_household_for_finalize(rdi, business_area):
    return PendingHouseholdFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=business_area,
    )


@pytest.fixture
def pending_individuals_for_finalize(rdi, business_area, pending_household_for_finalize):
    return [
        PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=business_area,
            household=pending_household_for_finalize,
        )
        for _ in range(2)
    ]


# --- _check_duplicates_threshold ---


@pytest.mark.parametrize(
    (
        "duplicates_count",
        "max_allowed",
        "duplicates_set_size",
        "allowed_pct_count",
        "individuals_count",
        "threshold_pct",
        "context",
        "expected_none_reason",
    ),
    [
        # no threshold exceeded
        (3, 10, 3, 5, 100, 10.0, "batch", "below max and below percentage"),
        # percentage not triggered when individuals_count == 1
        (0, 10, 8, 5, 1, 10.0, "batch", "individuals_count == 1 skips percentage check"),
    ],
)
def test_check_duplicates_threshold_returns_none(
    task,
    duplicates_count,
    max_allowed,
    duplicates_set_size,
    allowed_pct_count,
    individuals_count,
    threshold_pct,
    context,
    expected_none_reason,
):
    result = task._check_duplicates_threshold(
        duplicates_count,
        max_allowed,
        duplicates_set_size,
        allowed_pct_count,
        individuals_count,
        threshold_pct,
        context,
    )
    assert result is None


@pytest.mark.parametrize(
    (
        "duplicates_count",
        "max_allowed",
        "duplicates_set_size",
        "allowed_pct_count",
        "individuals_count",
        "threshold_pct",
        "context",
        "expected_substring",
    ),
    [
        # exceeds max allowed
        (10, 5, 3, 10, 100, 10.0, "batch", "exceed the maximum allowed (5)"),
        # percentage threshold reached (set_size >= allowed, individuals > 1)
        (3, 10, 8, 5, 100, 10.0, "population", "The percentage of records (10.0%)"),
    ],
)
def test_check_duplicates_threshold_returns_error_message(
    task,
    duplicates_count,
    max_allowed,
    duplicates_set_size,
    allowed_pct_count,
    individuals_count,
    threshold_pct,
    context,
    expected_substring,
):
    result = task._check_duplicates_threshold(
        duplicates_count,
        max_allowed,
        duplicates_set_size,
        allowed_pct_count,
        individuals_count,
        threshold_pct,
        context,
    )
    assert expected_substring in result


# --- _set_deduplication_batch_status ---


def test_set_deduplication_batch_status_duplicates(task):
    result = MagicMock()
    result.results_data = {"duplicates": [{"some": "data"}]}
    pending = MagicMock()
    task._set_deduplication_batch_status(result, pending)
    assert pending.deduplication_batch_status == DUPLICATE_IN_BATCH


def test_set_deduplication_batch_status_unique(task):
    result = MagicMock()
    result.results_data = {"duplicates": []}
    pending = MagicMock()
    task._set_deduplication_batch_status(result, pending)
    assert pending.deduplication_batch_status == UNIQUE_IN_BATCH


# --- _set_error_message_and_status ---


def test_set_error_message_and_status(task, rdi):
    task._set_error_message_and_status(rdi, "Some error occurred")
    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.DEDUPLICATION_FAILED
    assert rdi.error_message == "Some error occurred"


# --- _finalize_successful_deduplication ---


def test_finalize_successful_deduplication(task, rdi, pending_household_for_finalize, pending_individuals_for_finalize):
    task._finalize_successful_deduplication(
        rdi,
        duplicates_in_batch=set(),
        possible_duplicates_in_batch=set(),
        duplicates_in_population=set(),
        possible_duplicates_in_population=set(),
    )
    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.IN_REVIEW
    assert rdi.error_message == ""


# --- HardDocumentDeduplication._build_document_signatures ---


def test_build_document_signatures_empty():
    dedup = HardDocumentDeduplication()
    documents_numbers, new_sigs, per_individual_dict, duplicated = dedup._build_document_signatures([])

    assert documents_numbers == []
    assert new_sigs == []
    assert dict(per_individual_dict) == {}
    assert duplicated == []


def test_build_document_signatures_single_doc():
    dedup = HardDocumentDeduplication()
    individual_id = uuid.uuid4()

    doc = MagicMock()
    doc.document_number = "DOC-001"
    doc.individual_id = individual_id
    doc.type.valid_for_deduplication = True
    doc.type_id = "passport"
    doc.country_id = "AFG"

    documents_numbers, new_sigs, per_individual_dict, duplicated = dedup._build_document_signatures([doc])

    expected_sig = "passport--DOC-001--AFG"
    assert documents_numbers == ["DOC-001"]
    assert new_sigs == [expected_sig]
    assert per_individual_dict[str(individual_id)] == [expected_sig]
    assert duplicated == []


def test_build_document_signatures_duplicates():
    dedup = HardDocumentDeduplication()
    individual_id_1 = uuid.uuid4()
    individual_id_2 = uuid.uuid4()

    doc1 = MagicMock()
    doc1.document_number = "DOC-001"
    doc1.individual_id = individual_id_1
    doc1.type.valid_for_deduplication = True
    doc1.type_id = "passport"
    doc1.country_id = "AFG"

    doc2 = MagicMock()
    doc2.document_number = "DOC-001"
    doc2.individual_id = individual_id_2
    doc2.type.valid_for_deduplication = True
    doc2.type_id = "passport"
    doc2.country_id = "AFG"

    documents_numbers, new_sigs, per_individual_dict, duplicated = dedup._build_document_signatures([doc1, doc2])

    expected_sig = "passport--DOC-001--AFG"
    assert documents_numbers == ["DOC-001", "DOC-001"]
    assert new_sigs == [expected_sig, expected_sig]
    assert per_individual_dict[str(individual_id_1)] == [expected_sig]
    assert per_individual_dict[str(individual_id_2)] == [expected_sig]
    assert duplicated == [expected_sig, expected_sig]
