from datetime import datetime
from typing import Callable

import factory
import pytest
from dateutil.relativedelta import relativedelta
from e2e.page_object.filters import Filters
from e2e.page_object.targeting.targeting import Targeting
from e2e.page_object.targeting.targeting_create import TargetingCreate
from e2e.page_object.targeting.targeting_details import TargetingDetails
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import (
    DataCollectingTypeFactory,
    create_afghanistan,
)
from extras.test_utils.factories.household import (
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    create_household_with_individual_with_collectors,
)
from extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from extras.test_utils.factories.steficon import RuleCommitFactory, RuleFactory
from extras.test_utils.factories.targeting import TargetingCriteriaRuleFactory
from pytz import utc
from selenium.common import NoSuchElementException

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.models import (
    BusinessArea,
    DataCollectingType,
    FlexibleAttribute,
    PeriodicFieldData,
)
from hct_mis_api.apps.household.models import (
    HEARING,
    HOST,
    REFUGEE,
    ROLE_PRIMARY,
    SEEING,
    Household,
    Individual,
)
from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    FinancialServiceProvider,
    PaymentPlan,
)
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.periodic_data_update.utils import (
    field_label_to_field_name,
    populate_pdu_with_null_values,
)
from hct_mis_api.apps.program.models import BeneficiaryGroup, Program, ProgramCycle
from hct_mis_api.apps.steficon.models import Rule

pytestmark = pytest.mark.django_db()


@pytest.fixture
def sw_program() -> Program:
    yield get_program_with_dct_type_and_name(
        "Test Programm", dct_type=DataCollectingType.Type.SOCIAL, status=Program.ACTIVE, beneficiary_group_name="People"
    )


@pytest.fixture
def non_sw_program() -> Program:
    yield get_program_with_dct_type_and_name(
        "Test Programm", dct_type=DataCollectingType.Type.STANDARD, status=Program.ACTIVE
    )


@pytest.fixture
def program() -> Program:
    business_area = create_afghanistan()
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    return ProgramFactory(
        name="Test Program",
        status=Program.ACTIVE,
        business_area=business_area,
        cycle__title="Cycle In Programme",
        cycle__start_date=datetime.now() - relativedelta(days=5),
        cycle__end_date=datetime.now() + relativedelta(months=5),
        beneficiary_group=beneficiary_group,
    )


@pytest.fixture
def individual() -> Callable:
    def _individual(program: Program) -> Individual:
        business_area = create_afghanistan()
        rdi = RegistrationDataImportFactory()

        household, individuals = create_household_with_individual_with_collectors(
            household_args={
                "business_area": business_area,
                "program_id": program.pk,
                "registration_data_import": rdi,
            },
            individual_args={
                "business_area": business_area,
                "program_id": program.pk,
                "registration_data_import": rdi,
            },
        )
        individual = individuals[0]
        individual.flex_fields = populate_pdu_with_null_values(program, individual.flex_fields)
        individual.save()
        return individual

    return _individual


@pytest.fixture
def string_attribute(program: Program) -> FlexibleAttribute:
    return create_flexible_attribute(
        label="Test String Attribute",
        subtype=PeriodicFieldData.STRING,
        number_of_rounds=1,
        rounds_names=["Test Round String 1"],
        program=program,
    )


@pytest.fixture
def date_attribute(program: Program) -> FlexibleAttribute:
    return create_flexible_attribute(
        label="Test Date Attribute",
        subtype=PeriodicFieldData.DATE,
        number_of_rounds=1,
        rounds_names=["Test Round Date 1"],
        program=program,
    )


@pytest.fixture
def bool_attribute(program: Program) -> FlexibleAttribute:
    return create_flexible_attribute(
        label="Test Bool Attribute",
        subtype=PeriodicFieldData.BOOL,
        number_of_rounds=2,
        rounds_names=["Test Round Bool 1", "Test Round Bool 2"],
        program=program,
    )


@pytest.fixture
def decimal_attribute(program: Program) -> FlexibleAttribute:
    return create_flexible_attribute(
        label="Test Decimal Attribute",
        subtype=PeriodicFieldData.DECIMAL,
        number_of_rounds=1,
        rounds_names=["Test Round Decimal 1"],
        program=program,
    )


def create_flexible_attribute(
    label: str, subtype: str, number_of_rounds: int, rounds_names: list[str], program: Program
) -> FlexibleAttribute:
    name = field_label_to_field_name(label)
    flexible_attribute = FlexibleAttribute.objects.create(
        label={"English(EN)": label},
        name=name,
        type=FlexibleAttribute.PDU,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        program=program,
    )
    flexible_attribute.pdu_data = PeriodicFieldData.objects.create(
        subtype=subtype, number_of_rounds=number_of_rounds, rounds_names=rounds_names
    )
    flexible_attribute.save()
    return flexible_attribute


def create_custom_household(
    observed_disability: list[str], residence_status: str = HOST, unicef_id: str = "HH-00-0000.0442", size: int = 2
) -> Household:
    program = Program.objects.get(name="Test Programm")
    household, _ = create_household_with_individual_with_collectors(
        household_args={
            "unicef_id": unicef_id,
            "rdi_merge_status": "MERGED",
            "business_area": program.business_area,
            "program": program,
            "residence_status": residence_status,
            "size": size,
        },
        individual_args={
            "rdi_merge_status": "MERGED",
            "business_area": program.business_area,
            "observed_disability": observed_disability,
        },
    )
    return household


@pytest.fixture
def household_with_disability() -> Household:
    yield create_custom_household(observed_disability=[SEEING, HEARING], unicef_id="HH-00-0000.0443", size=1)


@pytest.fixture
def household_without_disabilities() -> Household:
    yield create_custom_household(observed_disability=[], unicef_id="HH-00-0000.0444", size=1)


@pytest.fixture
def household_refugee() -> Household:
    yield create_custom_household(observed_disability=[], residence_status=REFUGEE, unicef_id="HH-00-0000.0445")


def get_program_with_dct_type_and_name(
    name: str,
    dct_type: str = DataCollectingType.Type.STANDARD,
    status: str = Program.ACTIVE,
    beneficiary_group_name: str = "Main Menu",
) -> Program:
    dct = DataCollectingTypeFactory(type=dct_type)
    beneficiary_group = BeneficiaryGroup.objects.filter(name=beneficiary_group_name).first()
    return ProgramFactory(
        name=name,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        cycle__title="First Cycle In Programme",
        cycle__start_date=datetime.now() - relativedelta(days=5),
        cycle__end_date=datetime.now() + relativedelta(months=5),
        beneficiary_group=beneficiary_group,
    )


