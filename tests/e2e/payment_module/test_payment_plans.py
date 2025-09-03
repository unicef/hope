from datetime import datetime
import os
from time import sleep
import zipfile

from dateutil.relativedelta import relativedelta
import factory
import openpyxl
import pytest
from pytz import utc
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from sorl.thumbnail.conf import settings

from e2e.helpers.date_time_format import FormatTime
from e2e.page_object.payment_module.new_payment_plan import NewPaymentPlan
from e2e.page_object.payment_module.payment_module import PaymentModule
from e2e.page_object.payment_module.payment_module_details import PaymentModuleDetails
from e2e.page_object.payment_module.program_cycle import ProgramCyclePage
from e2e.page_object.payment_module.program_cycle_details import ProgramCycleDetailsPage
from extras.test_utils.factories.core import DataCollectingTypeFactory
from extras.test_utils.factories.household import (
    HouseholdFactory,
    IndividualFactory,
    create_household,
)
from extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PaymentFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.factories.steficon import RuleCommitFactory, RuleFactory
from extras.test_utils.factories.targeting import TargetingCriteriaRuleFactory
from hope.apps.account.models import User
from hope.apps.core.models import DataCollectingType
from hope.apps.payment.models import (
    DeliveryMechanism,
    FinancialServiceProvider,
    PaymentPlan,
)
from hope.apps.program.models import BeneficiaryGroup, Program, ProgramCycle
from hope.apps.steficon.models import Rule

pytestmark = pytest.mark.django_db()


def find_file(
    file_name: str,
    search_in_dir: str = settings.DOWNLOAD_DIRECTORY,
    number_of_ties: int = 1,
) -> str:
    for _ in range(number_of_ties):
        for file in os.listdir(search_in_dir):
            if file_name in file:
                return file
        sleep(1)
    raise Exception(f"{file_name} file did not found in {search_in_dir}")


@pytest.fixture
def create_test_program() -> Program:
    return create_program()


@pytest.fixture
def social_worker_program() -> Program:
    return create_program(dct_type=DataCollectingType.Type.SOCIAL, beneficiary_group_name="People")


def create_program(
    name: str = "Test Program",
    dct_type: str = DataCollectingType.Type.STANDARD,
    beneficiary_group_name: str = "Main Menu",
) -> Program:
    dct = DataCollectingTypeFactory(type=dct_type)
    beneficiary_group = BeneficiaryGroup.objects.filter(name=beneficiary_group_name).first()
    return ProgramFactory(
        name=name,
        programme_code="1234",
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=Program.ACTIVE,
        cycle__title="First cycle for Test Program",
        cycle__status=ProgramCycle.DRAFT,
        cycle__start_date=datetime.now() - relativedelta(days=5),
        cycle__end_date=datetime.now() + relativedelta(days=5),
        beneficiary_group=beneficiary_group,
    )


@pytest.fixture
def create_targeting(create_test_program: Program) -> None:
    generate_delivery_mechanisms()
    dm_cash = DeliveryMechanism.objects.get(code="cash")
    program = create_test_program
    business_area = program.business_area
    program_cycle = program.cycles.first()

    households = [
        create_household(
            household_args={
                "size": 2,
                "business_area": business_area,
                "program": program,
            },
        )[0]
        for _ in range(14)
    ]
    hh_ids_str = ", ".join([hh.unicef_id for hh in households])

    payment_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        status=PaymentPlan.Status.DRAFT,
    )
    TargetingCriteriaRuleFactory(household_ids=hh_ids_str, individual_ids="", payment_plan=payment_plan)
    rule = RuleFactory(
        name="Test Rule",
        type=Rule.TYPE_PAYMENT_PLAN,
        deprecated=False,
        enabled=True,
    )
    rule.allowed_business_areas.add(business_area)
    RuleCommitFactory(rule=rule, version=2)

    fsp_xlsx_template = FinancialServiceProviderXlsxTemplateFactory(name="TestName123")

    fsp_1 = FinancialServiceProviderFactory(
        name="FSP_1",
        vision_vendor_number="149-69-3686",
        distribution_limit=10_000,
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
    )
    fsp_1.delivery_mechanisms.set([dm_cash])
    fsp_1.allowed_business_areas.add(business_area)
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp_1,
        xlsx_template=fsp_xlsx_template,
        delivery_mechanism=dm_cash,
    )


