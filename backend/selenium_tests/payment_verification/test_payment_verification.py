from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta
from page_object.payment_verification.payment_verification import PaymentVerification
from page_object.payment_verification.payment_verification_details import (
    PaymentVerificationDetails,
)

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import (
    CashPlanFactory,
    PaymentRecordFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerification as PV
from hct_mis_api.apps.payment.models import PaymentVerificationPlan
from hct_mis_api.apps.payment.models import PaymentRecord as PR
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)
from selenium.webdriver.common.by import By

from page_object.payment_verification.payment_record import PaymentRecord

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def active_program() -> Program:
    return get_program_with_dct_type_and_name("Active Program", "ACTI", status=Program.ACTIVE)


def get_program_with_dct_type_and_name(
        name: str, programme_code: str, dct_type: str = DataCollectingType.Type.STANDARD, status: str = Program.ACTIVE
) -> Program:
    BusinessArea.objects.filter(slug="afghanistan").update(is_payment_plan_applicable=True)
    dct = DataCollectingTypeFactory(type=dct_type)
    program = ProgramFactory(
        name=name,
        programme_code=programme_code,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
    )
    return program


@pytest.fixture
def add_payment_verification() -> PV:
    registration_data_import = RegistrationDataImportFactory(
        imported_by=User.objects.first(), business_area=BusinessArea.objects.first()
    )
    program = Program.objects.filter(name="Active Program").first()
    household, individuals = create_household(
        {
            "registration_data_import": registration_data_import,
            "admin_area": Area.objects.order_by("?").first(),
            "program": program,
        },
        {"registration_data_import": registration_data_import},
    )

    cash_plan = CashPlanFactory(
        name="TEST",
        program=program,
        business_area=BusinessArea.objects.first(),
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
    )

    targeting_criteria = TargetingCriteriaFactory()

    target_population = TargetPopulationFactory(
        created_by=User.objects.first(),
        targeting_criteria=targeting_criteria,
        business_area=BusinessArea.objects.first(),
    )

    from hct_mis_api.apps.payment.models import GenericPayment
    payment_record = PaymentRecordFactory(
        parent=cash_plan,
        household=household,
        head_of_household=household.head_of_household,
        target_population=target_population,
        entitlement_quantity="21.36",
        delivered_quantity="21.36",
        currency="PLN",
        status=GenericPayment.STATUS_DISTRIBUTION_SUCCESS
    )
    payment_verification_plan = PaymentVerificationPlanFactory(
        generic_fk_obj=cash_plan, verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL
    )

    pv = PaymentVerificationFactory(
        generic_fk_obj=payment_record,
        payment_verification_plan=payment_verification_plan,
        status=PV.STATUS_PENDING,
    )
    return pv