@pytest.fixture
def create_targeting() -> PaymentPlan:
    test_program = Program.objects.get(name="Test Programm")
    generate_delivery_mechanisms()
    dm_cash = DeliveryMechanism.objects.get(code="cash")
    business_area = BusinessArea.objects.get(slug="afghanistan")

    fsp_1 = FinancialServiceProviderFactory(
        name="FSP_1",
        vision_vendor_number="149-69-3686",
        distribution_limit=10_000,
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
    )
    fsp_1.delivery_mechanisms.set([dm_cash])
    fsp_1.allowed_business_areas.add(business_area)

    pp = PaymentPlanFactory(
        name="Test Target Population",
        status=PaymentPlan.Status.TP_OPEN,
        program_cycle=test_program.cycles.first(),
        build_status=PaymentPlan.BuildStatus.BUILD_STATUS_OK,
        created_by=User.objects.filter(email="test@example.com").first(),
        updated_at=datetime.now(),
        delivery_mechanism=dm_cash,
        financial_service_provider=fsp_1,
    )

    hoh1 = IndividualFactory(household=None)
    hoh2 = IndividualFactory(household=None)
    household_1 = HouseholdFactory(
        program=test_program,
        id="3d7087be-e8f8-478d-9ca2-4ca6d5e96f51",
        unicef_id="HH-17-0000.3340",
        head_of_household=hoh1,
        size=5,
    )
    household_2 = HouseholdFactory(
        program=test_program,
        id="3d7087be-e8f8-478d-9ca2-4ca6d5e96f52",
        unicef_id="HH-17-0000.3341",
        head_of_household=hoh2,
        size=6,
    )
    # HH1 - Female Children: 1; Female Adults: 1; Male Children: 2; Male Adults: 1;
    ind_1 = IndividualFactory(
        household=household_1,
        program=test_program,
        sex="MALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=11, maximum_age=16),
    )
    IndividualFactory(
        household=household_1,
        program=test_program,
        sex="MALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=11, maximum_age=16),
    )
    IndividualFactory(
        household=household_1,
        program=test_program,
        sex="FEMALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=1, maximum_age=10),
    )
    IndividualFactory(
        household=household_1,
        program=test_program,
        sex="FEMALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=20, maximum_age=40),
    )
    IndividualFactory(
        household=household_1,
        program=test_program,
        sex="MALE",
        unicef_id="IND-06-0001.1828",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=20, maximum_age=40),
    )
    # HH2 - Female Children: 4; Female Adults: 1; Male Children: 1; Male Adults: 0;
    ind_2 = IndividualFactory(
        household=household_2,
        program=test_program,
        sex="MALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=1, maximum_age=3),
    )
    IndividualFactory(
        household=household_2,
        program=test_program,
        sex="FEMALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=1, maximum_age=10),
    )
    IndividualFactory(
        household=household_2,
        program=test_program,
        sex="FEMALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=1, maximum_age=10),
    )
    IndividualFactory(
        household=household_2,
        program=test_program,
        sex="FEMALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=1, maximum_age=10),
    )
    IndividualFactory(
        household=household_2,
        program=test_program,
        sex="FEMALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=1, maximum_age=10),
    )
    IndividualFactory(
        household=household_2,
        program=test_program,
        sex="FEMALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=30, maximum_age=45),
    )
    IndividualRoleInHouseholdFactory(individual=ind_1, household=household_1, role=ROLE_PRIMARY)
    IndividualRoleInHouseholdFactory(individual=ind_2, household=household_2, role=ROLE_PRIMARY)
    rule = RuleFactory(
        name="Test Rule",
        type=Rule.TYPE_PAYMENT_PLAN,
        deprecated=False,
        enabled=True,
    )
    rule.allowed_business_areas.add(business_area)
    RuleCommitFactory(rule=rule, version=2)

    fsp_xlsx_template = FinancialServiceProviderXlsxTemplateFactory(name="TestName123")

    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp_1,
        xlsx_template=fsp_xlsx_template,
        delivery_mechanism=dm_cash,
    )
    TargetingCriteriaRuleFactory(
        household_ids=f"{household_1.unicef_id}, {household_2.unicef_id}",
        individual_ids="",
        payment_plan=pp,
    )
    PaymentPlanService.create_payments(pp)
    pp.update_population_count_fields()
    pp.refresh_from_db()
    yield pp


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
        cycle__title="First Cycle In Programme",
    )


