from decimal import Decimal
from tempfile import NamedTemporaryFile

import pytest

from extras.test_utils.factories import (
    CurrencyFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentHouseholdSnapshotFactory,
    PaymentPlanFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.payment.services.top_up_amount_service import TopUpAmountTemplateService
from hope.apps.payment.xlsx.xlsx_payment_plan_base_service import XlsxPaymentPlanBaseService
from hope.models import BusinessArea, Payment, PaymentPlan, Program

pytestmark = pytest.mark.django_db()


def _fill_date(browser: HopeTestBrowser, name: str, value: str) -> None:
    browser.fill_date(f'input[name="{name}"]', value)


def _fill_fixed_amount(browser: HopeTestBrowser, amount: str) -> None:
    # FormikTextField derives its data-cy from the field name.
    field = browser.wait_for_element_clickable('input[data-cy="input-fixedAmount"]')
    field.click()
    field.send_keys(amount)


def _amount_file_funding_first_beneficiary(source_plan: PaymentPlan) -> str:
    """Write an amount template funding only the first eligible beneficiary. Returns its path."""
    workbook = TopUpAmountTemplateService(source_plan).generate_workbook()
    worksheet = workbook.active
    headers = [cell.value for cell in worksheet[1]]
    amount_column = headers.index(XlsxPaymentPlanBaseService.COLUMN_ENTITLEMENT_QUANTITY) + 1
    worksheet.cell(row=2, column=amount_column).value = 40
    with NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        workbook.save(tmp.name)
        return tmp.name


def _create_source_plan(
    program: Program,
    *,
    payment_status: str,
    plan_status: str = PaymentPlan.Status.ACCEPTED,
    payments: int = 1,
    excluded: bool = False,
) -> PaymentPlan:
    """Released Standard (REGULAR) plan with ``payments`` payments in ``payment_status``.

    Top-up eligibility requires a REGULAR plan in Accepted or Finished status with at least one
    payment on a non-withdrawn household. Payment status does not gate it — pass ``excluded`` to
    build a plan with nobody left to top up.
    """
    ba = program.business_area
    currency = CurrencyFactory(code="USD")
    delivery_mechanism = DeliveryMechanismFactory(
        code="dm-topup-cash", name="TopUp Cash", payment_gateway_id="dm-topup-cash"
    )
    fsp = FinancialServiceProviderFactory()
    fsp.delivery_mechanisms.add(delivery_mechanism)
    cycle = ProgramCycleFactory(program=program)

    plan = PaymentPlanFactory(
        name="Top-Up Source Plan",
        program_cycle=cycle,
        business_area=ba,
        currency=currency,
        delivery_mechanism=delivery_mechanism,
        financial_service_provider=fsp,
        plan_type=PaymentPlan.PlanType.REGULAR,
        status=plan_status,
    )

    for _ in range(payments):
        household = HouseholdFactory(business_area=ba, program=program)
        payment = PaymentFactory(
            parent=plan,
            household=household,
            collector=household.head_of_household,
            head_of_household=household.head_of_household,
            program=program,
            currency=currency,
            delivery_type=delivery_mechanism,
            financial_service_provider=fsp,
            entitlement_quantity=Decimal("100.00"),
            entitlement_quantity_usd=Decimal("100.00"),
            delivered_quantity=Decimal("100.00"),
            status=payment_status,
            excluded=excluded,
        )
        # The amount template renders from snapshots, which a released plan always carries.
        PaymentHouseholdSnapshotFactory(
            payment=payment,
            snapshot_data={
                "unicef_id": household.unicef_id,
                "size": household.size,
                "primary_collector": {
                    "unicef_id": household.head_of_household.unicef_id,
                    "full_name": household.head_of_household.full_name,
                },
                "alternate_collector": {},
            },
        )
    return plan


@pytest.fixture
def topup_program(business_area: BusinessArea) -> Program:
    return ProgramFactory(
        name="Top-Up E2E Program",
        status=Program.ACTIVE,
        business_area=business_area,
    )


@pytest.fixture
def topup_eligible_plan(topup_program: Program) -> PaymentPlan:
    # Delivered payment → eligible_payments_for_top_up() non-empty → canCreateTopUp True.
    return _create_source_plan(topup_program, payment_status=Payment.STATUS_SUCCESS)


@pytest.fixture
def topup_finished_plan_with_failed_payments(topup_program: Program) -> PaymentPlan:
    # Finished plan whose payments all failed: still top-up eligible, since neither the plan
    # status past Accepted nor a failed payment status disqualifies a beneficiary.
    return _create_source_plan(
        topup_program,
        payment_status=Payment.STATUS_ERROR,
        plan_status=PaymentPlan.Status.FINISHED,
        payments=3,
    )


@pytest.fixture
def topup_ineligible_plan(topup_program: Program) -> PaymentPlan:
    # Excluded payment → no eligible payments → canCreateTopUp False, even though the
    # Accepted-state header still renders.
    return _create_source_plan(topup_program, payment_status=Payment.STATUS_SUCCESS, excluded=True)


def test_create_top_up_payment_plan(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    topup_program: Program,
    topup_eligible_plan: PaymentPlan,
) -> None:
    source = topup_eligible_plan
    base_url = f"/{business_area.slug}/programs/{topup_program.code}"

    login.open(f"{base_url}/payment-module/payment-plans/{source.id}")
    login.wait_for_text(source.unicef_id, '[data-cy="pp-unicef-id"]')
    login.wait_for_text("ACCEPTED")

    # Top-up creation is a Payment-Plan-level action, available only on an
    # Accepted/Finished Standard plan with eligible payments.
    login.wait_for_element_clickable('[data-cy="button-create-topup"]')
    login.click('[data-cy="button-create-topup"]')

    login.wait_for_element_visible('input[name="dispersionStartDate"]')
    _fill_date(login, "dispersionStartDate", "2027-01-01")
    # The end date is disabled until a start date is set.
    login.wait_for_element_clickable('input[name="dispersionEndDate"]')
    _fill_date(login, "dispersionEndDate", "2027-12-31")
    _fill_fixed_amount(login, "25")
    login.click('[data-cy="button-submit"]')

    login.wait_for_text("Payment Plan Created")

    # A distinct Top-Up child plan is created and the UI navigates to its detail page.
    new_pp = PaymentPlan.objects.get(source_payment_plan=source, plan_type=PaymentPlan.PlanType.TOP_UP)
    assert new_pp.id != source.id
    # Waiting on the new plan's unicef_id in the header guarantees the navigation +
    # render to the child plan completed. It comes from the primary plan query, so
    # unlike the plan-type label (a separate async choices request) it can't race.
    login.wait_for_text(new_pp.unicef_id, '[data-cy="pp-unicef-id"]')
    assert str(new_pp.id) in login.get_current_url()


def test_top_up_button_hidden_when_no_eligible_payments(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    topup_program: Program,
    topup_ineligible_plan: PaymentPlan,
) -> None:
    source = topup_ineligible_plan
    base_url = f"/{business_area.slug}/programs/{topup_program.code}"

    login.open(f"{base_url}/payment-module/payment-plans/{source.id}")
    login.wait_for_text(source.unicef_id, '[data-cy="pp-unicef-id"]')
    login.wait_for_text("ACCEPTED")

    # Accepted-state header renders, but the Top-Up action is gated by canCreateTopUp.
    login.assert_element_absent('[data-cy="button-create-topup"]')


def test_create_top_up_from_finished_plan_with_failed_payments(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    topup_program: Program,
    topup_finished_plan_with_failed_payments: PaymentPlan,
) -> None:
    """A Finished plan whose payments all failed can still be topped up, funded by a flat amount."""
    source = topup_finished_plan_with_failed_payments
    base_url = f"/{business_area.slug}/programs/{topup_program.code}"

    login.open(f"{base_url}/payment-module/payment-plans/{source.id}")
    login.wait_for_text(source.unicef_id, '[data-cy="pp-unicef-id"]')
    login.wait_for_element_clickable('[data-cy="button-create-topup"]').click()

    login.wait_for_element_visible('input[name="dispersionStartDate"]')
    _fill_date(login, "dispersionStartDate", "2027-01-01")
    login.wait_for_element_clickable('input[name="dispersionEndDate"]')
    _fill_date(login, "dispersionEndDate", "2027-12-31")
    _fill_fixed_amount(login, "25")
    login.click('[data-cy="button-submit"]')

    login.wait_for_text("Payment Plan Created")
    top_up = PaymentPlan.objects.get(source_payment_plan=source, plan_type=PaymentPlan.PlanType.TOP_UP)
    assert top_up.payment_items.count() == 3
    assert set(top_up.payment_items.values_list("entitlement_quantity", flat=True)) == {Decimal("25.00")}


def test_create_top_up_with_amount_file_funds_only_listed_beneficiaries(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    topup_program: Program,
    topup_finished_plan_with_failed_payments: PaymentPlan,
) -> None:
    """The uploaded template funds only the rows carrying an amount; the rest stay available."""
    source = topup_finished_plan_with_failed_payments
    amount_file = _amount_file_funding_first_beneficiary(source)
    base_url = f"/{business_area.slug}/programs/{topup_program.code}"

    login.open(f"{base_url}/payment-module/payment-plans/{source.id}")
    login.wait_for_text(source.unicef_id, '[data-cy="pp-unicef-id"]')
    login.wait_for_element_clickable('[data-cy="button-create-topup"]').click()

    login.wait_for_element_visible('input[name="dispersionStartDate"]')
    _fill_date(login, "dispersionStartDate", "2027-01-01")
    login.wait_for_element_clickable('input[name="dispersionEndDate"]')
    _fill_date(login, "dispersionEndDate", "2027-12-31")
    login.choose_file('input[type="file"]', amount_file)
    login.click('[data-cy="button-submit"]')

    login.wait_for_text("Payment Plan Created")
    top_up = PaymentPlan.objects.get(source_payment_plan=source, plan_type=PaymentPlan.PlanType.TOP_UP)
    assert top_up.payment_items.count() == 1
    assert top_up.payment_items.first().entitlement_quantity == Decimal("40.00")
    assert source.eligible_payments_for_top_up().count() == 2
