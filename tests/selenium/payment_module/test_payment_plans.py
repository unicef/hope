import os
import zipfile
from datetime import datetime
from time import sleep

import factory
import openpyxl
import pytest
from dateutil.relativedelta import relativedelta
from pytz import utc
from selenium.webdriver.common.by import By
from sorl.thumbnail.conf import settings

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import (
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    FinancialServiceProvider,
    PaymentPlan,
)
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.steficon.fixtures import RuleCommitFactory, RuleFactory
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)
from hct_mis_api.apps.targeting.models import TargetPopulation
from src.hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from src.hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from tests.selenium.helpers.date_time_format import FormatTime
from tests.selenium.page_object.payment_module.new_payment_plan import NewPaymentPlan
from tests.selenium.page_object.payment_module.payment_module import PaymentModule
from tests.selenium.page_object.payment_module.payment_module_details import (
    PaymentModuleDetails,
)
from tests.selenium.page_object.payment_module.program_cycle import ProgramCyclePage
from tests.selenium.page_object.payment_module.program_cycle_details import (
    ProgramCycleDetailsPage,
)

pytestmark = pytest.mark.django_db(transaction=True)


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
    yield create_program(dct_type=DataCollectingType.Type.SOCIAL)


def create_program(name: str = "Test Program", dct_type: str = DataCollectingType.Type.STANDARD) -> Program:
    BusinessArea.objects.filter(slug="afghanistan").update(is_payment_plan_applicable=True)
    dct = DataCollectingTypeFactory(type=dct_type)
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
    )


@pytest.fixture
def create_targeting(create_test_program: Program) -> None:
    generate_delivery_mechanisms()
    dm_cash = DeliveryMechanism.objects.get(code="cash")

    targeting_criteria = TargetingCriteriaFactory()

    tp = TargetPopulationFactory(
        program=create_test_program,
        status=TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE,
        targeting_criteria=targeting_criteria,
        program_cycle=create_test_program.cycles.first(),
    )
    households = [
        create_household(
            household_args={"size": 2, "business_area": tp.business_area, "program": tp.program},
        )[0]
        for _ in range(14)
    ]

    tp.households.set(households)
    business_area = BusinessArea.objects.get(slug="afghanistan")
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
def clear_downloaded_files() -> None:
    for file in os.listdir(settings.DOWNLOAD_DIRECTORY):
        os.remove(os.path.join(settings.DOWNLOAD_DIRECTORY, file))
    yield
    for file in os.listdir(settings.DOWNLOAD_DIRECTORY):
        os.remove(os.path.join(settings.DOWNLOAD_DIRECTORY, file))


@pytest.fixture
def create_payment_plan(create_targeting: None) -> PaymentPlan:
    tp = TargetPopulation.objects.get(program__name="Test Program")
    cycle = ProgramCycleFactory(
        program=tp.program,
        title="Cycle for PaymentPlan",
        status=ProgramCycle.ACTIVE,
        start_date=datetime.now() + relativedelta(days=10),
        end_date=datetime.now() + relativedelta(days=15),
    )
    payment_plan = PaymentPlan.objects.update_or_create(
        business_area=BusinessArea.objects.only("is_payment_plan_applicable").get(slug="afghanistan"),
        target_population=tp,
        program_cycle=cycle,
        currency="USD",
        dispersion_start_date=datetime.now() + relativedelta(days=10),
        dispersion_end_date=datetime.now() + relativedelta(days=15),
        status_date=datetime.now(),
        status=PaymentPlan.Status.ACCEPTED,
        created_by=User.objects.first(),
        program=tp.program,
        total_delivered_quantity=999,
        total_entitled_quantity=2999,
        is_follow_up=False,
        program_id=tp.program.id,
    )
    yield payment_plan[0]


@pytest.fixture
def create_payment_plan_lock(create_test_program: Program) -> PaymentPlan:
    yield payment_plan_create(create_test_program)


@pytest.fixture
def create_payment_plan_lock_social_worker(social_worker_program: Program) -> PaymentPlan:
    yield payment_plan_create(social_worker_program)


