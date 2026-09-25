import pytest

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
