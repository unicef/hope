from datetime import datetime

from django.conf import settings
from django.core.management import call_command
from django.db import transaction

import pytest
from dateutil.relativedelta import relativedelta
from page_object.targeting.targeting import Targeting
from page_object.targeting.targeting_create import TargetingCreate
from page_object.targeting.targeting_details import TargetingDetails
from selenium.webdriver import ActionChains, Keys

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import HEARING, HOST, REFUGEE, SEEING, Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def sw_program() -> Program:
    return get_program_with_dct_type_and_name(
        "SW Program", dct_type=DataCollectingType.Type.SOCIAL, status=Program.ACTIVE
    )


@pytest.fixture
def non_sw_program() -> Program:
    return get_program_with_dct_type_and_name(
        "Non SW Program", dct_type=DataCollectingType.Type.STANDARD, status=Program.ACTIVE
    )


@pytest.fixture
def household_with_disability() -> Household:
    program = Program.objects.first()
    with transaction.atomic():
        household, individuals = create_household_and_individuals(
            household_data={"business_area": program.business_area, "program": program, "residence_status": HOST},
            individuals_data=[
                {"business_area": program.business_area, "observed_disability": [SEEING, HEARING]},
            ],
        )
        return household


@pytest.fixture
def household_without_disabilities() -> Household:
    program = Program.objects.first()
    with transaction.atomic():
        household, individuals = create_household_and_individuals(
            household_data={"business_area": program.business_area, "program": program, "residence_status": HOST},
            individuals_data=[
                {"business_area": program.business_area, "observed_disability": []},
            ],
        )
        return household


@pytest.fixture
def household_refugee() -> Household:
    program = Program.objects.first()
    with transaction.atomic():
        household, individuals = create_household_and_individuals(
            household_data={"business_area": program.business_area, "program": program, "residence_status": REFUGEE},
            individuals_data=[
                {"business_area": program.business_area, "observed_disability": []},
            ],
        )
        return household


def get_program_with_dct_type_and_name(
    name: str, dct_type: str = DataCollectingType.Type.STANDARD, status: str = Program.ACTIVE
) -> Program:
    BusinessArea.objects.filter(slug="afghanistan").update(is_payment_plan_applicable=True)
    dct = DataCollectingTypeFactory(type=dct_type)
    program = ProgramFactory(
        name=name,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
    )
    return program


@pytest.fixture
def create_programs() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    return


@pytest.fixture
def add_targeting() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/documenttype.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data-cypress.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/data-cypress.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/targeting/fixtures/data-cypress.json")


