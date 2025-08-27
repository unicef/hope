import pytest
from e2e.page_object.programme_population.individuals import Individuals
from e2e.page_object.programme_population.individuals_details import IndividualsDetails
from extras.test_utils.factories.core import (
    DataCollectingTypeFactory,
    create_afghanistan,
)
from extras.test_utils.factories.household import (
    create_household_with_individual_with_collectors,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from freezegun import freeze_time

from hope.apps.account.models import User
from hope.apps.core.models import BusinessArea, DataCollectingType
from hope.apps.geo.models import Area
from hope.apps.household.models import FEMALE, MARRIED, Household
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
        imported_by=User.objects.first(), business_area=BusinessArea.objects.first()
    )
    household, individuals = create_household_with_individual_with_collectors(
        {
            "registration_data_import": registration_data_import,
            "admin2": Area.objects.order_by("?").first(),
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
    return household


@pytest.mark.usefixtures("login")
class TestSmokeIndividuals:
    def test_smoke_page_individuals(
        self,
        create_programs: None,
        add_household: Household,
        page_individuals: Individuals,
    ) -> None:
        page_individuals.select_global_program_filter("Test Programm")
        page_individuals.get_nav_programme_population().click()
        page_individuals.get_nav_individuals().click()
        assert "Items" in page_individuals.get_table_title().text
        assert "Item ID" in page_individuals.get_individual_id().text
        assert "Item" in page_individuals.get_individual_name().text
        assert "Items Group ID" in page_individuals.get_household_id().text
        assert "Relationship to Head of Items Group" in page_individuals.get_relationship().text
        assert "Age" in page_individuals.get_individual_age().text
        assert "Gender" in page_individuals.get_individual_sex().text
        assert "Administrative Level 2" in page_individuals.get_individual_location().text
        assert len(add_household.active_individuals) == len(page_individuals.get_individual_table_row())

    @freeze_time("2024-08-26")
    def test_smoke_page_individuals_details(
        self,
        create_programs: None,
        add_household: Household,
        page_individuals: Individuals,
        page_individuals_details: IndividualsDetails,
    ) -> None:
        page_individuals.select_global_program_filter("Test Programm")
        page_individuals.get_nav_programme_population().click()
        page_individuals.get_nav_individuals().click()
        page_individuals.get_individual_table_row()[0].click()
        assert "Alicja Kowalska" in page_individuals_details.get_label_full_name().text
        assert "Alicja" in page_individuals_details.get_label_given_name().text
        assert "-" in page_individuals_details.get_label_middle_name().text
        assert "Kowalska" in page_individuals_details.get_label_family_name().text
        assert "Female" in page_individuals_details.get_label_gender().text
        assert "83" in page_individuals_details.get_label_age().text
        assert "26 Aug 1941" in page_individuals_details.get_label_date_of_birth().text
        assert "No" in page_individuals_details.get_label_estimated_date_of_birth().text
        assert "Married" in page_individuals_details.get_label_marital_status().text
        assert "Not provided" in page_individuals_details.get_label_work_status().text
        assert "Yes" in page_individuals_details.get_label_pregnant().text
        assert "-" in page_individuals_details.get_label_household_id().text
        assert "Primary collector" in page_individuals_details.get_label_role().text
        assert "Head of household (self)" in page_individuals_details.get_label_relationship_to_hoh().text
        assert "-" in page_individuals_details.get_label_preferred_language().text
        assert "HH-00-0000.1380 -Primary collector" in page_individuals_details.get_label_linked_households().text
        assert "None" in page_individuals_details.get_label_observed_disabilities().text
        assert "None" in page_individuals_details.get_label_seeing_disability_severity().text
        assert "None" in page_individuals_details.get_label_hearing_disability_severity().text
        assert "None" in page_individuals_details.get_label_physical_disability_severity().text
        assert "None" in page_individuals_details.get_label_remembering_or_concentrating_disability_severity().text
        assert "None" in page_individuals_details.get_label_communicating_disability_severity().text
        assert "Not Disabled" in page_individuals_details.get_label_disability().text
        assert "fake111test@email.com" in page_individuals_details.get_label_email().text
        assert "Invalid Phone Number" in page_individuals_details.get_label_phone_number().text
        assert "-" in page_individuals_details.get_label_alternative_phone_number().text
        assert "-" in page_individuals_details.get_label_date_of_last_screening_against_sanctions_list().text

    @pytest.mark.skip(reason="ToDo")
    def test_check_data_after_grievance_ticket_processed(self) -> None:
        pass