@pytest.mark.usefixtures("login")
class TestSmokeTargeting:
    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_smoke_targeting_page(
        self, create_programs: None, create_targeting: PaymentPlan, pageTargeting: Targeting
    ) -> None:
        PaymentPlanFactory(
            program_cycle=ProgramCycle.objects.get(program__name="Test Programm"),
            name="Copy TP",
            status=PaymentPlan.Status.TP_OPEN,
        )
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        assert "Targeting" in pageTargeting.getTitlePage().text
        assert "CREATE NEW" in pageTargeting.getButtonCreateNew().text
        expected_column_names = [
            "Name",
            "Status",
            "Num. of Items Groups",
            "Date Created",
            "Last Edited",
            "Created by",
        ]
        assert expected_column_names == [name.text for name in pageTargeting.getTabColumnLabel()]
        assert 2 == len(pageTargeting.getTargetPopulationsRows())
        pageTargeting.getButtonCreateNew().click()

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_smoke_targeting_create_use_filters(
        self,
        create_programs: None,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        assert "New Target Population" in pageTargetingCreate.getPageHeaderTitle().text
        assert "SAVE" in pageTargetingCreate.getButtonTargetPopulationCreate().text
        pageTargetingCreate.getInputName()
        pageTargetingCreate.getDivTargetPopulationAddCriteria().click()
        pageTargetingCreate.getButtonHouseholdRule().click()
        pageTargetingCreate.getButtonIndividualRule().click()
        pageTargetingCreate.getAutocompleteTargetCriteriaOption().click()

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_smoke_targeting_create_use_ids(
        self,
        create_programs: None,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        assert "New Target Population" in pageTargetingCreate.getPageHeaderTitle().text
        assert "SAVE" in pageTargetingCreate.getButtonTargetPopulationCreate().text
        pageTargetingCreate.getInputName()
        pageTargetingCreate.getDivTargetPopulationAddCriteria().click()
        pageTargetingCreate.getInputIncludedHouseholdIds()
        pageTargetingCreate.getInputHouseholdids()
        pageTargetingCreate.getInputIncludedIndividualIds()
        pageTargetingCreate.getInputIndividualids()

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_smoke_targeting_details_page(
        self,
        create_programs: None,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        pageTargeting.chooseTargetPopulations(0).click()
        assert create_targeting.name in pageTargetingDetails.getPageHeaderTitle().text
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
        # assert "PROGRAMME POPULATION CLOSE DATE" in pageTargetingDetails.getLabelizedFieldContainerCloseDate().text
        assert "PROGRAMME" in pageTargetingDetails.getLabelizedFieldContainerProgramName().text
        assert "Test Programm" in pageTargetingDetails.getLabelProgramme().text
        # assert "SEND BY" in pageTargetingDetails.getLabelizedFieldContainerSendBy().text
        # assert "-" in pageTargetingDetails.getLabelSendBy().text
        # assert "-" in pageTargetingDetails.getLabelSendDate().text
        assert "5" in pageTargetingDetails.getLabelFemaleChildren().text
        assert "3" in pageTargetingDetails.getLabelMaleChildren().text
        assert "2" in pageTargetingDetails.getLabelFemaleAdults().text
        assert "1" in pageTargetingDetails.getLabelMaleAdults().text
        assert "2" in pageTargetingDetails.getLabelTotalNumberOfHouseholds().text
        assert "11" in pageTargetingDetails.getLabelTargetedIndividuals().text
        assert "Items Groups" in pageTargetingDetails.getTableTitle().text
        expected_menu_items = [
            "ID",
            "Head of Items Group",
            "Items Group Size",
            "Administrative Level 2",
            "Score",
        ]
        assert expected_menu_items == [i.text for i in pageTargetingDetails.getTableLabel()]


@pytest.mark.night
@pytest.mark.usefixtures("login")
class TestCreateTargeting:
    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_create_targeting_for_people(
        self,
        sw_program: Program,
        household_with_disability: Household,
        household_without_disabilities: Household,
        pageTargeting: Targeting,
        pageTargetingCreate: TargetingCreate,
        pageTargetingDetails: TargetingDetails,
    ) -> None:
        pageTargeting.navigate_to_page("afghanistan", sw_program.slug)
        pageTargeting.getButtonCreateNew().click()

        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getFiltersProgramCycleAutocomplete().click()
        pageTargetingCreate.select_listbox_element("First Cycle In Programme")
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
        pageTargetingCreate.getNoValidationFspAccept().click()
        disability_expected_criteria_text = "Does the Social Worker have disability?: Difficulty hearing (even if using a hearing aid), Difficulty seeing (even if wearing glasses)"
        assert pageTargetingCreate.getCriteriaContainer().text == disability_expected_criteria_text
        targeting_name = "Test targeting people"
        pageTargetingCreate.getFieldName().send_keys(targeting_name)
        pageTargetingCreate.getTargetPopulationSaveButton().click()
        pageTargetingDetails.getLockButton()
        assert pageTargetingDetails.getTitlePage().text.split("\n")[0].strip() == targeting_name
        assert pageTargetingDetails.getCriteriaContainer().text == disability_expected_criteria_text
        assert Household.objects.count() == 2
        assert PaymentPlan.objects.get(name=targeting_name).payment_items.count() == 1
        individual = household_with_disability.individuals.first()
        pageTargetingDetails.wait_for_text(individual.unicef_id, pageTargetingDetails.household_table_cell.format(1, 1))
        assert len(pageTargetingDetails.getPeopleTableRows()) == 1
        assert pageTargetingDetails.getHouseholdTableCell(1, 1).text == individual.unicef_id

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
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
        pageTargeting.navigate_to_page("afghanistan", non_sw_program.slug)
        pageTargeting.getButtonCreateNew().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getFiltersProgramCycleAutocomplete().click()
        pageTargetingCreate.select_listbox_element("First Cycle In Programme")
        pageTargetingCreate.getAddCriteriaButton().click()
        assert pageTargetingCreate.getAddPeopleRuleButton().text.upper() == "ADD ITEMS GROUP RULE"
        pageTargetingCreate.getAddHouseholdRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.select_listbox_element("Residence status")
        pageTargetingCreate.getTargetingCriteriaValue().click()
        pageTargetingCreate.getSelectRefugee().click()
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        pageTargetingCreate.getNoValidationFspAccept().click()
        disability_expected_criteria_text = "Residence status: Displaced | Refugee / Asylum Seeker"
        assert pageTargetingCreate.getCriteriaContainer().text == disability_expected_criteria_text
        targeting_name = "Test targeting people"
        pageTargetingCreate.getFieldName().send_keys(targeting_name)
        pageTargetingCreate.getTargetPopulationSaveButton().click()
        pageTargetingDetails.getLockButton()
        assert pageTargetingDetails.getTitlePage().text.split("\n")[0].strip() == targeting_name
        assert pageTargetingDetails.getCriteriaContainer().text == disability_expected_criteria_text
        assert Household.objects.count() == 3
        assert PaymentPlan.objects.get(name=targeting_name).payment_items.count() == 1
        pageTargetingDetails.wait_for_text(
            household_refugee.unicef_id, pageTargetingDetails.household_table_cell.format(1, 1)
        )
        assert len(pageTargetingDetails.getHouseholdTableRows()) == 1
        assert pageTargetingDetails.getHouseholdTableCell(1, 1).text == household_refugee.unicef_id
        actions = ActionChains(pageTargetingDetails.driver)
        actions.move_to_element(pageTargetingDetails.getHouseholdTableCell(1, 1)).perform()

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_create_targeting_with_pdu_string_criteria(
        self,
        program: Program,
        pageTargeting: Targeting,
        pageTargetingCreate: TargetingCreate,
        pageTargetingDetails: TargetingDetails,
        individual: Callable,
        string_attribute: FlexibleAttribute,
    ) -> None:
        individual1 = individual(program)
        individual1.flex_fields[string_attribute.name]["1"]["value"] = "Text"
        individual1.save()
        individual2 = individual(program)
        individual2.flex_fields[string_attribute.name]["1"]["value"] = "Test"
        individual2.save()
        individual(program)
        pageTargeting.navigate_to_page("afghanistan", program.slug)
        pageTargeting.getButtonCreateNew().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getFiltersProgramCycleAutocomplete().click()
        pageTargetingCreate.select_listbox_element("Cycle In Programme")
        pageTargetingCreate.getAddCriteriaButton().click()
        pageTargetingCreate.getAddIndividualRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys("Test String Attribute")
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ARROW_DOWN)
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ENTER)
        pageTargetingCreate.getSelectIndividualsiFltersBlocksRoundNumber().click()
        pageTargetingCreate.getSelectRoundOption(1).click()
        pageTargetingCreate.getInputIndividualsFiltersBlocksValue().send_keys("Text")
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        pageTargetingCreate.getNoValidationFspAccept().click()
        expected_criteria_text = "Test String Attribute: Text\nRound 1 (Test Round String 1)"
        assert pageTargetingCreate.getCriteriaContainer().text == expected_criteria_text
        targeting_name = "Test Targeting PDU str"
        pageTargetingCreate.getFieldName().send_keys(targeting_name)
        pageTargetingCreate.getTargetPopulationSaveButton().click()
        pageTargetingDetails.getLockButton()
        assert pageTargetingDetails.getTitlePage().text.split("\n")[0].strip() == targeting_name
        assert pageTargetingDetails.getCriteriaContainer().text == expected_criteria_text
        assert Household.objects.count() == 3
        assert PaymentPlan.objects.get(name=targeting_name).payment_items.count() == 1
        pageTargetingDetails.wait_for_text(
            individual1.household.unicef_id, pageTargetingDetails.household_table_cell.format(1, 1)
        )
        assert pageTargetingCreate.getTotalNumberOfHouseholdsCount().text == "1"
        assert len(pageTargetingDetails.getHouseholdTableRows()) == 1
        assert pageTargetingDetails.getHouseholdTableCell(1, 1).text == individual1.household.unicef_id

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_create_targeting_with_pdu_bool_criteria(
        self,
        program: Program,
        pageTargeting: Targeting,
        pageTargetingCreate: TargetingCreate,
        pageTargetingDetails: TargetingDetails,
        individual: Callable,
        bool_attribute: FlexibleAttribute,
    ) -> None:
        individual1 = individual(program)
        individual1.flex_fields[bool_attribute.name]["2"]["value"] = True
        individual1.save()
        individual2 = individual(program)
        individual2.flex_fields[bool_attribute.name]["2"]["value"] = False
        individual2.save()
        individual(program)
        pageTargeting.navigate_to_page("afghanistan", program.slug)
        pageTargeting.getButtonCreateNew().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getFiltersProgramCycleAutocomplete().click()
        pageTargetingCreate.select_listbox_element("Cycle In Programme")
        pageTargetingCreate.getAddCriteriaButton().click()
        pageTargetingCreate.getAddIndividualRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys("Test Bool Attribute")
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ARROW_DOWN)
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ENTER)
        pageTargetingCreate.getSelectIndividualsiFltersBlocksRoundNumber().click()
        pageTargetingCreate.getSelectRoundOption(2).click()
        pageTargetingCreate.getSelectIndividualsFiltersBlocksValue().click()
        pageTargetingCreate.select_option_by_name("Yes")
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        pageTargetingCreate.getNoValidationFspAccept().click()
        bool_yes_expected_criteria_text = "Test Bool Attribute: Yes\nRound 2 (Test Round Bool 2)"
        assert pageTargetingCreate.getCriteriaContainer().text == bool_yes_expected_criteria_text

        targeting_name = "Test Targeting PDU bool"
        pageTargetingCreate.getFieldName().send_keys(targeting_name)
        pageTargetingCreate.getTargetPopulationSaveButton().click()

        pageTargetingDetails.getLockButton()

        assert pageTargetingDetails.getTitlePage().text.split("\n")[0].strip() == targeting_name
        assert pageTargetingDetails.getCriteriaContainer().text == bool_yes_expected_criteria_text
        assert Household.objects.count() == 3
        pageTargetingDetails.wait_for_text(
            individual1.household.unicef_id, pageTargetingDetails.household_table_cell.format(1, 1)
        )
        assert pageTargetingDetails.getHouseholdTableCell(1, 1).text == individual1.household.unicef_id
        assert pageTargetingCreate.getTotalNumberOfHouseholdsCount().text == "1"
        assert len(pageTargetingDetails.getHouseholdTableRows()) == 1

        # edit to False
        pageTargetingDetails.getButtonEdit().click()
        pageTargetingDetails.getButtonIconEdit().click()
        pageTargetingCreate.getSelectIndividualsFiltersBlocksValue().click()
        pageTargetingCreate.select_option_by_name("No")
        bool_no_expected_criteria_text = "Test Bool Attribute: No\nRound 2 (Test Round Bool 2)"

        pageTargetingCreate.get_elements(pageTargetingCreate.targetingCriteriaAddDialogSaveButton)[1].click()

        assert pageTargetingCreate.getCriteriaContainer().text == bool_no_expected_criteria_text
        pageTargetingCreate.getButtonSave().click()
        pageTargetingDetails.getLockButton()

        pageTargetingDetails.wait_for_text(
            individual2.household.unicef_id, pageTargetingDetails.household_table_cell.format(1, 1)
        )
        assert pageTargetingDetails.getCriteriaContainer().text == bool_no_expected_criteria_text
        assert pageTargetingDetails.getHouseholdTableCell(1, 1).text == individual2.household.unicef_id
        assert pageTargetingCreate.getTotalNumberOfHouseholdsCount().text == "1"
        assert len(pageTargetingDetails.getHouseholdTableRows()) == 1

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_create_targeting_with_pdu_decimal_criteria(
        self,
        program: Program,
        pageTargeting: Targeting,
        pageTargetingCreate: TargetingCreate,
        pageTargetingDetails: TargetingDetails,
        individual: Callable,
        decimal_attribute: FlexibleAttribute,
    ) -> None:
        individual1 = individual(program)
        individual1.flex_fields[decimal_attribute.name]["1"]["value"] = 2.5
        individual1.save()
        individual2 = individual(program)
        individual2.flex_fields[decimal_attribute.name]["1"]["value"] = 7.0
        individual2.save()
        individual(program)
        pageTargeting.navigate_to_page("afghanistan", program.slug)
        pageTargeting.getButtonCreateNew().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getFiltersProgramCycleAutocomplete().click()
        pageTargetingCreate.select_listbox_element("Cycle In Programme")
        pageTargetingCreate.getAddCriteriaButton().click()
        pageTargetingCreate.getAddIndividualRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys("Test Decimal Attribute")
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ARROW_DOWN)
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ENTER)
        pageTargetingCreate.getSelectIndividualsiFltersBlocksRoundNumber().click()
        pageTargetingCreate.getSelectRoundOption(1).click()
        pageTargetingCreate.getInputIndividualsFiltersBlocksValueFrom().send_keys("2")
        pageTargetingCreate.getInputIndividualsFiltersBlocksValueTo().send_keys("4")
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        pageTargetingCreate.getNoValidationFspAccept().click()
        expected_criteria_text = "Test Decimal Attribute: 2 - 5\nRound 1 (Test Round Decimal 1)"
        assert pageTargetingCreate.getCriteriaContainer().text == expected_criteria_text
        targeting_name = "Test Targeting PDU decimal"
        pageTargetingCreate.getFieldName().send_keys(targeting_name)
        pageTargetingCreate.getTargetPopulationSaveButton().click()
        pageTargetingCreate.getNoValidationFspAccept().click()
        pageTargetingDetails.getLockButton()
        assert pageTargetingDetails.getTitlePage().text.split("\n")[0].strip() == targeting_name
        assert pageTargetingDetails.getCriteriaContainer().text == expected_criteria_text
        assert Household.objects.count() == 3
        assert PaymentPlan.objects.get(name=targeting_name).payment_items.count() == 1
        pageTargetingDetails.wait_for_text(
            individual1.household.unicef_id, pageTargetingDetails.household_table_cell.format(1, 1)
        )
        assert pageTargetingCreate.getTotalNumberOfHouseholdsCount().text == "1"
        assert len(pageTargetingDetails.getHouseholdTableRows()) == 1
        assert pageTargetingDetails.getHouseholdTableCell(1, 1).text == individual1.household.unicef_id

        # edit range
        pageTargetingDetails.getButtonEdit().click()
        pageTargetingDetails.getButtonIconEdit().click()
        pageTargetingCreate.getInputIndividualsFiltersBlocksValueTo().send_keys(Keys.BACKSPACE)
        pageTargetingCreate.getInputIndividualsFiltersBlocksValueTo().send_keys("9")
        bool_no_expected_criteria_text = "Test Decimal Attribute: 2 - 9\nRound 1 (Test Round Decimal 1)"

        pageTargetingCreate.get_elements(pageTargetingCreate.targetingCriteriaAddDialogSaveButton)[1].click()

        assert pageTargetingCreate.getCriteriaContainer().text == bool_no_expected_criteria_text
        pageTargetingCreate.getButtonSave().click()
        pageTargetingDetails.getLockButton()
        pageTargetingDetails.disappearStatusContainer()
        pageTargetingDetails.wait_for_text(
            individual1.household.unicef_id, pageTargetingDetails.household_table_cell.format(1, 1)
        )
        assert pageTargetingDetails.getCriteriaContainer().text == bool_no_expected_criteria_text
        assert pageTargetingCreate.getTotalNumberOfHouseholdsCount().text == "2"
        assert len(pageTargetingDetails.getHouseholdTableRows()) == 2
        assert pageTargetingDetails.getHouseholdTableCell(1, 1).text in [
            individual1.household.unicef_id,
            individual2.household.unicef_id,
        ]
        assert pageTargetingDetails.getHouseholdTableCell(2, 1).text in [
            individual1.household.unicef_id,
            individual2.household.unicef_id,
        ]

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_create_targeting_with_pdu_date_criteria(
        self,
        program: Program,
        pageTargeting: Targeting,
        pageTargetingCreate: TargetingCreate,
        pageTargetingDetails: TargetingDetails,
        individual: Callable,
        date_attribute: FlexibleAttribute,
    ) -> None:
        individual1 = individual(program)
        individual1.flex_fields[date_attribute.name]["1"]["value"] = "2022-02-02"
        individual1.save()
        individual2 = individual(program)
        individual2.flex_fields[date_attribute.name]["1"]["value"] = "2022-10-02"
        individual2.save()
        individual(program)
        pageTargeting.navigate_to_page("afghanistan", program.slug)
        pageTargeting.getButtonCreateNew().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getFiltersProgramCycleAutocomplete().click()
        pageTargetingCreate.select_listbox_element("Cycle In Programme")
        pageTargetingCreate.getAddCriteriaButton().click()
        pageTargetingCreate.getAddIndividualRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys("Test Date Attribute")
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ARROW_DOWN)
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ENTER)
        pageTargetingCreate.getSelectIndividualsiFltersBlocksRoundNumber().click()
        pageTargetingCreate.getSelectRoundOption(1).click()
        pageTargetingCreate.getInputDateIndividualsFiltersBlocksValueFrom().click()
        pageTargetingCreate.getInputDateIndividualsFiltersBlocksValueFrom().send_keys("2022-01-01")
        pageTargetingCreate.getInputDateIndividualsFiltersBlocksValueTo().click()
        pageTargetingCreate.getInputDateIndividualsFiltersBlocksValueTo().send_keys("2022-03-03")
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        pageTargetingCreate.getNoValidationFspAccept().click()
        expected_criteria_text = "Test Date Attribute: 2022-01-01 - 2022-03-03\nRound 1 (Test Round Date 1)"
        assert pageTargetingCreate.getCriteriaContainer().text == expected_criteria_text
        targeting_name = "Test Targeting PDU date"
        pageTargetingCreate.getFieldName().send_keys(targeting_name)
        pageTargetingCreate.getTargetPopulationSaveButton().click()
        pageTargetingDetails.getLockButton()
        assert pageTargetingDetails.getTitlePage().text.split("\n")[0].strip() == targeting_name
        assert pageTargetingDetails.getCriteriaContainer().text == expected_criteria_text
        assert Household.objects.count() == 3
        pageTargetingDetails.wait_for_text(
            individual1.household.unicef_id, pageTargetingDetails.household_table_cell.format(1, 1)
        )
        assert pageTargetingDetails.getHouseholdTableCell(1, 1).text == individual1.household.unicef_id
        assert len(pageTargetingDetails.getHouseholdTableRows()) == 1
        assert pageTargetingCreate.getTotalNumberOfHouseholdsCount().text == "1"

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_create_targeting_with_pdu_null_criteria(
        self,
        program: Program,
        pageTargeting: Targeting,
        pageTargetingCreate: TargetingCreate,
        pageTargetingDetails: TargetingDetails,
        individual: Callable,
        string_attribute: FlexibleAttribute,
    ) -> None:
        individual1 = individual(program)
        individual1.flex_fields[string_attribute.name]["1"]["value"] = "Text"
        individual1.save()
        individual2 = individual(program)
        individual2.flex_fields[string_attribute.name]["1"]["value"] = "Test"
        individual2.save()
        individual3 = individual(program)
        pageTargeting.navigate_to_page("afghanistan", program.slug)
        pageTargeting.getButtonCreateNew().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getFiltersProgramCycleAutocomplete().click()
        pageTargetingCreate.select_listbox_element("Cycle In Programme")
        pageTargetingCreate.getAddCriteriaButton().click()
        pageTargetingCreate.getAddIndividualRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys("Test String Attribute")
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ARROW_DOWN)
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ENTER)
        pageTargetingCreate.getSelectIndividualsiFltersBlocksRoundNumber().click()
        pageTargetingCreate.getSelectRoundOption(1).click()
        pageTargetingCreate.getSelectIndividualsiFltersBlocksIsNull().click()
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        pageTargetingCreate.getNoValidationFspAccept().click()
        expected_criteria_text = "Test String Attribute: Empty\nRound 1 (Test Round String 1)"
        assert pageTargetingCreate.getCriteriaContainer().text == expected_criteria_text
        targeting_name = "Test Targeting PDU null"
        pageTargetingCreate.getFieldName().send_keys(targeting_name)
        pageTargetingCreate.getTargetPopulationSaveButton().click()
        pageTargetingDetails.getLockButton()
        assert pageTargetingDetails.getTitlePage().text.split("\n")[0].strip() == targeting_name
        assert pageTargetingDetails.getCriteriaContainer().text == expected_criteria_text
        assert Household.objects.count() == 3
        assert PaymentPlan.objects.get(name=targeting_name).payment_items.count() == 1
        assert pageTargetingCreate.getTotalNumberOfHouseholdsCount().text == "1"
        pageTargetingDetails.wait_for_text(
            individual3.household.unicef_id, pageTargetingDetails.household_table_cell.format(1, 1)
        )
        assert len(pageTargetingDetails.getHouseholdTableRows()) == 1
        assert pageTargetingDetails.getHouseholdTableCell(1, 1).text == individual3.household.unicef_id

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_create_targeting_for_people_with_pdu(
        self,
        sw_program: Program,
        pageTargeting: Targeting,
        pageTargetingCreate: TargetingCreate,
        pageTargetingDetails: TargetingDetails,
        individual: Callable,
    ) -> None:
        string_attribute_for_sw = create_flexible_attribute(
            label="Test String Attribute SW",
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=1,
            rounds_names=["Test Round String 1"],
            program=sw_program,
        )
        individual1 = individual(sw_program)
        individual1.flex_fields[string_attribute_for_sw.name]["1"]["value"] = "Text"
        individual1.save()
        individual2 = individual(sw_program)
        individual2.flex_fields[string_attribute_for_sw.name]["1"]["value"] = "Failed"
        individual2.save()
        individual(sw_program)
        pageTargeting.navigate_to_page("afghanistan", sw_program.slug)
        pageTargeting.getButtonCreateNew().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getFiltersProgramCycleAutocomplete().click()
        pageTargetingCreate.select_listbox_element("First Cycle In Programme")
        pageTargetingCreate.getAddCriteriaButton().click()
        assert pageTargetingCreate.getAddPeopleRuleButton().text.upper() == "ADD PEOPLE RULE"
        pageTargetingCreate.getAddPeopleRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        # pageTargetingCreate.select_listbox_element("Test String Attribute SW")  # not works
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys("Test String Attribute")
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ARROW_DOWN)
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ENTER)
        pageTargetingCreate.getSelectFiltersRoundNumber().click()
        pageTargetingCreate.getSelectRoundOption(1).click()
        pageTargetingCreate.getInputFiltersValue().send_keys("Text")
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        pageTargetingCreate.getNoValidationFspAccept().click()
        expected_criteria_text = "Test String Attribute SW: Text\nRound 1 (Test Round String 1)"
        assert pageTargetingCreate.getCriteriaContainer().text == expected_criteria_text
        targeting_name = "Test Targeting SW PDU str"
        pageTargetingCreate.getFieldName().send_keys(targeting_name)
        pageTargetingCreate.getTargetPopulationSaveButton().click()
        pageTargetingDetails.getLockButton()

        assert pageTargetingDetails.getTitlePage().text.split("\n")[0].strip() == targeting_name
        assert pageTargetingDetails.getCriteriaContainer().text == expected_criteria_text
        assert Household.objects.count() == 3
        assert PaymentPlan.objects.get(name=targeting_name).payment_items.count() == 1
        assert pageTargetingCreate.getTotalNumberOfPeopleCount().text == "1"

        pageTargetingDetails.wait_for_text(
            individual1.unicef_id, pageTargetingDetails.household_table_cell.format(1, 1)
        )

        assert len(pageTargetingDetails.getPeopleTableRows()) == 1
        assert pageTargetingDetails.getHouseholdTableCell(1, 1).text == individual1.unicef_id


