"""Tests for RdiMergeTask extracted helpers."""

from unittest.mock import MagicMock, patch

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PendingDocumentFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.registration_datahub.tasks.rdi_merge import RdiMergeTask
from hope.models import (
    BusinessArea,
    Document,
    PendingHousehold,
    PendingIndividual,
    Program,
    RegistrationDataImport,
)
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def rdi(program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        status=RegistrationDataImport.IN_REVIEW,
    )


@pytest.fixture
def pending_household(rdi: RegistrationDataImport) -> PendingHousehold:
    return PendingHouseholdFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=rdi.business_area,
    )


@pytest.fixture
def pending_individual(rdi: RegistrationDataImport, pending_household: PendingHousehold) -> PendingIndividual:
    return PendingIndividualFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=rdi.business_area,
        household=pending_household,
    )


def test_update_merge_statuses_sets_merged_on_all_models(
    rdi: RegistrationDataImport,
    pending_household: PendingHousehold,
    pending_individual: PendingIndividual,
) -> None:
    PendingDocumentFactory(
        individual=pending_individual,
        program=rdi.program,
    )
    task = RdiMergeTask()
    task._update_merge_statuses([pending_household.id], [pending_individual.id])

    pending_household.refresh_from_db()
    pending_individual.refresh_from_db()
    assert pending_household.rdi_merge_status == MergeStatusModel.MERGED
    assert pending_individual.rdi_merge_status == MergeStatusModel.MERGED
    assert Document.all_objects.filter(
        individual=pending_individual,
        rdi_merge_status=MergeStatusModel.MERGED,
    ).exists()


def test_clear_cache_deletes_matching_keys(business_area: BusinessArea) -> None:
    mock_cache = MagicMock()
    mock_cache.keys.return_value = [
        f"count_{business_area.slug}_HouseholdNodeConnection_abc",
        f"count_{business_area.slug}_IndividualNodeConnection_xyz",
        "unrelated_key",
    ]

    task = RdiMergeTask()
    with patch("hope.apps.registration_datahub.tasks.rdi_merge.cache", mock_cache):
        task._clear_cache(business_area.slug)

    assert mock_cache.delete.call_count == 2
    mock_cache.delete.assert_any_call(f"count_{business_area.slug}_HouseholdNodeConnection_abc")
    mock_cache.delete.assert_any_call(f"count_{business_area.slug}_IndividualNodeConnection_xyz")


def test_clear_cache_suppresses_connection_error(business_area: BusinessArea) -> None:
    mock_cache = MagicMock()
    mock_cache.keys.side_effect = ConnectionError("Redis down")

    task = RdiMergeTask()
    with patch("hope.apps.registration_datahub.tasks.rdi_merge.cache", mock_cache):
        # Should not raise
        task._clear_cache(business_area.slug)
