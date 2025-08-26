from datetime import datetime
from typing import Callable

import factory
import pytest
from dateutil.relativedelta import relativedelta
from e2e.page_object.filters import Filters
from e2e.page_object.targeting.targeting import Targeting
from e2e.page_object.targeting.targeting_create import TargetingCreate
from e2e.page_object.targeting.targeting_details import TargetingDetails
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
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By

from hope.models.user import User
from hope.models.business_area import (
    BusinessArea,
)
from hope.models.data_collecting_type import DataCollectingType
from hope.models.flexible_attribute import FlexibleAttribute, PeriodicFieldData
from hope.models.household import (
    HEARING,
    HOST,
    REFUGEE,
    ROLE_PRIMARY,
    SEEING,
    Household,
)
from hope.models.individual import Individual
from hope.models import (
    DeliveryMechanism,
    FinancialServiceProvider,
    PaymentPlan,
)
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.apps.periodic_data_update.utils import (
    field_label_to_field_name,
    populate_pdu_with_null_values,
)
from hope.models.program import Program
from hope.models.program_cycle import ProgramCycle
from hope.models.beneficiary_group import BeneficiaryGroup
from hope.models.rule import Rule

pytestmark = pytest.mark.django_db()


@pytest.fixture
def sw_program() -> Program:
    yield get_program_with_dct_type_and_name(
        "Test Programm",
        dct_type=DataCollectingType.Type.SOCIAL,
        status=Program.ACTIVE,
        beneficiary_group_name="People",
    )


