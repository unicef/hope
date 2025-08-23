from datetime import datetime

import pytest
from e2e.page_object.programme_population.households import Households
from e2e.page_object.programme_population.households_details import HouseholdsDetails
from extras.test_utils.factories.core import (
    DataCollectingTypeFactory,
    create_afghanistan,
)
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from pytz import utc

from hope.apps.account.models import User
from hope.apps.core.models import BusinessArea, DataCollectingType
from hope.apps.geo.models import Area
from hope.apps.household.models import REFUGEE, Household
from hope.apps.program.models import BeneficiaryGroup, Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def create_programs() -> None:
    business_area = create_afghanistan()
    dct = DataCollectingTypeFactory(type=DataCollectingType.Type.STANDARD)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    ProgramFactory(
        name="Test Programm",
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=dct,
        beneficiary_group=beneficiary_group,
    )


@pytest.fixture
def add_household() -> Household:
    registration_data_import = RegistrationDataImportFactory(
        imported_by=User.objects.first(),
        business_area=BusinessArea.objects.first(),
        import_date=datetime(2022, 1, 29, tzinfo=utc),
    )
    household, individuals = create_household(
        {
            "registration_data_import": registration_data_import,
            "admin1": Area.objects.filter(name="Kabul").first(),
            "program": Program.objects.filter(name="Test Programm").first(),
            "size": 7,
            "residence_status": REFUGEE,
            "address": "938 Luna Cliffs Apt. 551 Jameschester, SC 24934",
            "village": "Small One",
        },
        {
            "registration_data_import": registration_data_import,
            "full_name": "Agata Kowalska",
        },
    )

    household.unicef_id = "HH-00-0000.1380"
    household.save()
    yield household


@pytest.mark.usefixtures("login")
class TestSmokeHouseholds:
    def test_smoke_page_households(
        self,
        create_programs: None,
        add_household: Household,
        page_households: Households,
    ) -> None:
        page_households.select_global_program_filter("Test Programm")
        page_households.get_nav_programme_population().click()
        page_households.get_nav_households().click()
        assert len(page_households.get_households_rows()) == 1
        assert "Items Groups" in page_households.get_table_title().text
        assert "Items Group ID" in page_households.get_household_id().text
        assert "Status" in page_households.get_status().text
        assert "Head of Items Group" in page_households.get_household_head_name().text
        assert "Items Group Size" in page_households.get_household_size().text
        assert "Administrative Level 2" in page_households.get_household_location().text
        assert "Residence Status" in page_households.get_household_residence_status().text
        assert "Total Cash Received" in page_households.get_household_total_cash_received().text
        assert "Registration Date" in page_households.get_household_registration_date().text

    def test_smoke_page_households_details(
        self,
        create_programs: None,
        add_household: Household,
        page_households: Households,
        page_households_details: HouseholdsDetails,
    ) -> None:
        page_households.select_global_program_filter("Test Programm")
        page_households.get_nav_programme_population().click()
        page_households.get_nav_households().click()
        page_households.get_households_row_by_number(0).click()
        assert "7" in page_households_details.get_label_household_size().text
        assert "Displaced | Refugee / Asylum Seeker" in page_households_details.get_label_residence_status().text
        assert "Agata Kowalska" in page_households_details.get_label_head_of_household().text
        assert "Afghanistan" in page_households_details.get_label_country().text
        assert "Afghanistan" in page_households_details.get_label_country_of_origin().text
        assert "938 Luna Cliffs Apt. 551 Jameschester, SC 24934" in page_households_details.get_label_address().text
        assert "Small One" in page_households_details.get_label_village().text
        assert "-" in page_households_details.get_label_zip_code().text
        assert "Kabul" in page_households_details.get_label_administrative_level_1().text
        assert "-" in page_households_details.get_label_administrative_level_2().text
        assert "-" in page_households_details.get_label_administrative_level_3().text
        assert "-" in page_households_details.get_label_administrative_level_4().text
        assert "-" in page_households_details.get_label_geolocation().text
        assert "-" in page_households_details.get_label_unhcr_case_id().text
        assert "-" in page_households_details.get_label_length_of_time_since_arrival().text
        assert "-" in page_households_details.get_label_number_of_times_displaced().text
        assert "-" in page_households_details.get_label_linked_grievances().text
        assert "USD 0.00" in page_households_details.get_label_cash_received().text
        assert "USD 0.00" in page_households_details.get_label_total_cash_received().text
        assert "Items Group Members" in page_households_details.get_table_title().text
        assert "Item ID" in page_households_details.get_table_label().text
        assert "ACTIVE" in page_households_details.get_status_container().text
        assert "No results" in page_households_details.get_table_row().text
        assert add_household.registration_data_import.data_source in page_households_details.get_label_source().text
        assert add_household.registration_data_import.name in page_households_details.get_label_import_name().text

        assert (
            add_household.last_registration_date.strftime("%-d %b %Y")
            in page_households_details.get_label_registration_date().text
        )
        assert (
            add_household.registration_data_import.imported_by.email
            in page_households_details.get_label_user_name().text
        )
