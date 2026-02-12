"""Tests for DeduplicateTask extracted helper methods."""

from unittest.mock import MagicMock

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
from hope.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
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
        "expected_contains",
    ),
    [
        # exceeds max allowed
        (10, 5, 3, 10, 100, 10.0, "batch", "exceed the maximum allowed (5)"),
        # percentage threshold reached (set_size >= allowed, individuals > 1)
        (3, 10, 8, 5, 100, 10.0, "population", "The percentage of records (10.0%)"),
        # no threshold exceeded
        (3, 10, 3, 5, 100, 10.0, "batch", None),
        # percentage not triggered when individuals_count == 1
        (0, 10, 8, 5, 1, 10.0, "batch", None),
    ],
)
def test_check_duplicates_threshold(
    task,
    duplicates_count,
    max_allowed,
    duplicates_set_size,
    allowed_pct_count,
    individuals_count,
    threshold_pct,
    context,
    expected_contains,
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
    if expected_contains is None:
        assert result is None
    else:
        assert expected_contains in result


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


def test_finalize_successful_deduplication(task, rdi, business_area):
    pending_hh = PendingHouseholdFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=business_area,
    )
    PendingIndividualFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=business_area,
        household=pending_hh,
    )
    PendingIndividualFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=business_area,
        household=pending_hh,
    )

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
