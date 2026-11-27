from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
import uuid

import openpyxl
import pytest

from extras.test_utils.factories import (
    CurrencyFactory,
    DataCollectingTypeFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import (
    BeneficiaryGroup,
    BusinessArea,
    DataCollectingType,
    Payment,
    PaymentPlan,
    PaymentVerification,
    PaymentVerificationPlan,
    Program,
)

PROGRAM_NAME = "Active Program"
DELIVERED_QUANTITY = Decimal("21.36")
PLAN_STATUS = 'div[data-cy="verification-plan-status"]'
BUTTON_SUBMIT = 'button[data-cy="button-submit"]'
BUTTON_ACTIVATE = 'button[data-cy="button-activate-plan"]'
RECORD_STATUS = 'tr[role="checkbox"] div[data-cy="status-container"]'


@pytest.fixture
def pending_verification_payment_plan(business_area: BusinessArea) -> PaymentPlan:
    """FINISHED payment plan in an ACTIVE program with a single PENDING verification plan.

    The MANUAL verification channel is used on purpose: it keeps activation deterministic
    by skipping the RapidPro path entirely (no external service to mock). The program must
    be ACTIVE so the frontend Activate button is enabled (it is disabled otherwise).
    """
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    payment_plan = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=program.cycles.first(),
        status=PaymentPlan.Status.FINISHED,
        financial_service_provider=FinancialServiceProviderFactory(),
        delivery_mechanism=DeliveryMechanismFactory(),
    )
    PaymentVerificationPlanFactory(
        payment_plan=payment_plan,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL,
        sampling="FULL_LIST",
    )
    return payment_plan


@pytest.fixture
def verification_program(business_area: BusinessArea) -> Program:
    return ProgramFactory(
        name=PROGRAM_NAME,
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=DataCollectingTypeFactory(type=DataCollectingType.Type.STANDARD),
        beneficiary_group=BeneficiaryGroup.objects.get(name="Main Menu"),
    )


def create_verification(program: Program, channel: str) -> PaymentVerification:
    """One distributed payment in a FINISHED payment plan with a PENDING verification plan."""
    delivery_mechanism = DeliveryMechanismFactory(code="cash", name="Cash")
    fsp = FinancialServiceProviderFactory(name="Verification FSP")
    fsp.delivery_mechanisms.set([delivery_mechanism])
    payment_plan = PaymentPlanFactory(
        name="TEST",
        status=PaymentPlan.Status.FINISHED,
        program_cycle=program.cycles.first(),
        business_area=program.business_area,
        start_date=date.today() - timedelta(days=30),
        end_date=date.today() + timedelta(days=30),
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
    )
    payment = PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=DELIVERED_QUANTITY,
        delivered_quantity=DELIVERED_QUANTITY,
        currency=CurrencyFactory(code="PLN"),
        delivery_type=delivery_mechanism,
        financial_service_provider=fsp,
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )
    verification_plan = PaymentVerificationPlanFactory(
        payment_plan=payment_plan,
        verification_channel=channel,
        sampling="FULL_LIST",
        sample_size=0,
        responded_count=0,
        received_count=0,
        not_received_count=0,
        received_with_problems_count=0,
    )
    # The export file is named after the plan's unicef_id and every xdist worker's database starts
    # at PVP-1, while browser downloads share one folder: a unique id keeps workers' files apart.
    verification_plan.unicef_id = f"PVP-{uuid.uuid4().hex[:8].upper()}"
    verification_plan.save(update_fields=["unicef_id"])
    return PaymentVerificationFactory(
        payment=payment,
        payment_verification_plan=verification_plan,
        status=PaymentVerification.STATUS_PENDING,
    )


@pytest.fixture
def manual_verification(verification_program: Program) -> PaymentVerification:
    return create_verification(verification_program, PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL)


@pytest.fixture
def xlsx_verification(verification_program: Program) -> PaymentVerification:
    return create_verification(verification_program, PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX)


def verification_url(payment_plan: PaymentPlan) -> str:
    program = payment_plan.program_cycle.program
    return (
        f"/{payment_plan.business_area.slug}/programs/{program.code}"
        f"/payment-verification/payment-plan/{payment_plan.id}"
    )


def activate_plan(browser: HopeTestBrowser, payment_plan: PaymentPlan) -> None:
    browser.open(verification_url(payment_plan))
    browser.wait_for_element_clickable(BUTTON_ACTIVATE).click()
    browser.wait_for_element_clickable(BUTTON_SUBMIT).click()
    browser.wait_for_text("ACTIVE", PLAN_STATUS)


def export_and_download_xlsx(browser: HopeTestBrowser, verification_plan: PaymentVerificationPlan) -> Path:
    browser.wait_for_element_clickable('button[data-cy="export-xlsx"]').click()
    # Celery runs eagerly, so the file exists once the export request returns; the page polls for it.
    download = browser.wait_for_element_clickable('button[data-cy="download-xlsx"]', timeout=30)
    filename = Path(verification_plan.get_xlsx_verification_file.file.name).name
    browser.delete_downloaded_file_if_present(filename, browser=True)
    download.click()
    browser.assert_downloaded_file(filename, browser=True)
    return Path(browser.get_path_of_downloaded_file(filename, browser=True))


def fill_verification_xlsx(source: Path, target: Path, received: str, received_amount: Decimal) -> None:
    workbook = openpyxl.load_workbook(source)
    sheet = workbook["Payment Verifications"]
    headers = [cell.value for cell in sheet[1]]
    sheet.cell(row=2, column=headers.index("received") + 1).value = received
    sheet.cell(row=2, column=headers.index("received_amount") + 1).value = float(received_amount)
    workbook.save(target)


def import_xlsx(browser: HopeTestBrowser, path: Path) -> None:
    browser.wait_for_element_clickable('div[data-cy="import-xlsx"] button[data-cy="button-import"]').click()
    browser.choose_file('div[role="dialog"] input[data-cy="file-input"]', str(path))
    browser.wait_for_element_clickable('button[data-cy="button-import-entitlement"]').click()
    browser.wait_for_text("Your import was successful!")
