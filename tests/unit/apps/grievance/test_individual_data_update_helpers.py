import pytest

from extras.test_utils.factories import HouseholdFactory, IndividualFactory
from hope.apps.grievance.services.data_change.individual_data_update_service import (
    IndividualDataUpdateService,
)
from hope.apps.household.const import SON_DAUGHTER
from hope.models import AsyncJob

# --- _update_household_fields ---


@pytest.mark.django_db
def test_update_household_fields_without_country():
    from extras.test_utils.factories import BusinessAreaFactory, HouseholdFactory, ProgramFactory
    from hope.apps.grievance.services.data_change.individual_data_update_service import IndividualDataUpdateService

    business_area = BusinessAreaFactory()
    program = ProgramFactory(business_area=business_area)
    household = HouseholdFactory(business_area=business_area, program=program)

    service = IndividualDataUpdateService.__new__(IndividualDataUpdateService)

    only_approved_data = {"address": "New Address 123", "village": "New Village"}
    service._update_household_fields(household, only_approved_data)

    household.refresh_from_db()
    assert household.address == "New Address 123"
    assert household.village == "New Village"
    # country fields should not have been touched
    assert "country_origin" not in only_approved_data
    assert "country" not in only_approved_data


# --- _recalculate ---


@pytest.fixture
def household_member():
    household = HouseholdFactory()
    return IndividualFactory(
        household=household,
        program=household.program,
        business_area=household.business_area,
        registration_data_import=household.registration_data_import,
    )


@pytest.mark.django_db
def test_recalculate_recounts_program_when_relationship_approved(household_member, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        IndividualDataUpdateService._recalculate(household_member, {"relationship": SON_DAUGHTER})

    job = AsyncJob.objects.get(action="hope.apps.program.celery_tasks.adjust_program_size_async_task_action")
    assert job.config["program_id"] == str(household_member.program_id)


@pytest.mark.django_db
def test_recalculate_skips_program_recount_without_relationship(household_member, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        IndividualDataUpdateService._recalculate(household_member, {"given_name": "Anna"})

    assert not AsyncJob.objects.filter(
        action="hope.apps.program.celery_tasks.adjust_program_size_async_task_action"
    ).exists()