@pytest.mark.usefixtures("login")
class TestSmokePaymentVerification:
    def test_smoke_payment_verification(
            self, active_program: Program, add_payment_verification: PV, pagePaymentVerification: PaymentVerification
    ) -> None:
        pagePaymentVerification.selectGlobalProgramFilter("Active Program").click()
        pagePaymentVerification.getNavPaymentVerification().click()
        assert "Payment Verification" in pagePaymentVerification.getPageHeaderTitle().text
        assert "List of Payment Plans" in pagePaymentVerification.getTableTitle().text
        assert "Payment Plan ID" in pagePaymentVerification.getUnicefid().text
        assert "Verification Status" in pagePaymentVerification.getVerificationstatus().text
        assert "Cash Amount" in pagePaymentVerification.getTotaldeliveredquantity().text
        assert "Timeframe" in pagePaymentVerification.getStartdate().text
        assert "Last Modified Date" in pagePaymentVerification.getUpdatedat().text
        assert "PP-0000-00-1122334" in pagePaymentVerification.getCashPlanTableRow().text
        assert "PENDING" in pagePaymentVerification.getStatusContainer().text
        assert "Rows per page: 5 1–1 of 1" in pagePaymentVerification.getTablePagination().text.replace("\n", " ")

    def test_smoke_payment_verification_details(
            self,
            active_program: Program,
            add_payment_verification: PV,
            pagePaymentVerification: PaymentVerification,
            pagePaymentVerificationDetails: PaymentVerificationDetails,
    ) -> None:
        pagePaymentVerification.selectGlobalProgramFilter("Active Program").click()
        pagePaymentVerification.getNavPaymentVerification().click()
        pagePaymentVerification.getCashPlanTableRow().click()
        assert "Payment Plan PP-0000-00-1122334" in pagePaymentVerificationDetails.getPageHeaderTitle().text
        assert "CREATE VERIFICATION PLAN" in pagePaymentVerificationDetails.getButtonNewPlan().text
        assert "Payment Plan Details" in pagePaymentVerificationDetails.getDivPaymentPlanDetails().text
        assert "Active Program" in pagePaymentVerificationDetails.getLabelProgrammeName().text
        pagePaymentVerificationDetails.getLabelPaymentRecords()
        pagePaymentVerificationDetails.getLabelStartDate()
        pagePaymentVerificationDetails.getLabelEndDate()
        pagePaymentVerificationDetails.getTableLabel()
        assert "0%" in pagePaymentVerificationDetails.getLabelSuccessful().text
        assert "0%" in pagePaymentVerificationDetails.getLabelErroneous().text
        assert "PENDING" in pagePaymentVerificationDetails.getLabelStatus().text
        assert "PENDING" in pagePaymentVerificationDetails.getVerificationPlansSummaryStatus().text
        assert (
                "ACTIVATION DATE -"
                in pagePaymentVerificationDetails.getLabelizedFieldContainerSummaryActivationDate().text.replace("\n",
                                                                                                                 " ")
        )
        assert "-" in pagePaymentVerificationDetails.getLabelActivationDate().text
        assert (
                "COMPLETION DATE -"
                in pagePaymentVerificationDetails.getLabelizedFieldContainerSummaryCompletionDate().text.replace("\n",
                                                                                                                 " ")
        )
        assert "-" in pagePaymentVerificationDetails.getLabelCompletionDate().text
        assert (
                "NUMBER OF VERIFICATION PLANS 1"
                in pagePaymentVerificationDetails.getLabelizedFieldContainerSummaryNumberOfPlans().text.replace("\n",
                                                                                                                " ")
        )
        assert "1" in pagePaymentVerificationDetails.getLabelNumberOfVerificationPlans().text
        assert "DELETE" in pagePaymentVerificationDetails.getButtonDeletePlan().text
        assert "EDIT" in pagePaymentVerificationDetails.getButtonEditPlan().text
        assert "ACTIVATE" in pagePaymentVerificationDetails.getButtonActivatePlan().text
        assert "PENDING" in pagePaymentVerificationDetails.getLabelStatus().text
        assert "PENDING" in pagePaymentVerificationDetails.getVerificationPlanStatus().text
        assert "MANUAL" in pagePaymentVerificationDetails.getLabelVerificationChannel().text
        assert "-" in pagePaymentVerificationDetails.getLabelActivationDate().text
        assert "-" in pagePaymentVerificationDetails.getLabelCompletionDate().text

    def test_happy_path_payment_verification(
            self,
            active_program: Program,
            add_payment_verification: PV,
            pagePaymentVerification: PaymentVerification,
            pagePaymentVerificationDetails: PaymentVerificationDetails,
            pagePaymentRecord: PaymentRecord,
    ) -> None:
        pagePaymentVerification.selectGlobalProgramFilter("Active Program").click()
        pagePaymentVerification.getNavPaymentVerification().click()
        pagePaymentVerification.getCashPlanTableRow().click()
        assert "1" in pagePaymentVerificationDetails.getLabelPaymentRecords().text
        assert (datetime.now() - relativedelta(months=1)).strftime(
            "%-d %b %Y") in pagePaymentVerificationDetails.getLabelStartDate().text
        assert (datetime.now() + relativedelta(months=1)).strftime(
            "%-d %b %Y") in pagePaymentVerificationDetails.getLabelEndDate().text
        assert "Bank reconciliation" in pagePaymentVerificationDetails.getTableLabel().text
        # activity date
        # completion date
        payment_verification = add_payment_verification.payment_verification_plan
        assert payment_verification.sampling.lower().replace("_", " ") in pagePaymentVerificationDetails.getLabelSampling().text.lower()
        assert str(payment_verification.responded_count) in pagePaymentVerificationDetails.getLabelResponded().text
        assert str(payment_verification.received_with_problems_count) in pagePaymentVerificationDetails.getLabelReceivedWithIssues().text
        assert str(payment_verification.sample_size) in pagePaymentVerificationDetails.getLabelSampleSize().text
        assert str(payment_verification.received_count) in pagePaymentVerificationDetails.getLabelReceived().text
        assert str(payment_verification.not_received_count) in pagePaymentVerificationDetails.getLabelNotReceived().text
        pagePaymentVerificationDetails.getButtonDeletePlan().click()
        pagePaymentVerificationDetails.getButtonSubmit().click()
        from time import sleep
        sleep(1)
        pagePaymentVerificationDetails.getButtonNewPlan().click()
        pagePaymentVerificationDetails.getButtonSubmit().click()

        pagePaymentVerificationDetails.getButtonActivatePlan().click()
        pagePaymentVerificationDetails.getButtonSubmit().click()

        pagePaymentVerificationDetails.getRows()[0].find_elements(By.TAG_NAME, "a")[0].click()
        payment_record = PR.objects.first()
        assert "Payment Record" in pagePaymentRecord.getPageHeaderTitle().text
        assert "VERIFY" in pagePaymentRecord.getButtonEdPlan().text
        assert "DELIVERED FULLY" in pagePaymentRecord.getLabelStatus().text
        assert "DELIVERED FULLY" in pagePaymentRecord.getStatusContainer().text
        assert "HH-0" in pagePaymentRecord.getLabelHousehold().text
        assert payment_record.target_population.name in pagePaymentRecord.getLabelTargetPopulation().text
        assert payment_record.distribution_modality in pagePaymentRecord.getLabelDistributionModality().text
        assert payment_record.status in pagePaymentRecord.getLabelStatus().text
        assert payment_record.payment_verification.status in pagePaymentRecord.getStatusContainer().text
        assert "PLN 0.00" in pagePaymentRecord.getLabelAmountReceived().text
        assert "HH-0" in pagePaymentRecord.getLabelHouseholdId().text
        assert "Scott Robert Oliver" in pagePaymentRecord.getLabelHeadOfHousehold().text
        assert "3" in pagePaymentRecord.getLabelTotalPersonCovered().text
        assert "+48609456000" in pagePaymentRecord.getLabelPhoneNumber().text
        assert "-" in pagePaymentRecord.getLabelAlt.PhoneNumber().text
        assert "21.36" in pagePaymentRecord.getLabelEntitlementQuantity().text
        assert "21.36" in pagePaymentRecord.getLabelDeliveredQuantity().text
        assert "PLN" in pagePaymentRecord.getLabelCurrency().text
        assert "-" in pagePaymentRecord.getLabelDeliveryType().text
        assert "13 May 2022" in pagePaymentRecord.getLabelDeliveryDate().text
        assert "151-41-7049" in pagePaymentRecord.getLabelEntitlementCardId().text
        assert "-" in pagePaymentRecord.getLabelTransactionReferenceId().text
        assert "25 Apr 2022" in pagePaymentRecord.getLabelEntitlementCardIssueDate().text
        assert "Sanchez, Cook and Jones" in pagePaymentRecord.getLabelFsp().text

        pagePaymentVerificationDetails.getButtonFinish().click()
        pagePaymentVerificationDetails.getButtonSubmit().click()
        pagePaymentVerificationDetails.screenshot("1")