@pytest.fixture
def non_sw_program() -> Program:
    yield get_program_with_dct_type_and_name(
        "Test Programm",
        dct_type=DataCollectingType.Type.STANDARD,
        status=Program.ACTIVE,
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
    label: str,
    subtype: str,
    number_of_rounds: int,
    rounds_names: list[str],
    program: Program,
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
    observed_disability: list[str],
    residence_status: str = HOST,
    unicef_id: str = "HH-00-0000.0442",
    size: int = 2,
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
    def test_smoke_targeting_page(
        self,
        create_programs: None,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
    ) -> None:
        PaymentPlanFactory(
            program_cycle=ProgramCycle.objects.get(program__name="Test Programm"),
            name="Copy TP",
            status=PaymentPlan.Status.TP_OPEN,
        )
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        assert "Targeting" in page_targeting.get_title_page().text
        assert "CREATE NEW" in page_targeting.get_button_create_new().text
        expected_column_names = [
            "Name",
            "Status",
            "Num. of Items Groups",
            "Date Created",
            "Last Edited",
            "Created by",
        ]
        assert expected_column_names == [name.text for name in page_targeting.get_tab_column_label()]
        assert len(page_targeting.get_target_populations_rows()) == 2
        page_targeting.get_button_create_new().click()

    def test_smoke_targeting_create_use_filters(
        self,
        create_programs: None,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
        page_targeting_create: TargetingCreate,
    ) -> None:
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        page_targeting.get_button_create_new().click()
        assert "New Target Population" in page_targeting_create.get_page_header_title().text
        assert "SAVE" in page_targeting_create.get_button_target_population_create().text
        page_targeting_create.get_input_name()
        page_targeting_create.get_div_target_population_add_criteria().click()
        page_targeting_create.get_button_household_rule().click()
        page_targeting_create.get_button_individual_rule().click()
        page_targeting_create.get_autocomplete_target_criteria_option().click()

    def test_smoke_targeting_create_use_ids(
        self,
        create_programs: None,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
        page_targeting_create: TargetingCreate,
    ) -> None:
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        page_targeting.get_button_create_new().click()
        assert "New Target Population" in page_targeting_create.get_page_header_title().text
        assert "SAVE" in page_targeting_create.get_button_target_population_create().text
        page_targeting_create.get_input_name()
        page_targeting_create.get_div_target_population_add_criteria().click()
        page_targeting_create.get_input_included_household_ids()
        page_targeting_create.get_input_household_ids()
        page_targeting_create.get_input_included_individual_ids()
        page_targeting_create.get_input_individual_ids()

    def test_smoke_targeting_details_page(
        self,
        create_programs: None,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
        page_targeting_details: TargetingDetails,
    ) -> None:
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        page_targeting.choose_target_populations(0).click()
        assert create_targeting.name in page_targeting_details.get_page_header_title().text
        page_targeting_details.get_button_target_population_duplicate()
        page_targeting_details.get_button_delete()
        assert "EDIT" in page_targeting_details.get_button_edit().text
        assert "REBUILD" in page_targeting_details.get_button_rebuild().text
        assert "LOCK" in page_targeting_details.get_button_target_population_lock().text
        assert "Details" in page_targeting_details.get_details_title().text
        assert "OPEN" in page_targeting_details.get_label_status().text
        assert "OPEN" in page_targeting_details.get_target_population_status().text
        assert "CREATED BY" in page_targeting_details.get_labelized_field_container_created_by().text
        page_targeting_details.get_label_created_by()
        # assert "PROGRAMME POPULATION CLOSE DATE" in page_targeting_details.getLabelizedFieldContainerCloseDate().text
        assert "PROGRAMME" in page_targeting_details.get_labelized_field_container_program_name().text
        assert "Test Programm" in page_targeting_details.get_label_programme().text
        # assert "SEND BY" in page_targeting_details.getLabelizedFieldContainerSendBy().text
        # assert "-" in page_targeting_details.getLabelSendBy().text
        # assert "-" in page_targeting_details.getLabelSendDate().text
        assert "5" in page_targeting_details.get_label_female_children().text
        assert "3" in page_targeting_details.get_label_male_children().text
        assert "2" in page_targeting_details.get_label_female_adults().text
        assert "1" in page_targeting_details.get_label_male_adults().text
        assert "2" in page_targeting_details.get_label_total_number_of_households().text
        assert "11" in page_targeting_details.get_label_targeted_individuals().text
        assert "Items Groups" in page_targeting_details.get_table_title().text
        expected_menu_items = [
            "ID",
            "Head of Items Group",
            "Items Group Size",
            "Administrative Level 2",
            "Score",
        ]
        assert expected_menu_items == [i.text for i in page_targeting_details.get_table_label()]


@pytest.mark.night
@pytest.mark.usefixtures("login")
class TestCreateTargeting:
    def test_create_targeting_for_people(
        self,
        sw_program: Program,
        household_with_disability: Household,
        household_without_disabilities: Household,
        page_targeting: Targeting,
        page_targeting_create: TargetingCreate,
        page_targeting_details: TargetingDetails,
    ) -> None:
        page_targeting.navigate_to_page("afghanistan", sw_program.slug)
        page_targeting.get_button_create_new().click()

        assert "New Target Population" in page_targeting_create.get_title_page().text
        page_targeting_create.get_filters_program_cycle_autocomplete().click()
        page_targeting_create.select_listbox_element("First Cycle In Programme")
        page_targeting_create.get_add_criteria_button().click()
        assert page_targeting_create.get_add_people_rule_button().text.upper() == "ADD PEOPLE RULE"
        page_targeting_create.get_add_people_rule_button().click()
        page_targeting_create.get_targeting_criteria_auto_complete().click()
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(
            "Does the Social Worker have disability?"
        )
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ARROW_DOWN)
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ENTER)
        page_targeting_create.get_targeting_criteria_value().click()
        page_targeting_create.select_multiple_option_by_name(HEARING, SEEING)
        page_targeting_create.get_targeting_criteria_add_dialog_save_button().click()
        page_targeting_create.get_no_validation_fsp_accept().click()
        disability_expected_criteria_text = "Does the Social Worker have disability?: Difficulty hearing (even if using a hearing aid), Difficulty seeing (even if wearing glasses)"
        assert page_targeting_create.get_criteria_container().text == disability_expected_criteria_text
        targeting_name = "Test targeting people"
        page_targeting_create.get_field_name().send_keys(targeting_name)
        page_targeting_create.get_target_population_save_button().click()
        page_targeting_details.get_lock_button()
        assert page_targeting_details.get_title_page().text.split("\n")[0].strip() == targeting_name
        assert page_targeting_details.get_criteria_container().text == disability_expected_criteria_text
        assert Household.objects.count() == 2
        assert PaymentPlan.objects.get(name=targeting_name).payment_items.count() == 1
        individual = household_with_disability.individuals.first()
        page_targeting_details.wait_for_text(
            individual.unicef_id,
            page_targeting_details.household_table_cell.format(1, 1),
        )
        assert len(page_targeting_details.get_people_table_rows()) == 1
        assert page_targeting_details.get_household_table_cell(1, 1).text == individual.unicef_id

    def test_create_targeting_for_normal_program(
        self,
        non_sw_program: Program,
        household_with_disability: Household,
        household_without_disabilities: Household,
        household_refugee: Household,
        page_targeting: Targeting,
        page_targeting_create: TargetingCreate,
        page_targeting_details: TargetingDetails,
    ) -> None:
        page_targeting.navigate_to_page("afghanistan", non_sw_program.slug)
        page_targeting.get_button_create_new().click()
        assert "New Target Population" in page_targeting_create.get_title_page().text
        page_targeting_create.get_filters_program_cycle_autocomplete().click()
        page_targeting_create.select_listbox_element("First Cycle In Programme")
        page_targeting_create.get_add_criteria_button().click()
        assert page_targeting_create.get_add_people_rule_button().text.upper() == "ADD ITEMS GROUP RULE"
        page_targeting_create.get_add_household_rule_button().click()
        page_targeting_create.get_targeting_criteria_auto_complete().click()
        page_targeting_create.select_listbox_element("Residence status")
        page_targeting_create.get_targeting_criteria_value().click()
        page_targeting_create.get_select_refugee().click()
        page_targeting_create.get_targeting_criteria_add_dialog_save_button().click()
        page_targeting_create.get_no_validation_fsp_accept().click()
        disability_expected_criteria_text = "Residence status: Displaced | Refugee / Asylum Seeker"
        assert page_targeting_create.get_criteria_container().text == disability_expected_criteria_text
        targeting_name = "Test targeting people"
        page_targeting_create.get_field_name().send_keys(targeting_name)
        page_targeting_create.get_target_population_save_button().click()
        page_targeting_details.get_lock_button()
        assert page_targeting_details.get_title_page().text.split("\n")[0].strip() == targeting_name
        assert page_targeting_details.get_criteria_container().text == disability_expected_criteria_text
        assert Household.objects.count() == 3
        assert PaymentPlan.objects.get(name=targeting_name).payment_items.count() == 1
        page_targeting_details.wait_for_text(
            household_refugee.unicef_id,
            page_targeting_details.household_table_cell.format(1, 1),
        )
        assert len(page_targeting_details.get_household_table_rows()) == 1
        assert page_targeting_details.get_household_table_cell(1, 1).text == household_refugee.unicef_id
        actions = ActionChains(page_targeting_details.driver)
        actions.move_to_element(page_targeting_details.get_household_table_cell(1, 1)).perform()

    def test_create_targeting_with_pdu_string_criteria(
        self,
        program: Program,
        page_targeting: Targeting,
        page_targeting_create: TargetingCreate,
        page_targeting_details: TargetingDetails,
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
        page_targeting.navigate_to_page("afghanistan", program.slug)
        page_targeting.get_button_create_new().click()
        assert "New Target Population" in page_targeting_create.get_title_page().text
        page_targeting_create.get_filters_program_cycle_autocomplete().click()
        page_targeting_create.select_listbox_element("Cycle In Programme")
        page_targeting_create.get_add_criteria_button().click()
        page_targeting_create.get_add_individual_rule_button().click()
        page_targeting_create.get_targeting_criteria_auto_complete().click()
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys("Test String Attribute")
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ARROW_DOWN)
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ENTER)
        page_targeting_create.get_select_individuals_filters_blocks_round_number().click()
        page_targeting_create.get_select_round_option(1).click()
        page_targeting_create.get_input_individuals_filters_blocks_value().send_keys("Text")
        page_targeting_create.get_targeting_criteria_add_dialog_save_button().click()
        page_targeting_create.get_no_validation_fsp_accept().click()
        expected_criteria_text = "Test String Attribute: Text\nRound 1 (Test Round String 1)"
        assert page_targeting_create.get_criteria_container().text == expected_criteria_text
        targeting_name = "Test Targeting PDU str"
        page_targeting_create.get_field_name().send_keys(targeting_name)
        page_targeting_create.get_target_population_save_button().click()
        page_targeting_details.get_lock_button()
        assert page_targeting_details.get_title_page().text.split("\n")[0].strip() == targeting_name
        assert page_targeting_details.get_criteria_container().text == expected_criteria_text
        assert Household.objects.count() == 3
        assert PaymentPlan.objects.get(name=targeting_name).payment_items.count() == 1
        page_targeting_details.wait_for_text(
            individual1.household.unicef_id,
            page_targeting_details.household_table_cell.format(1, 1),
        )
        assert page_targeting_create.get_total_number_of_households_count().text == "1"
        assert len(page_targeting_details.get_household_table_rows()) == 1
        assert page_targeting_details.get_household_table_cell(1, 1).text == individual1.household.unicef_id

    @pytest.mark.xfail(reason="UNSTABLE AFTER REST REFACTOR")
    def test_create_targeting_with_pdu_bool_criteria(
        self,
        program: Program,
        page_targeting: Targeting,
        page_targeting_create: TargetingCreate,
        page_targeting_details: TargetingDetails,
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
        page_targeting.navigate_to_page("afghanistan", program.slug)
        page_targeting.get_button_create_new().click()
        assert "New Target Population" in page_targeting_create.get_title_page().text
        page_targeting_create.get_filters_program_cycle_autocomplete().click()
        page_targeting_create.select_listbox_element("Cycle In Programme")
        page_targeting_create.get_add_criteria_button().click()
        page_targeting_create.get_add_individual_rule_button().click()
        page_targeting_create.get_targeting_criteria_auto_complete().click()
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys("Test Bool Attribute")
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ARROW_DOWN)
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ENTER)
        page_targeting_create.get_select_individuals_filters_blocks_round_number().click()
        page_targeting_create.get_select_round_option(2).click()
        page_targeting_create.get_select_individuals_filters_blocks_value().click()
        page_targeting_create.select_option_by_name("Yes")
        page_targeting_create.get_targeting_criteria_add_dialog_save_button().click()
        page_targeting_create.get_no_validation_fsp_accept().click()
        bool_yes_expected_criteria_text = "Test Bool Attribute: Yes\nRound 2 (Test Round Bool 2)"
        assert page_targeting_create.get_criteria_container().text == bool_yes_expected_criteria_text

        targeting_name = "Test Targeting PDU bool"
        page_targeting_create.get_field_name().send_keys(targeting_name)
        page_targeting_create.get_target_population_save_button().click()

        page_targeting_details.get_lock_button()

        assert page_targeting_details.get_title_page().text.split("\n")[0].strip() == targeting_name
        assert page_targeting_details.get_criteria_container().text == bool_yes_expected_criteria_text
        assert Household.objects.count() == 3
        page_targeting_details.wait_for_text(
            individual1.household.unicef_id,
            page_targeting_details.household_table_cell.format(1, 1),
        )
        assert page_targeting_details.get_household_table_cell(1, 1).text == individual1.household.unicef_id
        assert page_targeting_create.get_total_number_of_households_count().text == "1"
        assert len(page_targeting_details.get_household_table_rows()) == 1

        # edit to False
        page_targeting_details.get_button_edit().click()
        page_targeting_details.get_button_icon_edit().click()
        page_targeting_create.get_select_individuals_filters_blocks_value().click()
        page_targeting_create.select_option_by_name("No")
        bool_no_expected_criteria_text = "Test Bool Attribute: No\nRound 2 (Test Round Bool 2)"

        page_targeting_create.get_elements(page_targeting_create.targetingCriteriaAddDialogSaveButton)[1].click()
        page_targeting_create.get_no_validation_fsp_accept().click()
        assert page_targeting_create.get_criteria_container().text == bool_no_expected_criteria_text
        page_targeting_create.get_button_save().click()
        page_targeting_details.get_lock_button()

        page_targeting_details.wait_for_text(
            individual2.household.unicef_id,
            page_targeting_details.household_table_cell.format(1, 1),
        )
        assert page_targeting_details.get_criteria_container().text == bool_no_expected_criteria_text
        assert page_targeting_details.get_household_table_cell(1, 1).text == individual2.household.unicef_id
        assert page_targeting_create.get_total_number_of_households_count().text == "1"
        assert len(page_targeting_details.get_household_table_rows()) == 1

    @pytest.mark.xfail(reason="UNSTABLE AFTER REST REFACTOR")
    def test_create_targeting_with_pdu_decimal_criteria(
        self,
        program: Program,
        page_targeting: Targeting,
        page_targeting_create: TargetingCreate,
        page_targeting_details: TargetingDetails,
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
        page_targeting.navigate_to_page("afghanistan", program.slug)
        page_targeting.get_button_create_new().click()
        assert "New Target Population" in page_targeting_create.get_title_page().text
        page_targeting_create.get_filters_program_cycle_autocomplete().click()
        page_targeting_create.select_listbox_element("Cycle In Programme")
        page_targeting_create.get_add_criteria_button().click()
        page_targeting_create.get_add_individual_rule_button().click()
        page_targeting_create.get_targeting_criteria_auto_complete().click()
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys("Test Decimal Attribute")
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ARROW_DOWN)
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ENTER)
        page_targeting_create.get_select_individuals_filters_blocks_round_number().click()
        page_targeting_create.get_select_round_option(1).click()
        page_targeting_create.get_input_individuals_filters_blocks_value_from().send_keys("2")
        page_targeting_create.get_input_individuals_filters_blocks_value_to().send_keys("4")
        page_targeting_create.get_targeting_criteria_add_dialog_save_button().click()
        page_targeting_create.get_no_validation_fsp_accept().click()
        expected_criteria_text = "Test Decimal Attribute: 2 - 4\nRound 1 (Test Round Decimal 1)"
        assert page_targeting_create.get_criteria_container().text == expected_criteria_text
        targeting_name = "Test Targeting PDU decimal"
        page_targeting_create.get_field_name().send_keys(targeting_name)
        page_targeting_create.get_target_population_save_button().click()
        page_targeting_details.get_lock_button()
        assert page_targeting_details.get_title_page().text.split("\n")[0].strip() == targeting_name
        assert page_targeting_details.get_criteria_container().text == expected_criteria_text
        assert Household.objects.count() == 3
        assert PaymentPlan.objects.get(name=targeting_name).payment_items.count() == 1
        page_targeting_details.wait_for_text(
            individual1.household.unicef_id,
            page_targeting_details.household_table_cell.format(1, 1),
        )
        assert page_targeting_create.get_total_number_of_households_count().text == "1"
        assert len(page_targeting_details.get_household_table_rows()) == 1
        assert page_targeting_details.get_household_table_cell(1, 1).text == individual1.household.unicef_id

        # edit range
        page_targeting_details.get_button_edit().click()
        page_targeting_details.get_button_icon_edit().click()
        page_targeting_create.get_input_individuals_filters_blocks_value_to().send_keys(Keys.BACKSPACE)
        page_targeting_create.get_input_individuals_filters_blocks_value_to().send_keys("9")
        bool_no_expected_criteria_text = "Test Decimal Attribute: 2 - 9\nRound 1 (Test Round Decimal 1)"

        page_targeting_create.get_elements(page_targeting_create.targetingCriteriaAddDialogSaveButton)[1].click()
        page_targeting_create.get_no_validation_fsp_accept().click()

        assert page_targeting_create.get_criteria_container().text == bool_no_expected_criteria_text
        page_targeting_create.get_button_save().click()
        page_targeting_details.get_lock_button()
        page_targeting_details.disappear_status_container()
        page_targeting_details.wait_for_text(
            individual1.household.unicef_id,
            page_targeting_details.household_table_cell.format(1, 1),
        )
        assert page_targeting_details.get_criteria_container().text == bool_no_expected_criteria_text
        assert page_targeting_create.get_total_number_of_households_count().text == "2"
        assert len(page_targeting_details.get_household_table_rows()) == 2
        assert page_targeting_details.get_household_table_cell(1, 1).text in [
            individual1.household.unicef_id,
            individual2.household.unicef_id,
        ]
        assert page_targeting_details.get_household_table_cell(2, 1).text in [
            individual1.household.unicef_id,
            individual2.household.unicef_id,
        ]

    def test_create_targeting_with_pdu_date_criteria(
        self,
        program: Program,
        page_targeting: Targeting,
        page_targeting_create: TargetingCreate,
        page_targeting_details: TargetingDetails,
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
        page_targeting.navigate_to_page("afghanistan", program.slug)
        page_targeting.get_button_create_new().click()
        assert "New Target Population" in page_targeting_create.get_title_page().text
        page_targeting_create.get_filters_program_cycle_autocomplete().click()
        page_targeting_create.select_listbox_element("Cycle In Programme")
        page_targeting_create.get_add_criteria_button().click()
        page_targeting_create.get_add_individual_rule_button().click()
        page_targeting_create.get_targeting_criteria_auto_complete().click()
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys("Test Date Attribute")
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ARROW_DOWN)
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ENTER)
        page_targeting_create.get_select_individuals_filters_blocks_round_number().click()
        page_targeting_create.get_select_round_option(1).click()
        page_targeting_create.get_input_date_individuals_filters_blocks_value_from().click()
        page_targeting_create.get_input_date_individuals_filters_blocks_value_from().send_keys("2022-01-01")
        page_targeting_create.get_input_date_individuals_filters_blocks_value_to().click()
        page_targeting_create.get_input_date_individuals_filters_blocks_value_to().send_keys("2022-03-03")
        page_targeting_create.get_targeting_criteria_add_dialog_save_button().click()
        page_targeting_create.get_no_validation_fsp_accept().click()
        expected_criteria_text = "Test Date Attribute: 2022-01-01 - 2022-03-03\nRound 1 (Test Round Date 1)"
        assert page_targeting_create.get_criteria_container().text == expected_criteria_text
        targeting_name = "Test Targeting PDU date"
        page_targeting_create.get_field_name().send_keys(targeting_name)
        page_targeting_create.get_target_population_save_button().click()
        page_targeting_details.get_lock_button()
        assert page_targeting_details.get_title_page().text.split("\n")[0].strip() == targeting_name
        assert page_targeting_details.get_criteria_container().text == expected_criteria_text
        assert Household.objects.count() == 3
        page_targeting_details.wait_for_text(
            individual1.household.unicef_id,
            page_targeting_details.household_table_cell.format(1, 1),
        )
        assert page_targeting_details.get_household_table_cell(1, 1).text == individual1.household.unicef_id
        assert len(page_targeting_details.get_household_table_rows()) == 1
        assert page_targeting_create.get_total_number_of_households_count().text == "1"

    def test_create_targeting_with_pdu_null_criteria(
        self,
        program: Program,
        page_targeting: Targeting,
        page_targeting_create: TargetingCreate,
        page_targeting_details: TargetingDetails,
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
        page_targeting.navigate_to_page("afghanistan", program.slug)
        page_targeting.get_button_create_new().click()
        assert "New Target Population" in page_targeting_create.get_title_page().text
        page_targeting_create.get_filters_program_cycle_autocomplete().click()
        page_targeting_create.select_listbox_element("Cycle In Programme")
        page_targeting_create.get_add_criteria_button().click()
        page_targeting_create.get_add_individual_rule_button().click()
        page_targeting_create.get_targeting_criteria_auto_complete().click()
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys("Test String Attribute")
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ARROW_DOWN)
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ENTER)
        page_targeting_create.get_select_individuals_filters_blocks_round_number().click()
        page_targeting_create.get_select_round_option(1).click()
        page_targeting_create.get_select_individuals_filters_blocks_is_null().click()
        page_targeting_create.get_targeting_criteria_add_dialog_save_button().click()
        page_targeting_create.get_no_validation_fsp_accept().click()
        expected_criteria_text = "Test String Attribute: Empty\nRound 1 (Test Round String 1)"
        assert page_targeting_create.get_criteria_container().text == expected_criteria_text
        targeting_name = "Test Targeting PDU null"
        page_targeting_create.get_field_name().send_keys(targeting_name)
        page_targeting_create.get_target_population_save_button().click()
        page_targeting_details.get_lock_button()
        assert page_targeting_details.get_title_page().text.split("\n")[0].strip() == targeting_name
        assert page_targeting_details.get_criteria_container().text == expected_criteria_text
        assert Household.objects.count() == 3
        assert PaymentPlan.objects.get(name=targeting_name).payment_items.count() == 1
        assert page_targeting_create.get_total_number_of_households_count().text == "1"
        page_targeting_details.wait_for_text(
            individual3.household.unicef_id,
            page_targeting_details.household_table_cell.format(1, 1),
        )
        assert len(page_targeting_details.get_household_table_rows()) == 1
        assert page_targeting_details.get_household_table_cell(1, 1).text == individual3.household.unicef_id

    def test_create_targeting_for_people_with_pdu(
        self,
        sw_program: Program,
        page_targeting: Targeting,
        page_targeting_create: TargetingCreate,
        page_targeting_details: TargetingDetails,
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
        page_targeting.navigate_to_page("afghanistan", sw_program.slug)
        page_targeting.get_button_create_new().click()
        assert "New Target Population" in page_targeting_create.get_title_page().text
        page_targeting_create.get_filters_program_cycle_autocomplete().click()
        page_targeting_create.select_listbox_element("First Cycle In Programme")
        page_targeting_create.get_add_criteria_button().click()
        assert page_targeting_create.get_add_people_rule_button().text.upper() == "ADD PEOPLE RULE"
        page_targeting_create.get_add_people_rule_button().click()
        page_targeting_create.get_targeting_criteria_auto_complete().click()
        # page_targeting_create.select_listbox_element("Test String Attribute SW")  # not works
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys("Test String Attribute")
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ARROW_DOWN)
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ENTER)
        page_targeting_create.get_select_filters_round_number().click()
        page_targeting_create.get_select_round_option(1).click()
        page_targeting_create.get_input_filters_value().send_keys("Text")
        page_targeting_create.get_targeting_criteria_add_dialog_save_button().click()
        page_targeting_create.get_no_validation_fsp_accept().click()
        expected_criteria_text = "Test String Attribute SW: Text\nRound 1 (Test Round String 1)"
        assert page_targeting_create.get_criteria_container().text == expected_criteria_text
        targeting_name = "Test Targeting SW PDU str"
        page_targeting_create.get_field_name().send_keys(targeting_name)
        page_targeting_create.get_target_population_save_button().click()
        page_targeting_details.get_lock_button()

        assert page_targeting_details.get_title_page().text.split("\n")[0].strip() == targeting_name
        assert page_targeting_details.get_criteria_container().text == expected_criteria_text
        assert Household.objects.count() == 3
        assert PaymentPlan.objects.get(name=targeting_name).payment_items.count() == 1
        assert page_targeting_create.get_total_number_of_people_count().text == "1"

        page_targeting_details.wait_for_text(
            individual1.unicef_id,
            page_targeting_details.household_table_cell.format(1, 1),
        )

        assert len(page_targeting_details.get_people_table_rows()) == 1
        assert page_targeting_details.get_household_table_cell(1, 1).text == individual1.unicef_id


