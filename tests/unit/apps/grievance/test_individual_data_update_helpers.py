from unittest.mock import call, patch

import pytest

from extras.test_utils.factories import HouseholdFactory, IndividualFactory
from hope.apps.grievance.services.data_change.individual_data_update_service import (
    IndividualDataUpdateService,
    _handle_photo_field,
)
from hope.apps.household.const import SON_DAUGHTER
from hope.models import AsyncJob


@pytest.mark.parametrize(
    ("data", "handle_photo_result", "expected_data", "expected_calls"),
    [
        pytest.param({"name": "John", "age": 30}, None, {"name": "John", "age": 30}, [], id="no-photo-key"),
        pytest.param({}, None, {}, [], id="empty-dict"),
        pytest.param({"photo": None, "name": "John"}, None, {"photo": "", "name": "John"}, [], id="photo-is-none"),
        pytest.param(
            {"photo": "some_photo_data", "name": "John"},
            "saved/photo/path.jpg",
            {"photo": "saved/photo/path.jpg", "name": "John"},
            [call("some_photo_data", None, None)],
            id="photo-saved",
        ),
        pytest.param(
            {"photo": "some_photo_data", "name": "John"},
            None,
            {"name": "John"},
            [call("some_photo_data", None, None)],
            id="photo-not-saved",
        ),
        pytest.param(
            {"photo": "some_photo_data"},
            "",
            {},
            [call("some_photo_data", None, None)],
            id="photo-saved-as-an-empty-string",
        ),
        pytest.param(
            {"photo": {"some": "complex_data"}, "other_field": 42},
            "path/to/photo.png",
            {"photo": "path/to/photo.png", "other_field": 42},
            [call({"some": "complex_data"}, None, None)],
            id="photo-is-a-dict",
        ),
        pytest.param(
            {"name": "Jane", "age": 25, "address": "123 St"},
            None,
            {"name": "Jane", "age": 25, "address": "123 St"},
            [],
            id="other-keys-preserved",
        ),
    ],
)
@patch("hope.apps.grievance.services.data_change.individual_data_update_service.handle_photo")
def test_handle_photo_field(mock_handle_photo, data, handle_photo_result, expected_data, expected_calls):
    mock_handle_photo.return_value = handle_photo_result

    _handle_photo_field(data)

    assert data == expected_data
    assert mock_handle_photo.call_args_list == expected_calls


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