@pytest.fixture
def create_payment_plan(create_targeting: None) -> PaymentPlan:
    pp = PaymentPlan.objects.get(program_cycle__program__name="Test Program")
    program = pp.program_cycle.program
    cycle = ProgramCycleFactory(
        program=program,
        title="Cycle for PaymentPlan",
        status=ProgramCycle.ACTIVE,
        start_date=datetime.now() + relativedelta(days=10),
        end_date=datetime.now() + relativedelta(days=15),
    )
    dm_cash = DeliveryMechanism.objects.get(code="cash")
    fsp = FinancialServiceProviderFactory()
    fsp.delivery_mechanisms.set([dm_cash])
    payment_plan, _ = PaymentPlan.objects.update_or_create(
        name="Test Payment Plan",
        business_area=program.business_area,
        program_cycle=cycle,
        currency="USD",
        dispersion_start_date=datetime.now() + relativedelta(days=10),
        dispersion_end_date=datetime.now() + relativedelta(days=15),
        status_date=datetime.now(),
        status=PaymentPlan.Status.ACCEPTED,
        created_by=User.objects.first(),
        total_delivered_quantity=999,
        total_entitled_quantity=2999,
        is_follow_up=False,
        financial_service_provider=fsp,
        delivery_mechanism=dm_cash,
    )
    return payment_plan


@pytest.fixture
def create_payment_plan_lock(create_test_program: Program) -> PaymentPlan:
    return payment_plan_create(create_test_program)


@pytest.fixture
def create_payment_plan_lock_social_worker(
    social_worker_program: Program,
) -> PaymentPlan:
    return payment_plan_create(social_worker_program)


@pytest.fixture
def create_payment_plan_open(social_worker_program: Program) -> PaymentPlan:
    generate_delivery_mechanisms()
    dm_cash = DeliveryMechanism.objects.get(code="cash")
    fsp = FinancialServiceProviderFactory()
    fsp.delivery_mechanisms.set([dm_cash])

    program_cycle = ProgramCycleFactory(
        program=social_worker_program,
        title="Cycle for PaymentPlan",
        status=ProgramCycle.ACTIVE,
        start_date=datetime.now() + relativedelta(days=10),
        end_date=datetime.now() + relativedelta(days=15),
    )

    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.DRAFT,
        is_follow_up=False,
        program_cycle=program_cycle,
        business_area=social_worker_program.business_area,
        dispersion_start_date=datetime.now().date(),
        financial_service_provider=fsp,
        delivery_mechanism=dm_cash,
    )
    hoh1 = IndividualFactory(household=None)
    household_1 = HouseholdFactory(
        id="3d7087be-e8f8-478d-9ca2-4ca6d5e96f51",
        unicef_id="HH-17-0000.3340",
        head_of_household=hoh1,
        size=2,
    )
    IndividualFactory(
        household=household_1,
        program=social_worker_program,
        sex="MALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=11, maximum_age=16),
    )
    PaymentFactory(parent=payment_plan, household=household_1, excluded=False, currency="PLN")

    payment_plan.update_population_count_fields()
    payment_plan.update_money_fields()

    payment_plan.status_open()
    payment_plan.save(update_fields=("status",))

    PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        program_cycle=program_cycle,
        business_area=social_worker_program.business_area,
        dispersion_start_date=datetime.now().date(),
        is_follow_up=True,
        source_payment_plan=payment_plan,
        financial_service_provider=fsp,
        delivery_mechanism=dm_cash,
    )

    return payment_plan