@pytest.mark.usefixtures("login")
class TestSmokeTargeting:
    def test_smoke_targeting_page(self, create_programs: None, add_targeting: None, pageTargeting: Targeting) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        assert "Targeting" in pageTargeting.getTitlePage().text
        assert "CREATE NEW" in pageTargeting.getButtonCreateNew().text
        expected_column_names = ["Name", "Status", "Num. of Households", "Date Created", "Last Edited", "Created by"]
        assert expected_column_names == [name.text for name in pageTargeting.getTabColumnLabel()]
        assert 2 == len(pageTargeting.getTargetPopulationsRows())
        pageTargeting.getButtonCreateNew().click()
        assert "Use Filters" in pageTargeting.getCreateUseFilters().text
        assert "Use IDs" in pageTargeting.getCreateUseIDs().text

    def test_smoke_targeting_create_use_filters(
        self, create_programs: None, add_targeting: None, pageTargeting: Targeting, pageTargetingCreate: TargetingCreate
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getCreateUseFilters().click()
        assert "New Target Population" in pageTargetingCreate.getPageHeaderTitle().text
        assert "SAVE" in pageTargetingCreate.getButtonTargetPopulationCreate().text
        pageTargetingCreate.getInputName()
        pageTargetingCreate.getDivTargetPopulationAddCriteria().click()
        pageTargetingCreate.getButtonHouseholdRule().click()
        pageTargetingCreate.getButtonIndividualRule().click()
        pageTargetingCreate.getAutocompleteTargetCriteriaOption().click()

    def test_smoke_targeting_create_use_ids(
        self, create_programs: None, add_targeting: None, pageTargeting: Targeting, pageTargetingCreate: TargetingCreate
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getCreateUseIDs().click()
        assert "New Target Population" in pageTargetingCreate.getPageHeaderTitle().text
        assert "SAVE" in pageTargetingCreate.getButtonTargetPopulationCreate().text
        pageTargetingCreate.getInputName()
        pageTargetingCreate.getInputIncludedHouseholdIds()
        pageTargetingCreate.getInputHouseholdids()
        pageTargetingCreate.getInputIncludedIndividualIds()
        pageTargetingCreate.getInputIndividualids()

    def test_smoke_targeting_details_page(
        self,
        create_programs: None,
        add_targeting: None,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.chooseTargetPopulations(0).click()
        assert "Copy TP" in pageTargetingDetails.getPageHeaderTitle().text
        pageTargetingDetails.getButtonTargetPopulationDuplicate()
        pageTargetingDetails.getButtonDelete()
        assert "EDIT" in pageTargetingDetails.getButtonEdit().text
        assert "REBUILD" in pageTargetingDetails.getButtonRebuild().text
        assert "LOCK" in pageTargetingDetails.getButtonTargetPopulationLock().text
        assert "Details" in pageTargetingDetails.getDetailsTitle().text
        assert "OPEN" in pageTargetingDetails.getLabelStatus().text
        assert "OPEN" in pageTargetingDetails.getTargetPopulationStatus().text
        assert "CREATED BY" in pageTargetingDetails.getLabelizedFieldContainerCreatedBy().text
        pageTargetingDetails.getLabelCreatedBy()
        assert "PROGRAMME POPULATION CLOSE DATE" in pageTargetingDetails.getLabelizedFieldContainerCloseDate().text
        assert "PROGRAMME" in pageTargetingDetails.getLabelizedFieldContainerProgramName().text
        assert "Test Programm" in pageTargetingDetails.getLabelProgramme().text
        assert "SEND BY" in pageTargetingDetails.getLabelizedFieldContainerSendBy().text
        assert "-" in pageTargetingDetails.getLabelSendBy().text
        assert "-" in pageTargetingDetails.getLabelSendDate().text
        assert "-" in pageTargetingDetails.getCriteriaContainer().text
        assert "0" in pageTargetingDetails.getLabelFemaleChildren().text
        assert "0" in pageTargetingDetails.getLabelMaleChildren().text
        assert "0" in pageTargetingDetails.getLabelMaleAdults().text
        assert "2" in pageTargetingDetails.getLabelTotalNumberOfHouseholds().text
        assert "8" in pageTargetingDetails.getLabelTargetedIndividuals().text
        assert "Households" in pageTargetingDetails.getTableTitle().text
        expected_menu_items = [
            "ID",
            "Head of Household",
            "Household Size",
            "Administrative Level 2",
            "Score",
        ]
        assert expected_menu_items == [i.text for i in pageTargetingDetails.getTableLabel()]


@pytest.mark.usefixtures("login")
class TestCreateTargeting:
    def test_create_targeting_for_people(
        self,
        sw_program: Program,
        household_with_disability: Household,
        household_without_disabilities: Household,
        pageTargeting: Targeting,
        pageTargetingCreate: TargetingCreate,
        pageTargetingDetails: TargetingDetails,
    ) -> None:
        pageTargeting.navigate_to_page("afghanistan", sw_program.id)
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getButtonCreateNewByFilters().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getAddCriteriaButton().click()
        assert pageTargetingCreate.getAddPeopleRuleButton().text.upper() == "ADD PEOPLE RULE"
        pageTargetingCreate.getAddPeopleRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys("Does the Social Worker have disability?")
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ARROW_DOWN)
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ENTER)
        pageTargetingCreate.getTargetingCriteriaValue().click()
        pageTargetingCreate.select_multiple_option_by_name(HEARING, SEEING)
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        disability_expected_criteria_text = "Does the Social Worker have disability?: Difficulty hearing (even if using a hearing aid), Difficulty seeing (even if wearing glasses)"
        assert pageTargetingCreate.getCriteriaContainer().text == disability_expected_criteria_text
        targeting_name = "Test targeting people"
        pageTargetingCreate.getFieldName().send_keys(targeting_name)
        pageTargetingCreate.getTargetPopulationSaveButton().click()
        pageTargetingDetails.getLockButton()
        assert pageTargetingDetails.getTitlePage().text == targeting_name
        assert pageTargetingDetails.getCriteriaContainer().text == disability_expected_criteria_text
        assert Household.objects.count() == 2
        assert (
            pageTargetingDetails.getHouseholdTableCell(1, 1).text
            == household_with_disability.individuals.first().unicef_id
        )
        assert len(pageTargetingDetails.getPeopleTableRows()) == 1

    def test_create_targeting_for_normal_program(
        self,
        non_sw_program: Program,
        household_with_disability: Household,
        household_without_disabilities: Household,
        household_refugee: Household,
        pageTargeting: Targeting,
        pageTargetingCreate: TargetingCreate,
        pageTargetingDetails: TargetingDetails,
    ) -> None:
        pageTargeting.navigate_to_page("afghanistan", non_sw_program.id)
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getButtonCreateNewByFilters().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getAddCriteriaButton().click()
        assert pageTargetingCreate.getAddPeopleRuleButton().text.upper() == "ADD HOUSEHOLD RULE"
        pageTargetingCreate.getAddHouseholdRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys("Residence Status")
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ARROW_DOWN)
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ENTER)
        pageTargetingCreate.getTargetingCriteriaValue().click()
        pageTargetingCreate.select_option_by_name(REFUGEE)
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        disability_expected_criteria_text = "Residence status: Displaced | Refugee / Asylum Seeker"
        assert pageTargetingCreate.getCriteriaContainer().text == disability_expected_criteria_text
        targeting_name = "Test targeting people"
        pageTargetingCreate.getFieldName().send_keys(targeting_name)
        pageTargetingCreate.getTargetPopulationSaveButton().click()
        pageTargetingDetails.getLockButton()
        assert pageTargetingDetails.getTitlePage().text == targeting_name
        assert pageTargetingDetails.getCriteriaContainer().text == disability_expected_criteria_text
        assert Household.objects.count() == 3
        assert Program.objects.count() == 1
        assert pageTargetingDetails.getHouseholdTableCell(1, 1).text == household_refugee.unicef_id
        actions = ActionChains(pageTargetingDetails.driver)
        actions.move_to_element(pageTargetingDetails.getHouseholdTableCell(1, 1)).perform()  # type: ignore
        assert len(pageTargetingDetails.getHouseholdTableRows()) == 1

@pytest.mark.usefixtures("login")
class TestTargeting:
    def test_smoke_targeting_page(self, create_programs: None, add_targeting: None, pageTargeting: Targeting) -> None:
        pass