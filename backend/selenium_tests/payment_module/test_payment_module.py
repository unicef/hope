from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta
from page_object.payment_module.new_payment_plan import NewPaymentPlan
from page_object.payment_module.payment_module import PaymentModule
from page_object.payment_module.payment_module_details import PaymentModuleDetails

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)
from hct_mis_api.apps.targeting.models import TargetPopulation

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def create_test_program() -> Program:
    BusinessArea.objects.filter(slug="afghanistan").update(is_payment_plan_applicable=True)
    dct = DataCollectingTypeFactory(type=DataCollectingType.Type.STANDARD)
    return ProgramFactory(
        name="Test Program",
        programme_code="1234",
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=Program.ACTIVE,
    )


@pytest.fixture
def create_payment_plan(create_test_program: Program) -> PaymentPlan:
    targeting_criteria = TargetingCriteriaFactory()
    TargetPopulationFactory(
        program=create_test_program,
        status=TargetPopulation.STATUS_OPEN,
        targeting_criteria=targeting_criteria,
    )
    tp = TargetPopulation.objects.first()
    payment_plan = PaymentPlan.objects.update_or_create(
        business_area=BusinessArea.objects.only("is_payment_plan_applicable").get(slug="afghanistan"),
        target_population=tp,
        start_date=datetime.now(),
        end_date=datetime.now() + relativedelta(days=30),
        currency="USD",
        dispersion_start_date=datetime.now(),
        dispersion_end_date=datetime.now() + relativedelta(days=14),
        status_date=datetime.now(),
        status=PaymentPlan.Status.ACCEPTED,
        created_by=User.objects.first(),
        program=tp.program,
        total_delivered_quantity=999,
        total_entitled_quantity=2999,
        is_follow_up=False,
        program_id=tp.program.id,
    )
    return payment_plan[0]


@pytest.mark.usefixtures("login")
class TestSmokePaymentModule:
    def test_smoke_payment_plan(self, create_payment_plan: PaymentPlan, pagePaymentModule: PaymentModule) -> None:
        pagePaymentModule.selectGlobalProgramFilter("Test Program").click()
        pagePaymentModule.getNavPaymentModule().click()
        assert "Payment Module" in pagePaymentModule.getPageHeaderTitle().text
        assert "NEW PAYMENT PLAN" in pagePaymentModule.getButtonNewPaymentPlan().text
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
        self, create_test_program: Program, pagePaymentModule: PaymentModule, pageNewPaymentPlan: NewPaymentPlan
    ) -> None:
        pagePaymentModule.selectGlobalProgramFilter("Test Program").click()
        pagePaymentModule.getNavPaymentModule().click()
        pagePaymentModule.getButtonNewPaymentPlan().click()

        assert "New Payment Plan" in pageNewPaymentPlan.getPageHeaderTitle().text
        assert "SAVE" in pageNewPaymentPlan.getButtonSavePaymentPlan().text
        assert "Target Population" in pageNewPaymentPlan.getInputTargetPopulation().text
        assert "Start Date*" in pageNewPaymentPlan.getInputStartDate().text
        assert "End Date*" in pageNewPaymentPlan.getInputEndDate().text
        assert "Currency" in pageNewPaymentPlan.getInputCurrency().text
        assert "Dispersion Start Date*" in pageNewPaymentPlan.getInputDispersionStartDate().text
        assert "Dispersion End Date*" in pageNewPaymentPlan.getInputDispersionEndDate().text

    def test_smoke_details_payment_plan(
        self,
        create_payment_plan: PaymentPlan,
        pagePaymentModule: PaymentModule,
        pagePaymentModuleDetails: PaymentModuleDetails,
    ) -> None:
        pagePaymentModule.selectGlobalProgramFilter("Test Program").click()
        pagePaymentModule.getNavPaymentModule().click()
        assert "NEW PAYMENT PLAN" in pagePaymentModule.getButtonNewPaymentPlan().text
        pagePaymentModule.getRow(0).click()
        assert "ACCEPTED" in pagePaymentModuleDetails.getStatusContainer().text
        assert "EXPORT XLSX" in pagePaymentModuleDetails.getButtonExportXlsx().text
        assert "Test Program" in pagePaymentModuleDetails.getLabelProgramme().text
        assert "USD" in pagePaymentModuleDetails.getLabelCurrency().text
        assert str((datetime.now()).strftime("%d %b %Y")) in pagePaymentModuleDetails.getLabelStartDate().text
        assert (
            str((datetime.now() + relativedelta(days=30)).strftime("%d %b %Y"))
            in pagePaymentModuleDetails.getLabelEndDate().text
        )
        assert str((datetime.now()).strftime("%d %b %Y")) in pagePaymentModuleDetails.getLabelDispersionStartDate().text
        assert (
            str((datetime.now() + relativedelta(days=14)).strftime("%d %b %Y"))
            in pagePaymentModuleDetails.getLabelDispersionEndDate().text
        )
        assert "-" in pagePaymentModuleDetails.getLabelRelatedFollowUpPaymentPlans().text
        assert "SET UP FSP" in pagePaymentModuleDetails.getButtonSetUpFsp().text
        assert "CREATE" in pagePaymentModuleDetails.getButtonCreateExclusions().text
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
        assert "FSP Auth Code" in pagePaymentModuleDetails.getTableLabel()[9].text
        assert "Reconciliation" in pagePaymentModuleDetails.getTableLabel()[10].text
