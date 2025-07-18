from datetime import datetime

import pytest
from pytz import utc

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory, create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import REFUGEE, Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import BeneficiaryGroup, Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from tests.selenium.page_object.programme_population.households import Households
from tests.selenium.page_object.programme_population.households_details import (
    HouseholdsDetails,
)

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
            "admin2": Area.objects.order_by("?").first(),
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
    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_smoke_page_households(
        self, create_programs: None, add_household: Household, pageHouseholds: Households
    ) -> None:
        pageHouseholds.selectGlobalProgramFilter("Test Programm")
        pageHouseholds.getNavProgrammePopulation().click()
        pageHouseholds.getNavHouseholds().click()
        assert 1 == len(pageHouseholds.getHouseholdsRows())
        assert "Items Groups" in pageHouseholds.getTableTitle().text
        assert "Items Group ID" in pageHouseholds.getHouseholdId().text
        assert "Status" in pageHouseholds.getStatus().text
        assert "Head of Items Group" in pageHouseholds.getHouseholdHeadName().text
        assert "Items Group Size" in pageHouseholds.getHouseholdSize().text
        assert "Administrative Level 2" in pageHouseholds.getHouseholdLocation().text
        assert "Residence Status" in pageHouseholds.getHouseholdResidenceStatus().text
        assert "Total Cash Received" in pageHouseholds.getHouseholdTotalCashReceived().text
        assert "Registration Date" in pageHouseholds.getHouseholdRegistrationDate().text

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_smoke_page_households_details(
        self,
        create_programs: None,
        add_household: Household,
        pageHouseholds: Households,
        pageHouseholdsDetails: HouseholdsDetails,
    ) -> None:
        pageHouseholds.selectGlobalProgramFilter("Test Programm")
        pageHouseholds.getNavProgrammePopulation().click()
        pageHouseholds.getNavHouseholds().click()
        pageHouseholds.getHouseholdsRowByNumber(0).click()
        assert "7" in pageHouseholdsDetails.getLabelHouseholdSize().text
        assert "Displaced | Refugee / Asylum Seeker" in pageHouseholdsDetails.getLabelResidenceStatus().text
        assert "Agata Kowalska" in pageHouseholdsDetails.getLabelHeadOfHousehold().text
        assert "Afghanistan" in pageHouseholdsDetails.getLabelCountry().text
        assert "Afghanistan" in pageHouseholdsDetails.getLabelCountryOfOrigin().text
        assert "938 Luna Cliffs Apt. 551 Jameschester, SC 24934" in pageHouseholdsDetails.getLabelAddress().text
        assert "Small One" in pageHouseholdsDetails.getLabelVillage().text
        assert "-" in pageHouseholdsDetails.getLabelZipCode().text
        assert "-" in pageHouseholdsDetails.getLabelAdministrativeLevel1().text
        assert "-" in pageHouseholdsDetails.getLabelAdministrativeLevel2().text
        assert "-" in pageHouseholdsDetails.getLabelAdministrativeLevel3().text
        assert "-" in pageHouseholdsDetails.getLabelAdministrativeLevel4().text
        assert "-" in pageHouseholdsDetails.getLabelGeolocation().text
        assert "-" in pageHouseholdsDetails.getLabelUnhcrCaseId().text
        assert "-" in pageHouseholdsDetails.getLabelLengthOfTimeSinceArrival().text
        assert "-" in pageHouseholdsDetails.getLabelNumberOfTimesDisplaced().text
        assert "-" in pageHouseholdsDetails.getLabelLinkedGrievances().text
        assert "USD 0.00" in pageHouseholdsDetails.getLabelCashReceived().text
        assert "USD 0.00" in pageHouseholdsDetails.getLabelTotalCashReceived().text
        assert "Items Group Members" in pageHouseholdsDetails.getTableTitle().text
        assert "Item ID" in pageHouseholdsDetails.getTableLabel().text
        assert "ACTIVE" in pageHouseholdsDetails.getStatusContainer().text
        assert "No results" in pageHouseholdsDetails.getTableRow().text
        assert add_household.registration_data_import.data_source in pageHouseholdsDetails.getLabelSource().text
        assert add_household.registration_data_import.name in pageHouseholdsDetails.getLabelImportName().text

        assert (
            add_household.last_registration_date.strftime("%-d %b %Y")
            in pageHouseholdsDetails.getLabelRegistrationDate().text
        )
        assert add_household.registration_data_import.imported_by.email in pageHouseholdsDetails.getLabelUserName().text