@pytest.mark.night
@pytest.mark.usefixtures("login")
class TestTargeting:
    def test_targeting_create_use_ids_hh(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
        page_targeting_details: TargetingDetails,
        page_targeting_create: TargetingCreate,
    ) -> None:
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        page_targeting.get_button_create_new().click()
        assert "New Target Population" in page_targeting_create.get_page_header_title().text
        assert "SAVE" in page_targeting_create.get_button_target_population_create().text
        page_targeting_create.get_filters_program_cycle_autocomplete().click()
        page_targeting_create.select_listbox_element("First Cycle In Programme")
        page_targeting_create.get_div_target_population_add_criteria().click()
        page_targeting_create.get_input_household_ids().click()
        page_targeting_create.get_input_household_ids().send_keys(household_with_disability.unicef_id)
        page_targeting_create.get_targeting_criteria_add_dialog_save_button().click()
        page_targeting_create.get_no_validation_fsp_accept().click()
        page_targeting_create.get_input_name().send_keys(f"Target Population for {household_with_disability.unicef_id}")
        page_targeting_create.click_button_target_population_create()
        target_population = PaymentPlan.objects.get(name__startswith="Target Population for")
        assert (
            str(target_population.total_individuals_count)
            == page_targeting_details.get_label_targeted_individuals().text
        )
        assert (
            str(target_population.total_households_count)
            == page_targeting_details.get_label_total_number_of_households().text
        )
        assert str(target_population.status) == "TP_OPEN"
        assert "OPEN" in page_targeting_details.get_label_status().text

    @pytest.mark.xfail(reason="Problem with deadlock during test - 202318")
    def test_targeting_create_use_ids_individual(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
        page_targeting_details: TargetingDetails,
        page_targeting_create: TargetingCreate,
    ) -> None:
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        page_targeting.get_button_create_new().click()
        assert "New Target Population" in page_targeting_create.get_page_header_title().text
        assert "SAVE" in page_targeting_create.get_button_target_population_create().text
        page_targeting_create.get_filters_program_cycle_autocomplete().click()
        page_targeting_create.select_listbox_element("First Cycle In Programme")
        page_targeting_create.get_input_individual_ids().send_keys("IND-88-0000.0002")
        page_targeting_create.get_input_name().send_keys("Target Population for IND-88-0000.0002")
        page_targeting_create.click_button_target_population_create()
        target_population = PaymentPlan.objects.get(name="Target Population for IND-88-0000.0002")
        assert (
            "4"
            == str(target_population.total_individuals_count)
            == page_targeting_details.get_label_targeted_individuals().text
        )
        assert (
            str(target_population.total_households_count)
            == page_targeting_details.get_label_total_number_of_households().text
        )
        assert str(target_population.status) in page_targeting_details.get_label_status().text
        page_targeting_details.get_button_rebuild().click()

    @pytest.mark.xfail(reason="Problem with deadlock during test - 202318")
    def test_targeting_rebuild(
        self,
        create_programs: None,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
        page_targeting_details: TargetingDetails,
        page_targeting_create: TargetingCreate,
    ) -> None:
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        page_targeting.choose_target_populations(0).click()
        page_targeting_details.get_label_status()
        page_targeting_details.get_button_rebuild().click()
        page_targeting_details.get_status_container()
        page_targeting_details.disappear_status_container()

    def test_targeting_mark_ready(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
        filters: Filters,
        page_targeting_details: TargetingDetails,
        page_targeting_create: TargetingCreate,
    ) -> None:
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        # filters.selectFiltersSatus("TP_OPEN")
        page_targeting.choose_target_populations(0).click()
        page_targeting_details.get_label_status()
        page_targeting_details.get_lock_button().click()
        page_targeting_details.get_lock_popup_button().click()
        page_targeting_details.wait_for_label_status("LOCKED")
        page_targeting_details.screenshot("targeting_locked.png")
        page_targeting_details.get_button_mark_ready().click()
        page_targeting_details.screenshot("targeting_lockedgetButtonMarkReady.png")
        page_targeting_details.get_button_popup_mark_ready().click()
        page_targeting_details.wait_for_label_status("READY FOR PAYMENT MODULE")

    @pytest.mark.xfail(reason="Problem with deadlock during test - 202318")
    def test_copy_targeting(
        self,
        create_programs: None,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
        page_targeting_details: TargetingDetails,
        page_targeting_create: TargetingCreate,
    ) -> None:
        program = Program.objects.get(name="Test Programm")
        page_targeting.select_global_program_filter(program.name)
        page_targeting.get_nav_targeting().click()
        page_targeting.choose_target_populations(0).click()
        page_targeting_details.get_button_target_population_duplicate().click()
        page_targeting_create.get_filters_program_cycle_autocomplete().click()
        page_targeting_create.select_listbox_element("First Cycle In Programme")
        page_targeting_details.get_input_name().send_keys("a1!")
        page_targeting_details.get_elements(page_targeting_details.buttonTargetPopulationDuplicate)[1].click()
        page_targeting_details.disappear_input_name()
        assert "a1!" in page_targeting_details.get_title_page().text
        assert "OPEN" in page_targeting_details.get_target_population_status().text
        assert "PROGRAMME" in page_targeting_details.get_labelized_field_container_program_name().text
        assert "Test Programm" in page_targeting_details.get_label_programme().text
        assert "2" in page_targeting_details.get_label_total_number_of_households().text
        assert "8" in page_targeting_details.get_label_targeted_individuals().text

    @pytest.mark.xfail(reason="Problem with select_listbox_element or getButtonIconEdit")
    def test_edit_targeting(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
        page_targeting_details: TargetingDetails,
        page_targeting_create: TargetingCreate,
    ) -> None:
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        page_targeting.choose_target_populations(0).click()
        page_targeting_details.get_button_edit().click()
        page_targeting_details.get_button_icon_edit().click()
        page_targeting_create.get_button_household_rule().send_keys(Keys.TAB)
        page_targeting_create.get_button_household_rule().send_keys(Keys.TAB)
        page_targeting_create.get_button_household_rule().send_keys(Keys.SPACE)
        # page_targeting_create.getButtonHouseholdRule().click()
        page_targeting_create.get_autocomplete_target_criteria_option().click()
        page_targeting_create.select_listbox_element("What is the Household size?")
        # page_targeting_create.get_targeting_criteria_auto_complete().send_keys("What is the Household size")
        # page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ARROW_DOWN)
        # page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ENTER)
        page_targeting_details.get_household_size_from().send_keys("0")
        page_targeting_details.get_household_size_to().send_keys("9")
        page_targeting_create.get_targeting_criteria_auto_complete().send_keys(Keys.ENTER)
        # page_targeting_create.get_targeting_criteria_add_dialog_save_button().click()
        page_targeting_details.clear_input(page_targeting_details.get_input_name())
        page_targeting_details.get_input_name().send_keys("New Test Data")
        page_targeting_details.get_input_name().send_keys(Keys.ENTER)
        # page_targeting_create.get_button_save().click()
        page_targeting_details.get_button_edit()
        assert page_targeting_details.wait_for_text_title_page("New Test Data")
        assert "9" in page_targeting_details.get_criteria_container().text

    def test_delete_targeting(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
        page_targeting_details: TargetingDetails,
    ) -> None:
        PaymentPlanFactory(
            program_cycle=ProgramCycle.objects.get(program__name="Test Programm"),
            name="Copy TP",
            status=PaymentPlan.Status.TP_OPEN,
        )
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        page_targeting.disappear_loading_rows()
        old_list = page_targeting.get_target_populations_rows()
        assert len(old_list) == 2
        assert "Copy TP" in old_list[0].text

        page_targeting.choose_target_populations(0).click()
        page_targeting_details.get_button_delete().click()
        page_targeting_details.get_dialog_box()
        page_targeting_details.get_elements(page_targeting_details.button_delete)[1].click()
        page_targeting.get_nav_targeting().click()
        page_targeting.disappear_loading_rows()
        new_list = page_targeting.get_target_populations_rows()
        assert len(new_list) == 1
        assert create_targeting.name in new_list[0].text

    @pytest.mark.xfail(reason="Problem with deadlock during test - 202318")
    def test_targeting_different_program_statuses(
        self,
        create_programs: None,
        page_targeting: Targeting,
        page_targeting_details: TargetingDetails,
        page_targeting_create: TargetingCreate,
    ) -> None:
        program = Program.objects.get(name="Test Programm")
        program.status = Program.DRAFT
        program.save()
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        page_targeting.mouse_on_element(page_targeting.get_button_inactive_create_new())
        assert "Program has to be active to create a new Target Population" in page_targeting.get_tooltip().text
        program.status = Program.ACTIVE
        program.save()
        page_targeting.driver.refresh()
        page_targeting.get_button_create_new()
        program.status = Program.FINISHED
        program.save()
        page_targeting.driver.refresh()
        page_targeting.mouse_on_element(page_targeting.get_button_inactive_create_new())
        assert "Program has to be active to create a new Target Population" in page_targeting.get_tooltip().text

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
    def test_exclude_households_with_active_adjudication_ticket(
        self,
        test_data: dict,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
        page_targeting_details: TargetingDetails,
        page_targeting_create: TargetingCreate,
    ) -> None:
        program = Program.objects.get(name="Test Programm")
        program.data_collecting_type.type = test_data["type"]
        program.data_collecting_type.save()
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        page_targeting.get_button_create_new().click()
        page_targeting_create.get_filters_program_cycle_autocomplete().click()
        page_targeting_create.select_listbox_element("First Cycle In Programme")
        page_targeting_create.get_div_target_population_add_criteria().click()
        page_targeting_create.get_input_household_ids().click()
        page_targeting_create.get_input_household_ids().send_keys(household_with_disability.unicef_id)
        page_targeting_create.get_targeting_criteria_add_dialog_save_button().click()
        page_targeting_create.get_no_validation_fsp_accept().click()
        page_targeting_create.get_input_name().send_keys(f"Test {household_with_disability.unicef_id}")
        page_targeting_create.get_input_flag_exclude_if_active_adjudication_ticket().click()
        page_targeting_create.click_button_target_population_create()
        with pytest.raises(NoSuchElementException):
            page_targeting_details.get_checkbox_exclude_if_on_sanction_list().find_element(
                By.CSS_SELECTOR, page_targeting_details.icon_selected
            )
        if test_data["type"] == "SOCIAL":
            page_targeting_details.get_checkbox_exclude_people_if_active_adjudication_ticket()
            page_targeting_details.get_checkbox_exclude_people_if_active_adjudication_ticket().find_element(
                By.CSS_SELECTOR, page_targeting_details.icon_selected
            )
            assert (
                test_data["text"]
                in page_targeting_details.get_checkbox_exclude_people_if_active_adjudication_ticket()
                .find_element(By.XPATH, "./..")
                .text
            )
        elif test_data["type"] == "STANDARD":
            page_targeting_details.get_checkbox_exclude_if_active_adjudication_ticket()
            page_targeting_details.get_checkbox_exclude_if_active_adjudication_ticket().find_element(
                By.CSS_SELECTOR, page_targeting_details.icon_selected
            )
            assert (
                test_data["text"]
                in page_targeting_details.get_checkbox_exclude_if_active_adjudication_ticket()
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
        page_targeting: Targeting,
        page_targeting_details: TargetingDetails,
        page_targeting_create: TargetingCreate,
    ) -> None:
        program = Program.objects.get(name="Test Programm")
        program.data_collecting_type.type = test_data["type"]
        program.data_collecting_type.save()
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        page_targeting.get_button_create_new().click()
        page_targeting_create.get_filters_program_cycle_autocomplete().click()
        page_targeting_create.select_listbox_element("First Cycle In Programme")
        page_targeting_create.get_input_household_ids().click()
        page_targeting_create.get_input_household_ids().send_keys(household_with_disability.unicef_id)
        page_targeting_create.get_input_name().send_keys(f"Test {household_with_disability.unicef_id}")
        page_targeting_create.get_input_flag_exclude_if_on_sanction_list().click()
        page_targeting_create.click_button_target_population_create()
        page_targeting_details.get_checkbox_exclude_if_on_sanction_list()
        # ToDo: Add after merge to develop
        # assert (
        #     test_data["text"]
        #     in page_targeting_details.get_checkbox_exclude_if_on_sanction_list().find_element(By.XPATH, "./..").text
        # )
        page_targeting_details.get_checkbox_exclude_if_on_sanction_list().find_element(
            By.CSS_SELECTOR, page_targeting_details.icon_selected
        )
        with pytest.raises(NoSuchElementException):
            page_targeting_details.get_checkbox_exclude_people_if_active_adjudication_ticket().find_element(
                By.CSS_SELECTOR, page_targeting_details.icon_selected
            )

    def test_targeting_info_button(
        self,
        create_programs: None,
        page_targeting: Targeting,
    ) -> None:
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        page_targeting.get_button_target_population().click()
        page_targeting.get_tab_field_list()
        page_targeting.get_tab_targeting_diagram().click()

    def test_targeting_filters(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
        filters: Filters,
    ) -> None:
        PaymentPlanFactory(
            program_cycle=ProgramCycle.objects.get(program__name="Test Programm"),
            name="Copy TP",
            status=PaymentPlan.Status.TP_PROCESSING,
        )
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        filters.get_filters_search().send_keys("Copy")
        filters.get_button_filters_apply().click()
        page_targeting.count_target_populations(1)
        assert "PROCESSING" in page_targeting.get_status_container().text
        filters.get_button_filters_clear().click()
        filters.get_filters_status().click()
        filters.select_listbox_element("Open")
        filters.get_button_filters_apply().click()
        page_targeting.count_target_populations(1)
        assert "OPEN" in page_targeting.get_status_container().text
        filters.get_button_filters_clear().click()
        filters.get_filters_total_households_count_min().send_keys("10")
        filters.get_filters_total_households_count_max().send_keys("10")
        filters.get_button_filters_apply().click()
        page_targeting.count_target_populations(0)
        filters.get_button_filters_clear().click()
        filters.get_filters_total_households_count_min().send_keys("1")
        filters.get_filters_total_households_count_max().send_keys("3")
        page_targeting.count_target_populations(2)
        filters.get_button_filters_clear().click()

    def test_targeting_and_labels(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
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
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        page_targeting.get_column_name().click()
        page_targeting.disappear_loading_rows()
        assert "A Copy TP" in page_targeting.choose_target_populations(0).text
        page_targeting.get_column_name().click()
        page_targeting.disappear_loading_rows()
        assert "Test Target Population" in page_targeting.choose_target_populations(0).text
        page_targeting.get_column_status().click()
        page_targeting.disappear_loading_rows()
        assert "A Copy TP" in page_targeting.choose_target_populations(0).text
        page_targeting.get_column_status().click()
        page_targeting.disappear_loading_rows()
        assert "Test Target Population" in page_targeting.choose_target_populations(0).text
        page_targeting.get_column_num_of_households().click()
        page_targeting.disappear_loading_rows()
        assert "A Copy TP" in page_targeting.choose_target_populations(0).text
        page_targeting.get_column_date_created().click()
        page_targeting.disappear_loading_rows()
        assert "Test Target Population" in page_targeting.choose_target_populations(0).text
        page_targeting.get_column_date_created().click()
        page_targeting.disappear_loading_rows()
        assert "A Copy TP" in page_targeting.choose_target_populations(0).text
        page_targeting.get_column_last_edited().click()
        page_targeting.disappear_loading_rows()
        assert "Test Target Population" in page_targeting.choose_target_populations(0).text
        page_targeting.get_column_last_edited().click()
        page_targeting.disappear_loading_rows()
        assert "A Copy TP" in page_targeting.choose_target_populations(0).text
        page_targeting.get_column_created_by().click()
        page_targeting.disappear_loading_rows()
        assert "Test Target Population" in page_targeting.choose_target_populations(0).text

    def test_targeting_parametrized_rules_filters(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
        page_targeting_details: TargetingDetails,
        page_targeting_create: TargetingCreate,
    ) -> None:
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        page_targeting.get_button_create_new().click()
        assert "New Target Population" in page_targeting_create.get_title_page().text
        page_targeting_create.get_filters_program_cycle_autocomplete().click()
        page_targeting_create.select_listbox_element("First Cycle In Programme")
        page_targeting_create.get_add_criteria_button().click()
        page_targeting_create.get_add_people_rule_button().click()
        page_targeting_create.get_targeting_criteria_auto_complete().click()
        page_targeting_create.select_listbox_element("Females Age 0 - 5")
        page_targeting_create.get_input_filters_value_from(0).send_keys("0")
        page_targeting_create.get_input_filters_value_to(0).send_keys("1")
        page_targeting_create.get_input_filters_value_to(0).send_keys("1")
        page_targeting_create.get_button_target_population_add_criteria().click()
        page_targeting_create.get_no_validation_fsp_accept().click()
        page_targeting_create.get_input_name().send_keys("Target Population for Females Age 0 - 5")
        page_targeting_create.get_input_flag_exclude_if_active_adjudication_ticket().click()
        page_targeting_create.click_button_target_population_create()
        assert "Females Age 0 - 5: 11" in page_targeting_create.get_criteria_container().text

    @pytest.mark.xfail(reason="Problem with deadlock during test - 202318")
    def test_targeting_parametrized_rules_filters_and_or(
        self,
        create_programs: None,
        household_with_disability: Household,
        create_targeting: PaymentPlan,
        page_targeting: Targeting,
        page_targeting_details: TargetingDetails,
        page_targeting_create: TargetingCreate,
    ) -> None:
        page_targeting.select_global_program_filter("Test Programm")
        page_targeting.get_nav_targeting().click()
        page_targeting.get_button_create_new().click()
        assert "New Target Population" in page_targeting_create.get_title_page().text
        page_targeting_create.get_filters_program_cycle_autocomplete().click()
        page_targeting_create.select_listbox_element("First Cycle In Programme")
        page_targeting_create.get_add_criteria_button().click()
        page_targeting_create.get_add_people_rule_button().click()
        page_targeting_create.get_targeting_criteria_auto_complete().click()
        page_targeting_create.select_listbox_element("Females Age 0 - 5")
        page_targeting_create.get_input_filters_value_from(0).send_keys("0")
        page_targeting_create.get_input_filters_value_to(0).send_keys("1")
        page_targeting_create.get_button_household_rule().click()
        page_targeting_create.get_targeting_criteria_auto_complete(1).click()
        page_targeting_create.select_listbox_element("Village")
        page_targeting_create.get_input_filters_value(1).send_keys("Testtown")
        page_targeting_create.get_button_individual_rule().click()
        page_targeting_create.get_targeting_criteria_auto_complete_individual().click()
        page_targeting_create.select_listbox_element("Does the Individual have disability?")
        page_targeting_create.get_select_many().click()
        page_targeting_create.select_multiple_option_by_name(HEARING, SEEING)
        page_targeting_create.get_targeting_criteria_add_dialog_save_button().click()
        assert "Females Age 0 - 5: 1" in page_targeting_create.get_criteria_container().text
        assert "Village: Testtown" in page_targeting_create.get_criteria_container().text
        assert (
            "Does the Individual have disability?: Difficulty hearing (even if using a hearing aid), Difficulty seeing (even if wearing glasses)"
            in page_targeting_create.get_criteria_container().text
        )
        page_targeting_create.get_button_edit().click()
        page_targeting_create.get_targeting_criteria_auto_complete_individual()
        page_targeting_create.get_elements(page_targeting_create.targetingCriteriaAddDialogSaveButton)[1].click()
        page_targeting_create.get_input_name().send_keys("Target Population")
        assert "ADD 'OR'FILTER" in page_targeting_create.get_targeting_criteria_add_dialog_save_button().text
        page_targeting_create.get_targeting_criteria_add_dialog_save_button().click()
        page_targeting_create.get_add_household_rule_button().click()
        page_targeting_create.get_targeting_criteria_auto_complete().click()
        page_targeting_create.select_listbox_element("Males age 0 - 5 with disability")
        page_targeting_create.get_input_filters_value_from(0).send_keys("1")
        page_targeting_create.get_input_filters_value_to(0).send_keys("10")
        page_targeting_create.get_elements(page_targeting_create.targetingCriteriaAddDialogSaveButton)[1].click()
        page_targeting_create.get_target_population_save_button().click()
        assert "Females Age 0 - 5: 1" in page_targeting_create.get_criteria_container().text
        assert "Village: Testtown" in page_targeting_create.get_criteria_container().text
        assert (
            "Does the Individual have disability?: Difficulty hearing (even if using a hearing aid), Difficulty seeing (even if wearing glasses)"
            in page_targeting_create.get_criteria_container().text
        )
        assert (
            "Males age 0 - 5 with disability: 1 -10"
            in page_targeting_create.get_elements(page_targeting_create.criteriaContainer)[1].text
        )