def payment_plan_create(program: Program) -> PaymentPlan:
    program_cycle = ProgramCycleFactory(
        program=program,
        title="Cycle for PaymentPlan",
        status=ProgramCycle.ACTIVE,
        start_date=datetime.now() + relativedelta(days=10),
        end_date=datetime.now() + relativedelta(days=15),
    )

    payment_plan = PaymentPlanFactory(
        program=program,
        is_follow_up=False,
        status=PaymentPlan.Status.LOCKED,
        program_cycle=program_cycle,
        dispersion_start_date=datetime.now().date(),
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
        sex="MALE",
        unicef_id="IND-06-0001.1828",
        birth_date=factory.Faker("date_of_birth", tzinfo=utc, minimum_age=20, maximum_age=40),
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
        assert "Num. of Households" in pagePaymentModule.getTableLabel()[3].text
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
        assert "SET UP FSP" in pagePaymentModuleDetails.getButtonSetUpFsp().text
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
        assert "Household ID" in pagePaymentModuleDetails.getTableLabel()[2].text
        assert "Household Size" in pagePaymentModuleDetails.getTableLabel()[3].text
        assert "Administrative Level 2" in pagePaymentModuleDetails.getTableLabel()[4].text
        assert "Collector" in pagePaymentModuleDetails.getTableLabel()[5].text
        assert "FSP" in pagePaymentModuleDetails.getTableLabel()[6].text
        assert "Entitlement" in pagePaymentModuleDetails.getTableLabel()[7].text
        assert "Delivered Quantity" in pagePaymentModuleDetails.getTableLabel()[8].text
        assert "Status" in pagePaymentModuleDetails.getTableLabel()[9].text
        assert "FSP Auth Code" in pagePaymentModuleDetails.getTableLabel()[10].text
        assert "Reconciliation" in pagePaymentModuleDetails.getTableLabel()[11].text

    def test_payment_plan_happy_path(
        self,
        clear_downloaded_files: None,
        create_targeting: None,
        pagePaymentModule: PaymentModule,
        pagePaymentModuleDetails: PaymentModuleDetails,
        pageNewPaymentPlan: NewPaymentPlan,
        pageProgramCycle: ProgramCyclePage,
        pageProgramCycleDetails: ProgramCycleDetailsPage,
    ) -> None:
        targeting = TargetPopulation.objects.first()
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
        pageNewPaymentPlan.select_listbox_element(targeting.name)
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

        for _ in range(10):
            try:
                pagePaymentModuleDetails.getButtonSetUpFsp().click()
                break
            except BaseException:
                sleep(1)
        else:
            pagePaymentModuleDetails.getButtonSetUpFsp().click()

        pagePaymentModuleDetails.getSelectDeliveryMechanism().click()
        pagePaymentModuleDetails.select_listbox_element("Cash")
        pagePaymentModuleDetails.getButtonNextSave().click()
        pagePaymentModuleDetails.getSelectDeliveryMechanismFSP().click()
        pagePaymentModuleDetails.select_listbox_element("FSP_1")
        pagePaymentModuleDetails.getButtonNextSave().click()
        pagePaymentModuleDetails.checkStatus("LOCKED")
        pagePaymentModuleDetails.getButtonLockPlan().click()
        pagePaymentModuleDetails.getButtonSubmit().click()
        pagePaymentModuleDetails.checkStatus("LOCKED FSP")
        pagePaymentModuleDetails.getButtonSendForApproval().click()
        pagePaymentModuleDetails.checkStatus("IN APPROVAL")
        pagePaymentModuleDetails.getButtonApprove().click()
        pagePaymentModuleDetails.getButtonSubmit().click()
        pagePaymentModuleDetails.checkStatus("IN AUTHORIZATION")
        pagePaymentModuleDetails.getButtonAuthorize().click()
        pagePaymentModuleDetails.getButtonSubmit().click()
        pagePaymentModuleDetails.checkStatus("IN REVIEW")
        pagePaymentModuleDetails.getButtonMarkAsReleased().click()
        pagePaymentModuleDetails.getButtonSubmit().click()
        pagePaymentModuleDetails.checkStatus("ACCEPTED")
        pagePaymentModuleDetails.getButtonExportXlsx().click()
        pagePaymentModuleDetails.checkAlert("Exporting XLSX started")

        # ToDo: Refresh is workaround. Works on dev properly.
        pagePaymentModule.driver.refresh()
        pagePaymentModuleDetails.getButtonDownloadXlsx().click()

        zip_file = find_file(".zip", number_of_ties=15)
        with zipfile.ZipFile(os.path.join(settings.DOWNLOAD_DIRECTORY, zip_file), "r") as zip_ref:
            zip_ref.extractall(settings.DOWNLOAD_DIRECTORY)

        xlsx_file = find_file(".xlsx")
        wb1 = openpyxl.load_workbook(os.path.join(settings.DOWNLOAD_DIRECTORY, xlsx_file))
        ws1 = wb1.active
        for cell in ws1["N:N"]:
            if cell.row >= 2:
                ws1.cell(row=cell.row, column=16, value=cell.value)

        wb1.save(os.path.join(settings.DOWNLOAD_DIRECTORY, xlsx_file))

        pagePaymentModuleDetails.getButtonUploadReconciliationInfo().click()
        pagePaymentModuleDetails.upload_file(
            os.path.abspath(os.path.join(settings.DOWNLOAD_DIRECTORY, xlsx_file)), timeout=120
        )
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

        assert "5" in pagePaymentModuleDetails.getLabelFemaleChildren().text
        assert "2" in pagePaymentModuleDetails.getLabelFemaleAdults().text
        assert "3" in pagePaymentModuleDetails.getLabelMaleChildren().text

        assert "10" in pagePaymentModuleDetails.getLabelTotalNumberOfPeople().text

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
        create_payment_plan_lock: PaymentPlan,
        pagePaymentModule: PaymentModule,
        pagePaymentModuleDetails: PaymentModuleDetails,
        pageNewPaymentPlan: NewPaymentPlan,
    ) -> None:
        pagePaymentModule.selectGlobalProgramFilter("Test Program")
        pagePaymentModule.getNavPaymentModule().click()
        pagePaymentModule.getNavPaymentPlans().click()
        payment_plan = pagePaymentModule.getRow(0).text
        pagePaymentModule.getRow(0).click()

        pagePaymentModuleDetails.getDeleteButton().click()
        pagePaymentModuleDetails.getButtonSubmit().click()
        pagePaymentModule.getRow(0)
        assert payment_plan not in pagePaymentModule.getRow(0).text

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
