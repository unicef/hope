import os
import zipfile
from datetime import datetime
from time import sleep

import factory
import openpyxl
import pytest
from dateutil.relativedelta import relativedelta
from e2e.helpers.date_time_format import FormatTime
from e2e.page_object.payment_module.new_payment_plan import NewPaymentPlan
from e2e.page_object.payment_module.payment_module import PaymentModule
from e2e.page_object.payment_module.payment_module_details import PaymentModuleDetails
from e2e.page_object.payment_module.program_cycle import ProgramCyclePage
from e2e.page_object.payment_module.program_cycle_details import ProgramCycleDetailsPage
from selenium.webdriver.common.by import By
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
from pytz import utc
from sorl.thumbnail.conf import settings

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


def find_file(file_name: str, search_in_dir: str = settings.DOWNLOAD_DIRECTORY, number_of_ties: int = 1) -> str:
    for _ in range(number_of_ties):
        for file in os.listdir(search_in_dir):
            if file_name in file:
                return file
        sleep(1)
    else:
        raise Exception(f"{file_name} file did not found in {search_in_dir}")


@pytest.fixture
def create_test_program() -> Program:
    yield create_program()


@pytest.fixture
def social_worker_program() -> Program:
    yield create_program(dct_type=DataCollectingType.Type.SOCIAL, beneficiary_group_name="People")


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
            household_args={"size": 2, "business_area": business_area, "program": program},
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
    yield payment_plan


@pytest.fixture
def create_payment_plan_lock(create_test_program: Program) -> PaymentPlan:
    yield payment_plan_create(create_test_program)