def payment_plan_create(program: Program, status: str = PaymentPlan.Status.LOCKED) -> PaymentPlan:
    generate_delivery_mechanisms()
    program_cycle = ProgramCycleFactory(
        program=program,
        title="Cycle for PaymentPlan",
        status=ProgramCycle.ACTIVE,
        start_date=datetime.now() + relativedelta(days=10),
        end_date=datetime.now() + relativedelta(days=15),
    )
    dm_cash = DeliveryMechanism.objects.get(code="cash")
    fsp = FinancialServiceProviderFactory()
    fsp.delivery_mechanisms.set([dm_cash])
    payment_plan = PaymentPlanFactory(
        is_follow_up=False,
        status=status,
        program_cycle=program_cycle,
        dispersion_start_date=datetime.now().date(),
        financial_service_provider=fsp,
        delivery_mechanism=dm_cash,
    )
    hoh1 = IndividualFactory(household=None)
    hoh2 = IndividualFactory(household=None)
    household_1 = HouseholdFactory(
        id="3d7087be-e8f8-478d-9ca2-4ca6d5e96f51",
        unicef_id="HH-17-0000.3340",
        head_of_household=hoh1,
        size=2,
    )
    household_2 = HouseholdFactory(
        id="3d7087be-e8f8-478d-9ca2-4ca6d5e96f52",
        unicef_id="HH-17-0000.3341",
        head_of_household=hoh2,
        size=3,
    )

    # HH1 - Female Children: 1; Female Adults: 1; Male Children: 2; Male Adults: 1;
    IndividualFactory(
        household=household_1,
        program=program,
        sex="MALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=11, maximum_age=16),
    )
    IndividualFactory(
        household=household_1,
        program=program,
        sex="MALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=11, maximum_age=16),
    )
    IndividualFactory(
        household=household_1,
        program=program,
        sex="FEMALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=1, maximum_age=10),
    )
    IndividualFactory(
        household=household_1,
        program=program,
        sex="FEMALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=20, maximum_age=40),
    )
    IndividualFactory(
        household=household_1,
        program=program,
        sex="MALE",
        unicef_id="IND-06-0001.1828",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=20, maximum_age=40),
    )

    # HH2 - Female Children: 4; Female Adults: 1; Male Children: 1; Male Adults: 0;
    IndividualFactory(
        household=household_2,
        program=program,
        sex="MALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=1, maximum_age=3),
    )
    IndividualFactory(
        household=household_2,
        program=program,
        sex="FEMALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=1, maximum_age=10),
    )
    IndividualFactory(
        household=household_2,
        program=program,
        sex="FEMALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=1, maximum_age=10),
    )
    IndividualFactory(
        household=household_2,
        program=program,
        sex="FEMALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=1, maximum_age=10),
    )
    IndividualFactory(
        household=household_2,
        program=program,
        sex="FEMALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=1, maximum_age=10),
    )
    IndividualFactory(
        household=household_2,
        program=program,
        sex="FEMALE",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=30, maximum_age=45),
    )

    PaymentFactory(parent=payment_plan, household=household_1, excluded=False, currency="PLN")
    PaymentFactory(parent=payment_plan, household=household_2, excluded=False, currency="PLN")

    payment_plan.update_population_count_fields()
    payment_plan.update_money_fields()

    return payment_plan


