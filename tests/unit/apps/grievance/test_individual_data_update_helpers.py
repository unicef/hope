from unittest.mock import patch

import pytest

from extras.test_utils.factories import HouseholdFactory, IndividualFactory
from hope.apps.grievance.services.data_change.individual_data_update_service import IndividualDataUpdateService
from hope.apps.household.const import SON_DAUGHTER
from hope.models import AsyncJob


def test_handle_photo_field_no_photo_key_dict_unchanged():
    from hope.apps.grievance.services.data_change.individual_data_update_service import _handle_photo_field

    data = {"name": "John", "age": 30}
    _handle_photo_field(data)
    assert data == {"name": "John", "age": 30}


def test_handle_photo_field_no_photo_key_empty_dict():
    from hope.apps.grievance.services.data_change.individual_data_update_service import _handle_photo_field

    data = {}
    _handle_photo_field(data)
    assert data == {}


def test_handle_photo_field_photo_is_none_sets_empty_string():
    from hope.apps.grievance.services.data_change.individual_data_update_service import _handle_photo_field

    data = {"photo": None, "name": "John"}
    _handle_photo_field(data)
    assert data["photo"] == ""
    assert data["name"] == "John"


@patch("hope.apps.grievance.services.data_change.individual_data_update_service.handle_photo")
def test_handle_photo_field_with_value_handle_photo_returns_result(mock_handle_photo):
    from hope.apps.grievance.services.data_change.individual_data_update_service import _handle_photo_field

    mock_handle_photo.return_value = "saved/photo/path.jpg"
    data = {"photo": "some_photo_data", "name": "John"}
    _handle_photo_field(data)
    assert data["photo"] == "saved/photo/path.jpg"
    mock_handle_photo.assert_called_once_with("some_photo_data", None)


@patch("hope.apps.grievance.services.data_change.individual_data_update_service.handle_photo")
def test_handle_photo_field_with_value_handle_photo_returns_none(mock_handle_photo):
    from hope.apps.grievance.services.data_change.individual_data_update_service import _handle_photo_field

    mock_handle_photo.return_value = None
    data = {"photo": "some_photo_data", "name": "John"}
    _handle_photo_field(data)
    # photo was popped and handle_photo returned None, so "photo" should not be in dict
    assert "photo" not in data
    assert data["name"] == "John"
    mock_handle_photo.assert_called_once_with("some_photo_data", None)


@patch("hope.apps.grievance.services.data_change.individual_data_update_service.handle_photo")
def test_handle_photo_field_with_value_handle_photo_returns_empty_string(mock_handle_photo):
    from hope.apps.grievance.services.data_change.individual_data_update_service import _handle_photo_field

    mock_handle_photo.return_value = ""
    data = {"photo": "some_photo_data"}
    _handle_photo_field(data)
    # empty string is falsy, so "photo" should not be in dict
    assert "photo" not in data


@patch("hope.apps.grievance.services.data_change.individual_data_update_service.handle_photo")
def test_handle_photo_field_with_truthy_value_sets_photo(mock_handle_photo):
    from hope.apps.grievance.services.data_change.individual_data_update_service import _handle_photo_field

    mock_handle_photo.return_value = "path/to/photo.png"
    data = {"photo": {"some": "complex_data"}, "other_field": 42}
    _handle_photo_field(data)
    assert data["photo"] == "path/to/photo.png"
    assert data["other_field"] == 42
    mock_handle_photo.assert_called_once_with({"some": "complex_data"}, None)


def test_handle_photo_field_preserves_other_keys():
    from hope.apps.grievance.services.data_change.individual_data_update_service import _handle_photo_field

    data = {"name": "Jane", "age": 25, "address": "123 St"}
    _handle_photo_field(data)
    assert data == {"name": "Jane", "age": 25, "address": "123 St"}


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