@pytest.fixture
def create_payment_plan_lock_social_worker(social_worker_program: Program) -> PaymentPlan:
    yield payment_plan_create(social_worker_program)


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
        id="3d7087be-e8f8-478d-9ca2-4ca6d5e96f51", unicef_id="HH-17-0000.3340", head_of_household=hoh1, size=2
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

    yield payment_plan


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
        id="3d7087be-e8f8-478d-9ca2-4ca6d5e96f51", unicef_id="HH-17-0000.3340", head_of_household=hoh1, size=2
    )
    household_2 = HouseholdFactory(
        id="3d7087be-e8f8-478d-9ca2-4ca6d5e96f52", unicef_id="HH-17-0000.3341", head_of_household=hoh2, size=3
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
    def test_smoke_payment_plan(self, create_payment_plan: PaymentPlan, pagePaymentModule: PaymentModule) -> None:
        pagePaymentModule.selectGlobalProgramFilter("Test Program")
        pagePaymentModule.getNavPaymentModule().click()
        pagePaymentModule.getNavPaymentPlans().click()
        assert "Payment Module" in pagePaymentModule.getPageHeaderTitle().text
        assert "Status" in pagePaymentModule.getSelectFilter().text
        assert "" in pagePaymentModule.getFiltersTotalEntitledQuantityFrom().text
        assert "" in pagePaymentModule.getFiltersTotalEntitledQuantityTo().text
        assert "" in pagePaymentModule.getDatePickerFilterFrom().text
        assert "" in pagePaymentModule.getDatePickerFilterTo().text
        assert "CLEAR" in pagePaymentModule.getButtonFiltersClear().text
        assert "APPLY" in pagePaymentModule.getButtonFiltersApply().text
        assert "Payment Plans" in pagePaymentModule.getTableTitle().text
        assert "Payment Plan ID" in pagePaymentModule.getTableLabel()[0].text
        assert "Status" in pagePaymentModule.getTableLabel()[1].text
        assert "Target Population" in pagePaymentModule.getTableLabel()[2].text
        assert "Num. of Items Groups" in pagePaymentModule.getTableLabel()[3].text
        assert "Currency" in pagePaymentModule.getTableLabel()[4].text
        assert "Total Entitled Quantity" in pagePaymentModule.getTableLabel()[5].text
        assert "Total Delivered Quantity" in pagePaymentModule.getTableLabel()[6].text
        assert "Total Undelivered Quantity" in pagePaymentModule.getTableLabel()[7].text
        assert "Dispersion Start Date" in pagePaymentModule.getTableLabel()[8].text
        assert "Dispersion End Date" in pagePaymentModule.getTableLabel()[9].text
        assert "Follow-up Payment Plans" in pagePaymentModule.getTableLabel()[10].text
        assert "ACCEPTED" in pagePaymentModule.getStatusContainer().text
        assert "Rows per page: 5 1–1 of 1" in pagePaymentModule.getTablePagination().text.replace("\n", " ")

    def test_smoke_new_payment_plan(
        self,
        create_test_program: Program,
        pagePaymentModule: PaymentModule,
        pageProgramCycle: ProgramCyclePage,
        pageProgramCycleDetails: ProgramCycleDetailsPage,
        pageNewPaymentPlan: NewPaymentPlan,
    ) -> None:
        pagePaymentModule.selectGlobalProgramFilter("Test Program")
        pagePaymentModule.getNavPaymentModule().click()
        pageProgramCycle.getNavProgrammeCycles().click()
        pageProgramCycle.getProgramCycleRow()[0].find_element(
            By.CSS_SELECTOR, 'td[data-cy="program-cycle-title"]'
        ).find_element(By.TAG_NAME, "a").click()
        pageProgramCycleDetails.getButtonCreatePaymentPlan().click()
        assert "New Payment Plan" in pageNewPaymentPlan.getPageHeaderTitle().text
        assert "SAVE" in pageNewPaymentPlan.getButtonSavePaymentPlan().text
        assert "Target Population" in pageNewPaymentPlan.getInputTargetPopulation().text
        assert "Currency" in pageNewPaymentPlan.getInputCurrency().text
        assert "Dispersion Start Date*" in pageNewPaymentPlan.wait_for(pageNewPaymentPlan.inputDispersionStartDate).text
        assert "Dispersion End Date*" in pageNewPaymentPlan.wait_for(pageNewPaymentPlan.inputDispersionEndDate).text

    def test_smoke_details_payment_plan(
        self,
        create_payment_plan: PaymentPlan,
        pagePaymentModule: PaymentModule,
        pagePaymentModuleDetails: PaymentModuleDetails,
    ) -> None:
        pagePaymentModule.selectGlobalProgramFilter("Test Program")
        pagePaymentModule.getNavPaymentModule().click()
        pagePaymentModule.getNavPaymentPlans().click()
        pagePaymentModule.getRow(0).click()
        assert "ACCEPTED" in pagePaymentModuleDetails.getStatusContainer().text
        assert "EXPORT XLSX" in pagePaymentModuleDetails.getButtonExportXlsx().text
        assert "USD" in pagePaymentModuleDetails.getLabelCurrency().text
        assert (
            str((datetime.now() + relativedelta(days=10)).strftime("%-d %b %Y"))
            in pagePaymentModuleDetails.getLabelDispersionStartDate().text
        )
        assert (
            str((datetime.now() + relativedelta(days=15)).strftime("%-d %b %Y"))
            in pagePaymentModuleDetails.getLabelDispersionEndDate().text
        )
        assert "-" in pagePaymentModuleDetails.getLabelRelatedFollowUpPaymentPlans().text
        assert "CREATE" in pagePaymentModuleDetails.getButtonCreateExclusions().text
        assert "Supporting Documents" in pagePaymentModuleDetails.getSupportingDocumentsTitle().text
        assert "No documents uploaded" in pagePaymentModuleDetails.getSupportingDocumentsEmpty().text
        assert "0" in pagePaymentModuleDetails.getLabelFemaleChildren().text
        assert "0" in pagePaymentModuleDetails.getLabelFemaleAdults().text
        assert "0" in pagePaymentModuleDetails.getLabelMaleChildren().text
        assert "0" in pagePaymentModuleDetails.getLabelMaleAdults().text
        assert "" in pagePaymentModuleDetails.getChartContainer().text
        assert "0" in pagePaymentModuleDetails.getLabelTotalNumberOfHouseholds().text
        assert "0" in pagePaymentModuleDetails.getLabelTargetedIndividuals().text
        assert "Payee List" in pagePaymentModuleDetails.getTableTitle().text
        assert "UPLOAD RECONCILIATION INFO" in pagePaymentModuleDetails.getButtonImport().text
        assert "Payment ID" in pagePaymentModuleDetails.getTableLabel()[1].text
        assert "Items Group ID" in pagePaymentModuleDetails.getTableLabel()[2].text
        assert "Items Group Size" in pagePaymentModuleDetails.getTableLabel()[3].text
        assert "Administrative Level 2" in pagePaymentModuleDetails.getTableLabel()[4].text
        assert "Collector" in pagePaymentModuleDetails.getTableLabel()[5].text
        assert "FSP" in pagePaymentModuleDetails.getTableLabel()[6].text
        assert "Entitlement" in pagePaymentModuleDetails.getTableLabel()[7].text
        assert "Delivered Quantity" in pagePaymentModuleDetails.getTableLabel()[8].text
        assert "Status" in pagePaymentModuleDetails.getTableLabel()[9].text
        assert "FSP Auth Code" in pagePaymentModuleDetails.getTableLabel()[10].text
        assert "Reconciliation" in pagePaymentModuleDetails.getTableLabel()[11].text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_payment_plan_happy_path(
        self,
        clear_downloaded_files: None,
        create_targeting: None,
        pagePaymentModule: PaymentModule,
        pagePaymentModuleDetails: PaymentModuleDetails,
        pageNewPaymentPlan: NewPaymentPlan,
        pageProgramCycle: ProgramCyclePage,
        pageProgramCycleDetails: ProgramCycleDetailsPage,
        download_path: str,
    ) -> None:
        payment_plan = PaymentPlan.objects.first()
        pageProgramCycle.selectGlobalProgramFilter("Test Program")
        pageProgramCycle.getNavPaymentModule().click()
        pageProgramCycle.getNavProgrammeCycles().click()
        assert (
            "Draft"
            in pageProgramCycle.getProgramCycleRow()[0]
            .find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-status"]')
            .text
        )
        pageProgramCycle.getProgramCycleRow()[0].find_element(
            By.CSS_SELECTOR, 'td[data-cy="program-cycle-title"]'
        ).find_element(By.TAG_NAME, "a").click()
        pageProgramCycleDetails.getButtonCreatePaymentPlan().click()
        pageNewPaymentPlan.getInputTargetPopulation().click()
        pageNewPaymentPlan.select_listbox_element(payment_plan.name)
        pageNewPaymentPlan.getInputCurrency().click()
        pageNewPaymentPlan.select_listbox_element("Czech koruna")
        pageNewPaymentPlan.getInputDispersionStartDate().click()
        pageNewPaymentPlan.getInputDispersionStartDate().send_keys(FormatTime(22, 1, 2024).numerically_formatted_date)
        pageNewPaymentPlan.getInputDispersionEndDate().click()
        pageNewPaymentPlan.getInputDispersionEndDate().send_keys(FormatTime(30, 6, 2030).numerically_formatted_date)
        pageNewPaymentPlan.getInputCurrency().click()
        pageNewPaymentPlan.getButtonSavePaymentPlan().click()
        assert "OPEN" in pagePaymentModuleDetails.getStatusContainer().text
        assert "CZK" in pagePaymentModuleDetails.getLabelCurrency().text
        assert (
            FormatTime(22, 1, 2024).date_in_text_format in pagePaymentModuleDetails.getLabelDispersionStartDate().text
        )
        assert FormatTime(30, 6, 2030).date_in_text_format in pagePaymentModuleDetails.getLabelDispersionEndDate().text
        pagePaymentModuleDetails.getButtonLockPlan().click()
        pagePaymentModuleDetails.getButtonSubmit().click()
        pagePaymentModuleDetails.getInputEntitlementFormula().click()
        pagePaymentModuleDetails.select_listbox_element("Test Rule")
        pagePaymentModuleDetails.getButtonApplySteficon().click()
        pagePaymentModuleDetails.checkStatus("LOCKED")
        pagePaymentModuleDetails.clickButtonLockPlan()
        pagePaymentModuleDetails.getButtonSubmit().click()
        pagePaymentModuleDetails.checkAlert("Payment Plan FSPs are locked.")
        pagePaymentModuleDetails.checkStatus("LOCKED FSP")
        pagePaymentModuleDetails.clickButtonSendForApproval()
        pagePaymentModuleDetails.checkAlert("Payment Plan has been sent for approval.")
        pagePaymentModuleDetails.checkStatus("IN APPROVAL")
        pagePaymentModuleDetails.clickButtonApprove()
        pagePaymentModuleDetails.getButtonSubmit().click()
        pagePaymentModuleDetails.checkAlert("Payment Plan has been approved.")
        pagePaymentModuleDetails.checkStatus("IN AUTHORIZATION")
        pagePaymentModuleDetails.clickButtonAuthorize()
        pagePaymentModuleDetails.getButtonSubmit().click()
        pagePaymentModuleDetails.checkAlert("Payment Plan has been authorized")
        pagePaymentModuleDetails.checkStatus("IN REVIEW")
        pagePaymentModuleDetails.clickButtonMarkAsReleased()
        pagePaymentModuleDetails.getButtonSubmit().click()
        pagePaymentModuleDetails.checkAlert("Payment Plan has been marked as reviewed.")
        pagePaymentModuleDetails.checkStatus("ACCEPTED")
        pagePaymentModuleDetails.clickButtonExportXlsx()
        pagePaymentModuleDetails.checkAlert("Exporting XLSX started")

        # ToDo: Refresh is workaround. Works on dev properly.
        pagePaymentModule.driver.refresh()
        pagePaymentModuleDetails.getButtonDownloadXlsx().click()

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

        pagePaymentModuleDetails.getButtonUploadReconciliationInfo().click()
        pagePaymentModuleDetails.upload_file(os.path.abspath(os.path.join(download_path, xlsx_file)), timeout=120)
        pagePaymentModuleDetails.getButtonImportSubmit().click()
        pagePaymentModuleDetails.checkStatus("FINISHED")
        assert "14 (100%)" in pagePaymentModuleDetails.getLabelReconciled().text
        assert "18.2 CZK (0.7 USD)" in pagePaymentModuleDetails.getLabelTotalEntitledQuantity().text
        pagePaymentModule.getNavPaymentModule().click()
        pagePaymentModule.getNavProgrammeCycles().click()
        assert (
            "Active"
            in pageProgramCycle.getProgramCycleRow()[0]
            .find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-status"]')
            .text
        )


@pytest.mark.usefixtures("login")
class TestPaymentPlans:
    def test_payment_plan_edit(
        self,
        clear_downloaded_files: None,
        create_targeting: None,
        pagePaymentModule: PaymentModule,
        pagePaymentModuleDetails: PaymentModuleDetails,
        pageNewPaymentPlan: NewPaymentPlan,
        pageProgramCycle: ProgramCyclePage,
        pageProgramCycleDetails: ProgramCycleDetailsPage,
    ) -> None:
        pageProgramCycle.selectGlobalProgramFilter("Test Program")
        pageProgramCycle.getNavPaymentModule().click()

    def test_payment_plan_exclude_not_lock_error(
        self,
        create_payment_plan: PaymentPlan,
        pagePaymentModule: PaymentModule,
        pagePaymentModuleDetails: PaymentModuleDetails,
        pageNewPaymentPlan: NewPaymentPlan,
        pageProgramCycle: ProgramCyclePage,
        pageProgramCycleDetails: ProgramCycleDetailsPage,
    ) -> None:
        pagePaymentModule.selectGlobalProgramFilter("Test Program")
        pagePaymentModule.getNavPaymentModule().click()
        pagePaymentModule.getNavPaymentPlans().click()
        pagePaymentModule.getRow(0).click()
        pagePaymentModuleDetails.getButtonCreateExclusions().click()
        with pytest.raises(Exception):
            pagePaymentModuleDetails.getButtonSaveExclusions().click()

    def test_payment_plan_save_exclude_people(
        self,
        create_payment_plan_lock_social_worker: PaymentPlan,
        pagePaymentModule: PaymentModule,
        pagePaymentModuleDetails: PaymentModuleDetails,
    ) -> None:
        pagePaymentModule.selectGlobalProgramFilter("Test Program")
        pagePaymentModule.getNavPaymentModule().click()
        pagePaymentModule.getNavPaymentPlans().click()
        pagePaymentModule.getRow(0).click()
        pagePaymentModuleDetails.getButtonCreateExclusions()
        pagePaymentModuleDetails.getLabelTotalNumberOfPeople()
        assert "5" in pagePaymentModuleDetails.getLabelFemaleChildren().text
        assert "2" in pagePaymentModuleDetails.getLabelFemaleAdults().text
        assert "3" in pagePaymentModuleDetails.getLabelMaleChildren().text
        assert "1" in pagePaymentModuleDetails.getLabelMaleAdults().text
        assert "11" in pagePaymentModuleDetails.getLabelTotalNumberOfPeople().text
        pagePaymentModuleDetails.getButtonCreateExclusions().click()
        pagePaymentModuleDetails.getInputExclusionReason().send_keys("Reason e2e Test")
        pagePaymentModuleDetails.getInputBeneficiariesIds()
        pagePaymentModuleDetails.getInputBeneficiariesIds().find_element(By.TAG_NAME, "input").send_keys(
            "IND-06-0001.1828"
        )
        pagePaymentModuleDetails.getButtonApplyExclusions().click()
        pagePaymentModuleDetails.getButtonSaveExclusions().click()
        for _ in range(100):
            sleep(0.1)
            if "0" in pagePaymentModuleDetails.getLabelMaleAdults().text:
                break
        else:
            assert "0" in pagePaymentModuleDetails.getLabelMaleAdults().text

        assert "4" in pagePaymentModuleDetails.getLabelFemaleChildren().text
        assert "1" in pagePaymentModuleDetails.getLabelFemaleAdults().text
        assert "1" in pagePaymentModuleDetails.getLabelMaleChildren().text
        assert "6" in pagePaymentModuleDetails.getLabelTotalNumberOfPeople().text

    def test_payment_plan_save_exclude(
        self,
        create_payment_plan_lock: PaymentPlan,
        pagePaymentModule: PaymentModule,
        pagePaymentModuleDetails: PaymentModuleDetails,
    ) -> None:
        pagePaymentModule.selectGlobalProgramFilter("Test Program")
        pagePaymentModule.getNavPaymentModule().click()
        pagePaymentModule.getNavPaymentPlans().click()
        pagePaymentModule.getRow(0).click()
        pagePaymentModuleDetails.getButtonCreateExclusions()
        pagePaymentModuleDetails.getLabelTargetedIndividuals()
        assert "5" in pagePaymentModuleDetails.getLabelFemaleChildren().text
        assert "2" in pagePaymentModuleDetails.getLabelFemaleAdults().text
        assert "3" in pagePaymentModuleDetails.getLabelMaleChildren().text
        assert "1" in pagePaymentModuleDetails.getLabelMaleAdults().text
        assert "2" in pagePaymentModuleDetails.getLabelTotalNumberOfHouseholds().text
        assert "11" in pagePaymentModuleDetails.getLabelTargetedIndividuals().text
        pagePaymentModuleDetails.getButtonCreateExclusions().click()
        pagePaymentModuleDetails.getInputExclusionReason().send_keys("Reason e2e Test")
        pagePaymentModuleDetails.getInputHouseholdsIds()
        pagePaymentModuleDetails.getInputHouseholdsIds().find_element(By.TAG_NAME, "input").send_keys("HH-17-0000.3340")
        pagePaymentModuleDetails.getButtonApplyExclusions().click()
        pagePaymentModuleDetails.getButtonSaveExclusions().click()
        for _ in range(100):
            sleep(0.1)
            if "1" in pagePaymentModuleDetails.getLabelTotalNumberOfHouseholds().text:
                break
        else:
            assert "1" in pagePaymentModuleDetails.getLabelTotalNumberOfHouseholds().text

        assert "4" in pagePaymentModuleDetails.getLabelFemaleChildren().text
        assert "1" in pagePaymentModuleDetails.getLabelFemaleAdults().text
        assert "1" in pagePaymentModuleDetails.getLabelMaleChildren().text
        assert "0" in pagePaymentModuleDetails.getLabelMaleAdults().text

        assert "6" in pagePaymentModuleDetails.getLabelTargetedIndividuals().text

    def test_payment_plan_delete(
        self,
        create_payment_plan_open: PaymentPlan,
        pagePaymentModule: PaymentModule,
        pagePaymentModuleDetails: PaymentModuleDetails,
        pageNewPaymentPlan: NewPaymentPlan,
    ) -> None:
        pagePaymentModule.selectGlobalProgramFilter("Test Program")
        pagePaymentModule.getNavPaymentModule().click()
        pagePaymentModule.getNavPaymentPlans().click()
        pagePaymentModule.getRows()
        for i in range(len(pagePaymentModule.getRows())):
            if "OPEN" in pagePaymentModule.getRow(i).text:
                payment_plan = pagePaymentModule.getRow(i).text
                pagePaymentModule.getRow(i).click()
                break
        else:
            raise AssertionError("No payment plan has Open status")
        pagePaymentModuleDetails.getDeleteButton().click()
        pagePaymentModuleDetails.getButtonSubmit().click()
        pagePaymentModule.getRow(0)
        assert payment_plan not in pagePaymentModule.getRow(0).text
        assert "LOCKED" in pagePaymentModule.getRow(0).text

    def test_payment_plan_creation_error(
        self,
        create_targeting: None,
        pagePaymentModule: PaymentModule,
        pagePaymentModuleDetails: PaymentModuleDetails,
        pageNewPaymentPlan: NewPaymentPlan,
        pageProgramCycle: ProgramCyclePage,
        pageProgramCycleDetails: ProgramCycleDetailsPage,
    ) -> None:
        pageProgramCycle.selectGlobalProgramFilter("Test Program")
        pageProgramCycle.getNavPaymentModule().click()
        pageProgramCycle.getNavProgrammeCycles().click()
        assert (
            "Draft"
            in pageProgramCycle.getProgramCycleRow()[0]
            .find_element(By.CSS_SELECTOR, 'td[data-cy="program-cycle-status"]')
            .text
        )
        pageProgramCycle.getProgramCycleRow()[0].find_element(
            By.CSS_SELECTOR, 'td[data-cy="program-cycle-title"]'
        ).find_element(By.TAG_NAME, "a").click()
        pageProgramCycleDetails.getButtonCreatePaymentPlan().click()

        pageNewPaymentPlan.getButtonSavePaymentPlan().click()

        assert "Target Population is required" in pageNewPaymentPlan.getInputTargetPopulation().text
        assert "Dispersion Start Date is required" in pageNewPaymentPlan.getInputStartDateError().text
        assert "Dispersion End Date is required" in pageNewPaymentPlan.getInputEndDateError().text
        assert "Currency is required" in pageNewPaymentPlan.getInputCurrency().text

    def test_payment_plan_supporting_documents(
        self,
        create_payment_plan_lock: PaymentPlan,
        pagePaymentModule: PaymentModule,
        pagePaymentModuleDetails: PaymentModuleDetails,
    ) -> None:
        pagePaymentModule.selectGlobalProgramFilter("Test Program")
        pagePaymentModule.getNavPaymentModule().click()
        pagePaymentModule.getNavPaymentPlans().click()
        pagePaymentModule.getRow(0).click()
        pagePaymentModuleDetails.getUploadFileButton().click()
        pagePaymentModuleDetails.upload_file(f"{pytest.SELENIUM_PATH}/helpers/document_example.png")
        pagePaymentModuleDetails.getTitleInput().find_element(By.TAG_NAME, "input").send_keys("title input")
        pagePaymentModuleDetails.getButtonImportSubmit().click()
