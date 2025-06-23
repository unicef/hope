import pytest
from freezegun import freeze_time

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory, create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.fixtures import (
    create_household_with_individual_with_collectors,
)
from hct_mis_api.apps.household.models import FEMALE, MARRIED, Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import BeneficiaryGroup, Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from tests.selenium.page_object.programme_population.individuals import Individuals
from tests.selenium.page_object.programme_population.individuals_details import (
    IndividualsDetails,
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
        imported_by=User.objects.first(), business_area=BusinessArea.objects.first()
    )
    household, individuals = create_household_with_individual_with_collectors(
        {
            "registration_data_import": registration_data_import,
            "admin_area": Area.objects.order_by("?").first(),
            "program": Program.objects.filter(name="Test Programm").first(),
        },
        {
            "registration_data_import": registration_data_import,
            "full_name": "Alicja Kowalska",
            "middle_name": "",
            "given_name": "Alicja",
            "family_name": "Kowalska",
            "sex": FEMALE,
            "birth_date": "1941-08-26",
            "marital_status": MARRIED,
            "pregnant": True,
            "email": "fake111test@email.com",
            "phone_no": "0048503123555",
        },
    )

    household.unicef_id = "HH-00-0000.1380"
    household.save()
    yield household


@pytest.mark.usefixtures("login")
class TestSmokeIndividuals:
    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_smoke_page_individuals(
        self, create_programs: None, add_household: Household, pageIndividuals: Individuals
    ) -> None:
        pageIndividuals.selectGlobalProgramFilter("Test Programm")
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        assert "Items" in pageIndividuals.getTableTitle().text
        assert "Item ID" in pageIndividuals.getIndividualId().text
        assert "Item" in pageIndividuals.getIndividualName().text
        assert "Items Group ID" in pageIndividuals.getHouseholdId().text
        assert "Relationship to Head of Items Group" in pageIndividuals.getRelationship().text
        assert "Age" in pageIndividuals.getIndividualAge().text
        assert "Gender" in pageIndividuals.getIndividualSex().text
        assert "Administrative Level 2" in pageIndividuals.getIndividualLocation().text
        assert len(add_household.active_individuals) == len(pageIndividuals.getIndividualTableRow())

    @freeze_time("2024-08-26")
    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_smoke_page_individuals_details(
        self,
        create_programs: None,
        add_household: Household,
        pageIndividuals: Individuals,
        pageIndividualsDetails: IndividualsDetails,
    ) -> None:
        pageIndividuals.selectGlobalProgramFilter("Test Programm")
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        pageIndividuals.getIndividualTableRow()[0].click()
        assert "Alicja Kowalska" in pageIndividualsDetails.getLabelFullName().text
        assert "Alicja" in pageIndividualsDetails.getLabelGivenName().text
        assert "-" in pageIndividualsDetails.getLabelMiddleName().text
        assert "Kowalska" in pageIndividualsDetails.getLabelFamilyName().text
        assert "Female" in pageIndividualsDetails.getLabelGender().text
        assert "83" in pageIndividualsDetails.getLabelAge().text
        assert "26 Aug 1941" in pageIndividualsDetails.getLabelDateOfBirth().text
        assert "No" in pageIndividualsDetails.getLabelEstimatedDateOfBirth().text
        assert "Married" in pageIndividualsDetails.getLabelMaritalStatus().text
        assert "Not provided" in pageIndividualsDetails.getLabelWorkStatus().text
        assert "Yes" in pageIndividualsDetails.getLabelPregnant().text
        assert "-" in pageIndividualsDetails.getLabelHouseholdId().text
        assert "Primary collector" in pageIndividualsDetails.getLabelRole().text
        assert "Head of household (self)" in pageIndividualsDetails.getLabelRelationshipToHoh().text
        assert "-" in pageIndividualsDetails.getLabelPreferredLanguage().text
        assert "HH-00-0000.1380 -Primary collector" in pageIndividualsDetails.getLabelLinkedHouseholds().text
        assert "None" in pageIndividualsDetails.getLabelObservedDisabilities().text
        assert "None" in pageIndividualsDetails.getLabelSeeingDisabilitySeverity().text
        assert "None" in pageIndividualsDetails.getLabelHearingDisabilitySeverity().text
        assert "None" in pageIndividualsDetails.getLabelPhysicalDisabilitySeverity().text
        assert "None" in pageIndividualsDetails.getLabelRememberingOrConcentratingDisabilitySeverity().text
        assert "None" in pageIndividualsDetails.getLabelCommunicatingDisabilitySeverity().text
        assert "Not Disabled" in pageIndividualsDetails.getLabelDisability().text
        assert "fake111test@email.com" in pageIndividualsDetails.getLabelEmail().text
        assert "Invalid Phone Number" in pageIndividualsDetails.getLabelPhoneNumber().text
        assert "-" in pageIndividualsDetails.getLabelAlternativePhoneNumber().text
        assert "-" in pageIndividualsDetails.getLabelDateOfLastScreeningAgainstSanctionsList().text

    @pytest.mark.skip(reason="ToDo")
    def test_check_data_after_grievance_ticket_processed(self) -> None:
        pass