@pytest.mark.usefixtures("login")
class TestSmokePaymentModule:
    def test_smoke_payment_plan(self, create_payment_plan: PaymentPlan, page_payment_module: PaymentModule) -> None:
        page_payment_module.select_global_program_filter("Test Program")
        page_payment_module.get_nav_payment_module().click()
        page_payment_module.get_nav_payment_plans().click()
        assert "Payment Module" in page_payment_module.get_page_header_title().text
        assert "Status" in page_payment_module.get_select_filter().text
        assert "" in page_payment_module.get_filters_total_entitled_quantity_from().text
        assert "" in page_payment_module.get_filters_total_entitled_quantity_to().text
        assert "" in page_payment_module.get_date_picker_filter_from().text
        assert "" in page_payment_module.get_date_picker_filter_to().text
        assert "CLEAR" in page_payment_module.get_button_filters_clear().text
        assert "APPLY" in page_payment_module.get_button_filters_apply().text
        assert "Payment Plans" in page_payment_module.get_table_title().text
        assert "Payment Plan ID" in page_payment_module.get_table_label()[0].text
        assert "Status" in page_payment_module.get_table_label()[1].text
        assert "Target Population" in page_payment_module.get_table_label()[2].text
        assert "Num. of Items Groups" in page_payment_module.get_table_label()[3].text
        assert "Currency" in page_payment_module.get_table_label()[4].text
        assert "Total Entitled Quantity" in page_payment_module.get_table_label()[5].text
        assert "Total Delivered Quantity" in page_payment_module.get_table_label()[6].text
        assert "Total Undelivered Quantity" in page_payment_module.get_table_label()[7].text
        assert "Dispersion Start Date" in page_payment_module.get_table_label()[8].text
        assert "Dispersion End Date" in page_payment_module.get_table_label()[9].text
        assert "Follow-up Payment Plans" in page_payment_module.get_table_label()[10].text
        assert "ACCEPTED" in page_payment_module.get_status_container().text
        assert "Rows per page: 5 1–1 of 1" in page_payment_module.get_table_pagination().text.replace("\n", " ")

    def test_smoke_new_payment_plan(
        self,
        create_test_program: Program,
        page_payment_module: PaymentModule,
        page_program_cycle: ProgramCyclePage,
        page_program_cycle_details: ProgramCycleDetailsPage,
        page_new_payment_plan: NewPaymentPlan,
    ) -> None:
        page_payment_module.select_global_program_filter("Test Program")
        page_payment_module.get_nav_payment_module().click()
        page_program_cycle.get_nav_programme_cycles().click()
        page_program_cycle.get_program_cycle_row()[0].find_element(
            By.CSS_SELECTOR, 'td[data-cy="program-cycle-title"]'
        ).find_element(By.TAG_NAME, "a").click()
        page_program_cycle_details.get_button_create_payment_plan().click()
        assert "New Payment Plan" in page_new_payment_plan.get_page_header_title().text
        assert "SAVE" in page_new_payment_plan.get_button_save_payment_plan().text
        assert "Target Population" in page_new_payment_plan.get_input_target_population().text
        assert "Currency" in page_new_payment_plan.get_input_currency().text
        assert (
            "Dispersion Start Date*"
            in page_new_payment_plan.wait_for(page_new_payment_plan.input_dispersion_start_date).text
        )
        assert (
            "Dispersion End Date*"
            in page_new_payment_plan.wait_for(page_new_payment_plan.input_dispersion_end_date).text
        )

    def test_smoke_details_payment_plan(
        self,
        create_payment_plan: PaymentPlan,
        page_payment_module: PaymentModule,
        page_payment_module_details: PaymentModuleDetails,
    ) -> None:
        page_payment_module.select_global_program_filter("Test Program")
        page_payment_module.get_nav_payment_module().click()
        page_payment_module.get_nav_payment_plans().click()
        page_payment_module.get_row(0).click()
        assert "ACCEPTED" in page_payment_module_details.get_status_container().text
        assert "EXPORT XLSX" in page_payment_module_details.get_button_export_xlsx().text
        assert "USD" in page_payment_module_details.get_label_currency().text
        assert (
            str((datetime.now() + relativedelta(days=10)).strftime("%-d %b %Y"))
            in page_payment_module_details.get_label_dispersion_start_date().text
        )
        assert (
            str((datetime.now() + relativedelta(days=15)).strftime("%-d %b %Y"))
            in page_payment_module_details.get_label_dispersion_end_date().text
        )
        assert "-" in page_payment_module_details.get_label_related_follow_up_payment_plans().text
        assert "CREATE" in page_payment_module_details.get_button_create_exclusions().text
        assert "Supporting Documents" in page_payment_module_details.get_supporting_documents_title().text
        assert "No documents uploaded" in page_payment_module_details.get_supporting_documents_empty().text
        assert "0" in page_payment_module_details.get_label_female_children().text
        assert "0" in page_payment_module_details.get_label_female_adults().text
        assert "0" in page_payment_module_details.get_label_male_children().text
        assert "0" in page_payment_module_details.get_label_male_adults().text
        assert "" in page_payment_module_details.get_chart_container().text
        assert "0" in page_payment_module_details.get_label_total_number_of_households().text
        assert "0" in page_payment_module_details.get_label_targeted_individuals().text
        assert "Payee List" in page_payment_module_details.get_table_title().text
        assert "UPLOAD RECONCILIATION INFO" in page_payment_module_details.get_button_import().text
        assert "Payment ID" in page_payment_module_details.get_table_label()[1].text
        assert "Items Group ID" in page_payment_module_details.get_table_label()[2].text
        assert "Items Group Size" in page_payment_module_details.get_table_label()[3].text
        assert "Administrative Level 2" in page_payment_module_details.get_table_label()[4].text
        assert "Collector" in page_payment_module_details.get_table_label()[5].text
        assert "FSP" in page_payment_module_details.get_table_label()[6].text
        assert "Entitlement" in page_payment_module_details.get_table_label()[7].text
        assert "Delivered Quantity" in page_payment_module_details.get_table_label()[8].text
        assert "Status" in page_payment_module_details.get_table_label()[9].text
        assert "FSP Auth Code" in page_payment_module_details.get_table_label()[10].text
        assert "Reconciliation" in page_payment_module_details.get_table_label()[11].text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_payment_plan_happy_path(
        self,
        clear_downloaded_files: None,
        create_targeting: None,
        page_payment_module: PaymentModule,
        page_payment_module_details: PaymentModuleDetails,
        page_new_payment_plan: NewPaymentPlan,
        page_program_cycle: ProgramCyclePage,
        page_program_cycle_details: ProgramCycleDetailsPage,
        download_path: str,
    ) -> None:
        payment_plan = PaymentPlan.objects.first()
        page_program_cycle.select_global_program_filter("Test Program")
        page_program_cycle.get_nav_payment_module().click()
        page_program_cycle.get_nav_programme_cycles().click()
        assert (
            "Draft"
            in page_program_cycle.get_program_cycle_row()[0]
            .find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-status"]')
            .text
        )
        page_program_cycle.get_program_cycle_row()[0].find_element(
            By.CSS_SELECTOR, 'td[data-cy="program-cycle-title"]'
        ).find_element(By.TAG_NAME, "a").click()
        page_program_cycle_details.get_button_create_payment_plan().click()
        page_new_payment_plan.get_input_target_population().click()
        page_new_payment_plan.select_listbox_element(payment_plan.name)
        page_new_payment_plan.get_input_currency().click()
        page_new_payment_plan.select_listbox_element("Czech koruna")
        page_new_payment_plan.get_input_dispersion_start_date().click()
        page_new_payment_plan.get_input_dispersion_start_date().send_keys(
            FormatTime(22, 1, 2024).numerically_formatted_date
        )
        page_new_payment_plan.get_input_dispersion_end_date().click()
        page_new_payment_plan.get_input_dispersion_end_date().send_keys(
            FormatTime(30, 6, 2030).numerically_formatted_date
        )
        page_new_payment_plan.get_input_currency().click()
        page_new_payment_plan.get_button_save_payment_plan().click()
        assert "OPEN" in page_payment_module_details.get_status_container().text
        assert "CZK" in page_payment_module_details.get_label_currency().text
        assert (
            FormatTime(22, 1, 2024).date_in_text_format
            in page_payment_module_details.get_label_dispersion_start_date().text
        )
        assert (
            FormatTime(30, 6, 2030).date_in_text_format
            in page_payment_module_details.get_label_dispersion_end_date().text
        )
        page_payment_module_details.get_button_lock_plan().click()
        page_payment_module_details.get_button_submit().click()
        page_payment_module_details.get_input_entitlement_formula().click()
        page_payment_module_details.select_listbox_element("Test Rule")
        page_payment_module_details.get_button_apply_steficon().click()
        page_payment_module_details.check_status("LOCKED")
        page_payment_module_details.click_button_lock_plan()
        page_payment_module_details.get_button_submit().click()
        page_payment_module_details.check_alert("Payment Plan FSPs are locked.")
        page_payment_module_details.check_status("LOCKED FSP")
        page_payment_module_details.click_button_send_for_approval()
        page_payment_module_details.check_alert("Payment Plan has been sent for approval.")
        page_payment_module_details.check_status("IN APPROVAL")
        page_payment_module_details.click_button_approve()
        page_payment_module_details.get_button_submit().click()
        page_payment_module_details.check_alert("Payment Plan has been approved.")
        page_payment_module_details.check_status("IN AUTHORIZATION")
        page_payment_module_details.click_button_authorize()
        page_payment_module_details.get_button_submit().click()
        page_payment_module_details.check_alert("Payment Plan has been authorized")
        page_payment_module_details.check_status("IN REVIEW")
        page_payment_module_details.click_button_mark_as_released()
        page_payment_module_details.get_button_submit().click()
        page_payment_module_details.check_alert("Payment Plan has been marked as reviewed.")
        page_payment_module_details.check_status("ACCEPTED")
        page_payment_module_details.click_button_export_xlsx()
        page_payment_module_details.check_alert("Exporting XLSX started")

        # ToDo: Refresh is workaround. Works on dev properly.
        page_payment_module.driver.refresh()
        page_payment_module_details.get_button_download_xlsx().click()

        zip_file = find_file(".zip", number_of_ties=15, search_in_dir=download_path)
        with zipfile.ZipFile(os.path.join(download_path, zip_file), "r") as zip_ref:
            zip_ref.extractall(download_path)

        xlsx_file = find_file(".xlsx", search_in_dir=download_path)
        wb1 = openpyxl.load_workbook(os.path.join(download_path, xlsx_file))
        ws1 = wb1.active
        for cell in ws1["N:N"]:
            if cell.row >= 2:
                ws1.cell(row=cell.row, column=16, value=cell.value)

        wb1.save(os.path.join(download_path, xlsx_file))

        page_payment_module_details.get_button_upload_reconciliation_info().click()
        page_payment_module_details.upload_file(os.path.abspath(os.path.join(download_path, xlsx_file)), timeout=120)
        page_payment_module_details.get_button_import_submit().click()
        page_payment_module_details.check_status("FINISHED")
        assert "14 (100%)" in page_payment_module_details.get_label_reconciled().text
        assert "18.2 CZK (0.7 USD)" in page_payment_module_details.get_label_total_entitled_quantity().text
        page_payment_module.get_nav_payment_module().click()
        page_payment_module.get_nav_programme_cycles().click()
        assert (
            "Active"
            in page_program_cycle.get_program_cycle_row()[0]
            .find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-status"]')
            .text
        )