@pytest.mark.night
@pytest.mark.usefixtures("login")
class TestTargeting:
    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_targeting_create_use_ids_hh(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        assert "New Target Population" in pageTargetingCreate.getPageHeaderTitle().text
        assert "SAVE" in pageTargetingCreate.getButtonTargetPopulationCreate().text
        pageTargetingCreate.getFiltersProgramCycleAutocomplete().click()
        pageTargetingCreate.select_listbox_element("First Cycle In Programme")
        pageTargetingCreate.getDivTargetPopulationAddCriteria().click()
        pageTargetingCreate.getInputHouseholdids().click()
        pageTargetingCreate.getInputHouseholdids().send_keys(household_with_disability.unicef_id)
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        pageTargetingCreate.getNoValidationFspAccept().click()
        pageTargetingCreate.getInputName().send_keys(f"Target Population for {household_with_disability.unicef_id}")
        pageTargetingCreate.clickButtonTargetPopulationCreate()
        target_population = PaymentPlan.objects.get(name__startswith="Target Population for")
        assert str(target_population.total_individuals_count) == pageTargetingDetails.getLabelTargetedIndividuals().text
        assert (
            str(target_population.total_households_count) == pageTargetingDetails.getLabelTotalNumberOfHouseholds().text
        )
        assert str(target_population.status) == "TP_OPEN"
        assert "OPEN" in pageTargetingDetails.getLabelStatus().text

    @pytest.mark.xfail(reason="Problem with deadlock during test - 202318")
    def test_targeting_create_use_ids_individual(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        assert "New Target Population" in pageTargetingCreate.getPageHeaderTitle().text
        assert "SAVE" in pageTargetingCreate.getButtonTargetPopulationCreate().text
        pageTargetingCreate.getFiltersProgramCycleAutocomplete().click()
        pageTargetingCreate.select_listbox_element("First Cycle In Programme")
        pageTargetingCreate.getInputIndividualids().send_keys("IND-88-0000.0002")
        pageTargetingCreate.getInputName().send_keys("Target Population for IND-88-0000.0002")
        pageTargetingCreate.clickButtonTargetPopulationCreate()
        target_population = PaymentPlan.objects.get(name="Target Population for IND-88-0000.0002")
        assert (
            "4"
            == str(target_population.total_individuals_count)
            == pageTargetingDetails.getLabelTargetedIndividuals().text
        )
        assert (
            str(target_population.total_households_count) == pageTargetingDetails.getLabelTotalNumberOfHouseholds().text
        )
        assert str(target_population.status) in pageTargetingDetails.getLabelStatus().text
        pageTargetingDetails.getButtonRebuild().click()

    @pytest.mark.xfail(reason="Problem with deadlock during test - 202318")
    def test_targeting_rebuild(
        self,
        create_programs: None,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        pageTargeting.chooseTargetPopulations(0).click()
        pageTargetingDetails.getLabelStatus()
        pageTargetingDetails.getButtonRebuild().click()
        pageTargetingDetails.getStatusContainer()
        pageTargetingDetails.disappearStatusContainer()

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_targeting_mark_ready(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
        filters: Filters,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        # filters.selectFiltersSatus("TP_OPEN")
        pageTargeting.chooseTargetPopulations(0).click()
        pageTargetingDetails.getLabelStatus()
        pageTargetingDetails.getLockButton().click()
        pageTargetingDetails.getLockPopupButton().click()
        pageTargetingDetails.waitForLabelStatus("LOCKED")
        pageTargetingDetails.screenshot("targeting_locked.png")
        pageTargetingDetails.getButtonMarkReady().click()
        pageTargetingDetails.screenshot("targeting_lockedgetButtonMarkReady.png")
        pageTargetingDetails.getButtonPopupMarkReady().click()
        pageTargetingDetails.waitForLabelStatus("READY FOR PAYMENT MODULE")

    @pytest.mark.xfail(reason="Problem with deadlock during test - 202318")
    def test_copy_targeting(
        self,
        create_programs: None,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        program = Program.objects.get(name="Test Programm")
        pageTargeting.selectGlobalProgramFilter(program.name)
        pageTargeting.getNavTargeting().click()
        pageTargeting.chooseTargetPopulations(0).click()
        pageTargetingDetails.getButtonTargetPopulationDuplicate().click()
        pageTargetingCreate.getFiltersProgramCycleAutocomplete().click()
        pageTargetingCreate.select_listbox_element("First Cycle In Programme")
        pageTargetingDetails.getInputName().send_keys("a1!")
        pageTargetingDetails.get_elements(pageTargetingDetails.buttonTargetPopulationDuplicate)[1].click()
        pageTargetingDetails.disappearInputName()
        assert "a1!" in pageTargetingDetails.getTitlePage().text
        assert "OPEN" in pageTargetingDetails.getTargetPopulationStatus().text
        assert "PROGRAMME" in pageTargetingDetails.getLabelizedFieldContainerProgramName().text
        assert "Test Programm" in pageTargetingDetails.getLabelProgramme().text
        assert "2" in pageTargetingDetails.getLabelTotalNumberOfHouseholds().text
        assert "8" in pageTargetingDetails.getLabelTargetedIndividuals().text

    @pytest.mark.xfail(reason="Problem with select_listbox_element or getButtonIconEdit")
    def test_edit_targeting(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        pageTargeting.chooseTargetPopulations(0).click()
        pageTargetingDetails.getButtonEdit().click()
        pageTargetingDetails.getButtonIconEdit().click()
        pageTargetingCreate.getButtonHouseholdRule().send_keys(Keys.TAB)
        pageTargetingCreate.getButtonHouseholdRule().send_keys(Keys.TAB)
        pageTargetingCreate.getButtonHouseholdRule().send_keys(Keys.SPACE)
        # pageTargetingCreate.getButtonHouseholdRule().click()
        pageTargetingCreate.getAutocompleteTargetCriteriaOption().click()
        pageTargetingCreate.select_listbox_element("What is the Household size?")
        # pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys("What is the Household size")
        # pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ARROW_DOWN)
        # pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ENTER)
        pageTargetingDetails.getHouseholdSizeFrom().send_keys("0")
        pageTargetingDetails.getHouseholdSizeTo().send_keys("9")
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ENTER)
        # pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        pageTargetingDetails.clear_input(pageTargetingDetails.getInputName())
        pageTargetingDetails.getInputName().send_keys("New Test Data")
        pageTargetingDetails.getInputName().send_keys(Keys.ENTER)
        # pageTargetingCreate.getButtonSave().click()
        pageTargetingDetails.getButtonEdit()
        assert pageTargetingDetails.waitForTextTitlePage("New Test Data")
        assert "9" in pageTargetingDetails.getCriteriaContainer().text

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_delete_targeting(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
    ) -> None:
        PaymentPlanFactory(
            program_cycle=ProgramCycle.objects.get(program__name="Test Programm"),
            name="Copy TP",
            status=PaymentPlan.Status.TP_OPEN,
        )
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        pageTargeting.disappearLoadingRows()
        old_list = pageTargeting.getTargetPopulationsRows()
        assert 2 == len(old_list)
        assert "Copy TP" in old_list[0].text

        pageTargeting.chooseTargetPopulations(0).click()
        pageTargetingDetails.getButtonDelete().click()
        pageTargetingDetails.getDialogBox()
        pageTargetingDetails.get_elements(pageTargetingDetails.buttonDelete)[1].click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.disappearLoadingRows()
        new_list = pageTargeting.getTargetPopulationsRows()
        assert 1 == len(new_list)
        assert create_targeting.name in new_list[0].text

    @pytest.mark.xfail(reason="Problem with deadlock during test - 202318")
    def test_targeting_different_program_statuses(
        self,
        create_programs: None,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        program = Program.objects.get(name="Test Programm")
        program.status = Program.DRAFT
        program.save()
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        pageTargeting.mouse_on_element(pageTargeting.getButtonInactiveCreateNew())
        assert "Program has to be active to create a new Target Population" in pageTargeting.geTooltip().text
        program.status = Program.ACTIVE
        program.save()
        pageTargeting.driver.refresh()
        pageTargeting.getButtonCreateNew()
        program.status = Program.FINISHED
        program.save()
        pageTargeting.driver.refresh()
        pageTargeting.mouse_on_element(pageTargeting.getButtonInactiveCreateNew())
        assert "Program has to be active to create a new Target Population" in pageTargeting.geTooltip().text

    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "type": "STANDARD",
                    "text": "Exclude Items Groups with Active Adjudication Ticket",
                },
                id="Programme population",
            ),
        ],
    )
    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_exclude_households_with_active_adjudication_ticket(
        self,
        test_data: dict,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        program = Program.objects.get(name="Test Programm")
        program.data_collecting_type.type = test_data["type"]
        program.data_collecting_type.save()
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        pageTargetingCreate.getFiltersProgramCycleAutocomplete().click()
        pageTargetingCreate.select_listbox_element("First Cycle In Programme")
        pageTargetingCreate.getDivTargetPopulationAddCriteria().click()
        pageTargetingCreate.getInputHouseholdids().click()
        pageTargetingCreate.getInputHouseholdids().send_keys(household_with_disability.unicef_id)
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        pageTargetingCreate.getNoValidationFspAccept().click()
        pageTargetingCreate.getInputName().send_keys(f"Test {household_with_disability.unicef_id}")
        pageTargetingCreate.getInputFlagexcludeifactiveadjudicationticket().click()
        pageTargetingCreate.clickButtonTargetPopulationCreate()
        with pytest.raises(NoSuchElementException):
            pageTargetingDetails.getCheckboxExcludeIfOnSanctionList().find_element(
                By.CSS_SELECTOR, pageTargetingDetails.iconSelected
            )
        if test_data["type"] == "SOCIAL":
            pageTargetingDetails.getCheckboxExcludePeopleIfActiveAdjudicationTicket()
            pageTargetingDetails.getCheckboxExcludePeopleIfActiveAdjudicationTicket().find_element(
                By.CSS_SELECTOR, pageTargetingDetails.iconSelected
            )
            assert (
                test_data["text"]
                in pageTargetingDetails.getCheckboxExcludePeopleIfActiveAdjudicationTicket()
                .find_element(By.XPATH, "./..")
                .text
            )
        elif test_data["type"] == "STANDARD":
            pageTargetingDetails.getCheckboxExcludeIfActiveAdjudicationTicket()
            pageTargetingDetails.getCheckboxExcludeIfActiveAdjudicationTicket().find_element(
                By.CSS_SELECTOR, pageTargetingDetails.iconSelected
            )
            assert (
                test_data["text"]
                in pageTargetingDetails.getCheckboxExcludeIfActiveAdjudicationTicket()
                .find_element(By.XPATH, "./..")
                .text
            )

    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "type": "SOCIAL",
                    "text": "Exclude People with an active sanction screen flag",
                },
                id="People",
            ),
            pytest.param(
                {
                    "type": "STANDARD",
                    "text": "Exclude Households with an active sanction screen flag",
                },
                id="Programme population",
            ),
        ],
    )
    @pytest.mark.xfail(reason="Problem with deadlock during test - 202318")
    def test_exclude_households_with_sanction_screen_flag(
        self,
        test_data: dict,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        program = Program.objects.get(name="Test Programm")
        program.data_collecting_type.type = test_data["type"]
        program.data_collecting_type.save()
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        pageTargetingCreate.getFiltersProgramCycleAutocomplete().click()
        pageTargetingCreate.select_listbox_element("First Cycle In Programme")
        pageTargetingCreate.getInputHouseholdids().click()
        pageTargetingCreate.getInputHouseholdids().send_keys(household_with_disability.unicef_id)
        pageTargetingCreate.getInputName().send_keys(f"Test {household_with_disability.unicef_id}")
        pageTargetingCreate.getInputFlagexcludeifonsanctionlist().click()
        pageTargetingCreate.clickButtonTargetPopulationCreate()
        pageTargetingDetails.getCheckboxExcludeIfOnSanctionList()
        # ToDo: Add after merge to develop
        # assert (
        #     test_data["text"]
        #     in pageTargetingDetails.getCheckboxExcludeIfOnSanctionList().find_element(By.XPATH, "./..").text
        # )
        pageTargetingDetails.getCheckboxExcludeIfOnSanctionList().find_element(
            By.CSS_SELECTOR, pageTargetingDetails.iconSelected
        )
        with pytest.raises(NoSuchElementException):
            pageTargetingDetails.getCheckboxExcludePeopleIfActiveAdjudicationTicket().find_element(
                By.CSS_SELECTOR, pageTargetingDetails.iconSelected
            )

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_targeting_info_button(
        self,
        create_programs: None,
        pageTargeting: Targeting,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonTargetPopulation().click()
        pageTargeting.getTabFieldList()
        pageTargeting.getTabTargetingDiagram().click()

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_targeting_filters(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
        filters: Filters,
    ) -> None:
        PaymentPlanFactory(
            program_cycle=ProgramCycle.objects.get(program__name="Test Programm"),
            name="Copy TP",
            status=PaymentPlan.Status.TP_PROCESSING,
        )
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        filters.getFiltersSearch().send_keys("Copy")
        filters.getButtonFiltersApply().click()
        pageTargeting.countTargetPopulations(1)
        assert "PROCESSING" in pageTargeting.getStatusContainer().text
        filters.getButtonFiltersClear().click()
        filters.getFiltersStatus().click()
        filters.select_listbox_element("Open")
        filters.getButtonFiltersApply().click()
        pageTargeting.countTargetPopulations(1)
        assert "OPEN" in pageTargeting.getStatusContainer().text
        filters.getButtonFiltersClear().click()
        filters.getFiltersTotalHouseholdsCountMin().send_keys("10")
        filters.getFiltersTotalHouseholdsCountMax().send_keys("10")
        filters.getButtonFiltersApply().click()
        pageTargeting.countTargetPopulations(0)
        filters.getButtonFiltersClear().click()
        filters.getFiltersTotalHouseholdsCountMin().send_keys("1")
        filters.getFiltersTotalHouseholdsCountMax().send_keys("3")
        pageTargeting.countTargetPopulations(2)
        filters.getButtonFiltersClear().click()

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_targeting_and_labels(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
    ) -> None:
        if not (user2 := User.objects.filter(pk="4196c2c5-c2dd-48d2-887f-3a9d39e88999").first()):
            user2 = UserFactory(
                pk="4196c2c5-c2dd-48d2-887f-3a9d39e88999",
                first_name="ABC",
                last_name="LastName",
            )
        PaymentPlanFactory(
            program_cycle=ProgramCycle.objects.get(program__name="Test Programm"),
            name="A Copy TP",
            status=PaymentPlan.Status.TP_PROCESSING,
            created_by=user2,
            total_households_count=1,
        )
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        pageTargeting.getColumnName().click()
        pageTargeting.disappearLoadingRows()
        assert "A Copy TP" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnName().click()
        pageTargeting.disappearLoadingRows()
        assert "Test Target Population" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnStatus().click()
        pageTargeting.disappearLoadingRows()
        assert "A Copy TP" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnStatus().click()
        pageTargeting.disappearLoadingRows()
        assert "Test Target Population" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnNumOfHouseholds().click()
        pageTargeting.disappearLoadingRows()
        assert "A Copy TP" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnDateCreated().click()
        pageTargeting.disappearLoadingRows()
        assert "Test Target Population" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnDateCreated().click()
        pageTargeting.disappearLoadingRows()
        assert "A Copy TP" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnLastEdited().click()
        pageTargeting.disappearLoadingRows()
        assert "Test Target Population" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnLastEdited().click()
        pageTargeting.disappearLoadingRows()
        assert "A Copy TP" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnCreatedBy().click()
        pageTargeting.disappearLoadingRows()
        assert "Test Target Population" in pageTargeting.chooseTargetPopulations(0).text

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_targeting_parametrized_rules_filters(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getFiltersProgramCycleAutocomplete().click()
        pageTargetingCreate.select_listbox_element("First Cycle In Programme")
        pageTargetingCreate.getAddCriteriaButton().click()
        pageTargetingCreate.getAddPeopleRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.select_listbox_element("Females Age 0 - 5")
        pageTargetingCreate.getInputFiltersValueFrom(0).send_keys("0")
        pageTargetingCreate.getInputFiltersValueTo(0).send_keys("1")
        pageTargetingCreate.getInputFiltersValueTo(0).send_keys("1")
        pageTargetingCreate.getButtonTargetPopulationAddCriteria().click()
        pageTargetingCreate.getNoValidationFspAccept().click()
        pageTargetingCreate.getInputName().send_keys("Target Population for Females Age 0 - 5")
        pageTargetingCreate.getInputFlagexcludeifactiveadjudicationticket().click()
        pageTargetingCreate.clickButtonTargetPopulationCreate()
        assert "Females Age 0 - 5: 11" in pageTargetingCreate.getCriteriaContainer().text

    @pytest.mark.xfail(reason="Problem with deadlock during test - 202318")
    def test_targeting_parametrized_rules_filters_and_or(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm")
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getFiltersProgramCycleAutocomplete().click()
        pageTargetingCreate.select_listbox_element("First Cycle In Programme")
        pageTargetingCreate.getAddCriteriaButton().click()
        pageTargetingCreate.getAddPeopleRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.select_listbox_element("Females Age 0 - 5")
        pageTargetingCreate.getInputFiltersValueFrom(0).send_keys("0")
        pageTargetingCreate.getInputFiltersValueTo(0).send_keys("1")
        pageTargetingCreate.getButtonHouseholdRule().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete(1).click()
        pageTargetingCreate.select_listbox_element("Village")
        pageTargetingCreate.getInputFiltersValue(1).send_keys("Testtown")
        pageTargetingCreate.getButtonIndividualRule().click()
        pageTargetingCreate.getTargetingCriteriaAutoCompleteIndividual().click()
        pageTargetingCreate.select_listbox_element("Does the Individual have disability?")
        pageTargetingCreate.getSelectMany().click()
        pageTargetingCreate.select_multiple_option_by_name(HEARING, SEEING)
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        assert "Females Age 0 - 5: 1" in pageTargetingCreate.getCriteriaContainer().text
        assert "Village: Testtown" in pageTargetingCreate.getCriteriaContainer().text
        assert (
            "Does the Individual have disability?: Difficulty hearing (even if using a hearing aid), Difficulty seeing (even if wearing glasses)"
            in pageTargetingCreate.getCriteriaContainer().text
        )
        pageTargetingCreate.getButtonEdit().click()
        pageTargetingCreate.getTargetingCriteriaAutoCompleteIndividual()
        pageTargetingCreate.get_elements(pageTargetingCreate.targetingCriteriaAddDialogSaveButton)[1].click()
        pageTargetingCreate.getInputName().send_keys("Target Population")
        assert "ADD 'OR'FILTER" in pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().text
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        pageTargetingCreate.getAddHouseholdRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.select_listbox_element("Males age 0 - 5 with disability")
        pageTargetingCreate.getInputFiltersValueFrom(0).send_keys("1")
        pageTargetingCreate.getInputFiltersValueTo(0).send_keys("10")
        pageTargetingCreate.get_elements(pageTargetingCreate.targetingCriteriaAddDialogSaveButton)[1].click()
        pageTargetingCreate.getTargetPopulationSaveButton().click()
        assert "Females Age 0 - 5: 1" in pageTargetingCreate.getCriteriaContainer().text
        assert "Village: Testtown" in pageTargetingCreate.getCriteriaContainer().text
        assert (
            "Does the Individual have disability?: Difficulty hearing (even if using a hearing aid), Difficulty seeing (even if wearing glasses)"
            in pageTargetingCreate.getCriteriaContainer().text
        )
        assert (
            "Males age 0 - 5 with disability: 1 -10"
            in pageTargetingCreate.get_elements(pageTargetingCreate.criteriaContainer)[1].text
        )