@pytest.mark.usefixtures("login")
class TestPaymentPlans:
    def test_payment_plan_edit(
        self,
        clear_downloaded_files: None,
        create_targeting: None,
        page_payment_module: PaymentModule,
        page_payment_module_details: PaymentModuleDetails,
        page_new_payment_plan: NewPaymentPlan,
        page_program_cycle: ProgramCyclePage,
        page_program_cycle_details: ProgramCycleDetailsPage,
    ) -> None:
        page_program_cycle.select_global_program_filter("Test Program")
        page_program_cycle.get_nav_payment_module().click()

    def test_payment_plan_exclude_not_lock_error(
        self,
        create_payment_plan: PaymentPlan,
        page_payment_module: PaymentModule,
        page_payment_module_details: PaymentModuleDetails,
        page_new_payment_plan: NewPaymentPlan,
        page_program_cycle: ProgramCyclePage,
        page_program_cycle_details: ProgramCycleDetailsPage,
    ) -> None:
        page_payment_module.select_global_program_filter("Test Program")
        page_payment_module.get_nav_payment_module().click()
        page_payment_module.get_nav_payment_plans().click()
        page_payment_module.get_row(0).click()
        page_payment_module_details.get_button_create_exclusions().click()
        with pytest.raises(ElementClickInterceptedException):
            page_payment_module_details.get_button_save_exclusions().click()

    def test_payment_plan_save_exclude_people(
        self,
        create_payment_plan_lock_social_worker: PaymentPlan,
        page_payment_module: PaymentModule,
        page_payment_module_details: PaymentModuleDetails,
    ) -> None:
        page_payment_module.select_global_program_filter("Test Program")
        page_payment_module.get_nav_payment_module().click()
        page_payment_module.get_nav_payment_plans().click()
        page_payment_module.get_row(0).click()
        page_payment_module_details.get_button_create_exclusions()
        page_payment_module_details.get_label_total_number_of_people()
        assert "5" in page_payment_module_details.get_label_female_children().text
        assert "2" in page_payment_module_details.get_label_female_adults().text
        assert "3" in page_payment_module_details.get_label_male_children().text
        assert "1" in page_payment_module_details.get_label_male_adults().text
        assert "11" in page_payment_module_details.get_label_total_number_of_people().text
        page_payment_module_details.get_button_create_exclusions().click()
        page_payment_module_details.get_input_exclusion_reason().send_keys("Reason e2e Test")
        page_payment_module_details.get_input_beneficiaries_ids()
        page_payment_module_details.get_input_beneficiaries_ids().find_element(By.TAG_NAME, "input").send_keys(
            "IND-06-0001.1828"
        )
        page_payment_module_details.get_button_apply_exclusions().click()
        page_payment_module_details.get_button_save_exclusions().click()
        for _ in range(100):
            sleep(0.1)
            if "0" in page_payment_module_details.get_label_male_adults().text:
                break
        else:
            assert "0" in page_payment_module_details.get_label_male_adults().text

        assert "4" in page_payment_module_details.get_label_female_children().text
        assert "1" in page_payment_module_details.get_label_female_adults().text
        assert "1" in page_payment_module_details.get_label_male_children().text
        assert "6" in page_payment_module_details.get_label_total_number_of_people().text

    def test_payment_plan_save_exclude(
        self,
        create_payment_plan_lock: PaymentPlan,
        page_payment_module: PaymentModule,
        page_payment_module_details: PaymentModuleDetails,
    ) -> None:
        page_payment_module.select_global_program_filter("Test Program")
        page_payment_module.get_nav_payment_module().click()
        page_payment_module.get_nav_payment_plans().click()
        page_payment_module.get_row(0).click()
        page_payment_module_details.get_button_create_exclusions()
        page_payment_module_details.get_label_targeted_individuals()
        assert "5" in page_payment_module_details.get_label_female_children().text
        assert "2" in page_payment_module_details.get_label_female_adults().text
        assert "3" in page_payment_module_details.get_label_male_children().text
        assert "1" in page_payment_module_details.get_label_male_adults().text
        assert "2" in page_payment_module_details.get_label_total_number_of_households().text
        assert "11" in page_payment_module_details.get_label_targeted_individuals().text
        page_payment_module_details.get_button_create_exclusions().click()
        page_payment_module_details.get_input_exclusion_reason().send_keys("Reason e2e Test")
        page_payment_module_details.get_input_households_ids()
        page_payment_module_details.get_input_households_ids().find_element(By.TAG_NAME, "input").send_keys(
            "HH-17-0000.3340"
        )
        page_payment_module_details.get_button_apply_exclusions().click()
        page_payment_module_details.get_button_save_exclusions().click()
        for _ in range(100):
            sleep(0.1)
            if "1" in page_payment_module_details.get_label_total_number_of_households().text:
                break
        else:
            assert "1" in page_payment_module_details.get_label_total_number_of_households().text

        assert "4" in page_payment_module_details.get_label_female_children().text
        assert "1" in page_payment_module_details.get_label_female_adults().text
        assert "1" in page_payment_module_details.get_label_male_children().text
        assert "0" in page_payment_module_details.get_label_male_adults().text

        assert "6" in page_payment_module_details.get_label_targeted_individuals().text

    def test_payment_plan_delete(
        self,
        create_payment_plan_open: PaymentPlan,
        page_payment_module: PaymentModule,
        page_payment_module_details: PaymentModuleDetails,
        page_new_payment_plan: NewPaymentPlan,
    ) -> None:
        page_payment_module.select_global_program_filter("Test Program")
        page_payment_module.get_nav_payment_module().click()
        page_payment_module.get_nav_payment_plans().click()
        page_payment_module.get_rows()
        for i in range(len(page_payment_module.get_rows())):
            if "OPEN" in page_payment_module.get_row(i).text:
                payment_plan = page_payment_module.get_row(i).text
                page_payment_module.get_row(i).click()
                break
        else:
            raise AssertionError("No payment plan has Open status")
        page_payment_module_details.get_delete_button().click()
        page_payment_module_details.get_button_submit().click()
        page_payment_module.get_row(0)
        assert payment_plan not in page_payment_module.get_row(0).text
        assert "LOCKED" in page_payment_module.get_row(0).text

    def test_payment_plan_creation_error(
        self,
        create_targeting: None,
        page_payment_module: PaymentModule,
        page_payment_module_details: PaymentModuleDetails,
        page_new_payment_plan: NewPaymentPlan,
        page_program_cycle: ProgramCyclePage,
        page_program_cycle_details: ProgramCycleDetailsPage,
    ) -> None:
        page_program_cycle.select_global_program_filter("Test Program")
        page_program_cycle.get_nav_payment_module().click()
        page_program_cycle.get_nav_programme_cycles().click()
        assert (
            "Draft"
            in page_program_cycle.get_program_cycle_row()[0]
            .find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-status"]')
            .text
        )
        page_program_cycle.get_program_cycle_row()[0].find_element(
            By.CSS_SELECTOR, 'td[data-cy="program-cycle-title"]'
        ).find_element(By.TAG_NAME, "a").click()
        page_program_cycle_details.get_button_create_payment_plan().click()

        page_new_payment_plan.get_button_save_payment_plan().click()

        assert "Target Population is required" in page_new_payment_plan.get_input_target_population().text
        assert "Dispersion Start Date is required" in page_new_payment_plan.get_input_start_date_error().text
        assert "Dispersion End Date is required" in page_new_payment_plan.get_input_end_date_error().text
        assert "Currency is required" in page_new_payment_plan.get_input_currency().text

    def test_payment_plan_supporting_documents(
        self,
        create_payment_plan_lock: PaymentPlan,
        page_payment_module: PaymentModule,
        page_payment_module_details: PaymentModuleDetails,
    ) -> None:
        page_payment_module.select_global_program_filter("Test Program")
        page_payment_module.get_nav_payment_module().click()
        page_payment_module.get_nav_payment_plans().click()
        page_payment_module.get_row(0).click()
        page_payment_module_details.get_upload_file_button().click()
        page_payment_module_details.upload_file(f"{pytest.SELENIUM_PATH}/helpers/document_example.png")
        page_payment_module_details.get_title_input().find_element(By.TAG_NAME, "input").send_keys("title input")
        page_payment_module_details.get_button_import_submit().click()
