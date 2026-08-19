from collections.abc import Sequence
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
from hope.models import BusinessArea, DeliveryMechanism, Payment, PaymentPlan, Program

pytestmark = pytest.mark.django_db()


def _fill_date(browser: HopeTestBrowser, name: str, value: str) -> None:
    browser.fill_date(f'input[name="{name}"]', value)


def _fill_fixed_amount(browser: HopeTestBrowser, amount: str) -> None:
    # FormikTextField derives its data-cy from the field name.
    field = browser.wait_for_element_clickable('input[data-cy="input-fixedAmount"]')
    field.click()
    field.send_keys(amount)


def _amount_file_funding_first_beneficiary(source_plan: PaymentPlan) -> str:
    """Amount template funding only the first of three eligible beneficiaries. Returns its path.

    The second row carries an explicit zero and the third is left blank: both mean "not part of
    this Top-Up", and the two are worth distinguishing because only the zero is something the
    operator actually typed.
    """
    workbook = TopUpAmountTemplateService(source_plan).generate_workbook()
    worksheet = workbook.active
    headers = [cell.value for cell in worksheet[1]]
    amount_column = headers.index(XlsxPaymentPlanBaseService.COLUMN_ENTITLEMENT_QUANTITY) + 1
    worksheet.cell(row=2, column=amount_column).value = 40
    worksheet.cell(row=3, column=amount_column).value = 0
    with NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        workbook.save(tmp.name)
        return tmp.name


def _create_source_plan(
    program: Program,
    *,
    payment_statuses: Sequence[str],
    plan_status: str = PaymentPlan.Status.ACCEPTED,
    excluded: bool = False,
) -> PaymentPlan:
    """Released Standard (REGULAR) plan with one payment per entry in ``payment_statuses``.

    Top-up eligibility requires a REGULAR plan in Accepted or Finished status with at least one
    payment on a non-withdrawn household. Payment status does not gate it — pass ``excluded`` to
    build a plan with nobody left to top up.
    """
    ba = program.business_area
    currency = CurrencyFactory(code="USD")
    # payment_gateway_id is unique, so a second plan in the same test has to reuse the mechanism.
    delivery_mechanism = DeliveryMechanism.objects.filter(code="dm-topup-cash").first() or DeliveryMechanismFactory(
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

    for payment_status in payment_statuses:
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
    return _create_source_plan(topup_program, payment_statuses=[Payment.STATUS_SUCCESS])


@pytest.fixture
def topup_finished_plan_with_mixed_payments(topup_program: Program) -> PaymentPlan:
    # Neither the payment status nor the plan having moved past Accepted disqualifies anybody.
    return _create_source_plan(
        topup_program,
        payment_statuses=[Payment.STATUS_SUCCESS, Payment.STATUS_PENDING, Payment.STATUS_ERROR],
        plan_status=PaymentPlan.Status.FINISHED,
    )


@pytest.fixture
def mixed_plan_amount_file(topup_finished_plan_with_mixed_payments: PaymentPlan) -> str:
    return _amount_file_funding_first_beneficiary(topup_finished_plan_with_mixed_payments)


@pytest.fixture
def topup_ineligible_plan(topup_program: Program) -> PaymentPlan:
    return _create_source_plan(topup_program, payment_statuses=[Payment.STATUS_SUCCESS], excluded=True)


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
    login.wait_for_element_clickable('[data-cy="button-create-topup"]').click()

    login.wait_for_element_visible('input[name="dispersionStartDate"]')
    # Both labels are asserted because a trailing colon inside t() is swallowed by i18next,
    # which silently renders an empty label.
    login.assert_text("Fixed:")
    login.assert_text("Custom / per Beneficiary:")
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


def test_create_top_up_from_finished_plan_with_mixed_payment_statuses(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    topup_program: Program,
    topup_finished_plan_with_mixed_payments: PaymentPlan,
) -> None:
    """Delivered, pending and failed are all topped up alike when a flat amount is given."""
    source = topup_finished_plan_with_mixed_payments
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
    topup_finished_plan_with_mixed_payments: PaymentPlan,
    mixed_plan_amount_file: str,
) -> None:
    """Only rows carrying a positive amount are funded; a zero and a blank both stay out."""
    source = topup_finished_plan_with_mixed_payments
    amount_file = mixed_plan_amount_file
    base_url = f"/{business_area.slug}/programs/{topup_program.code}"

    login.open(f"{base_url}/payment-module/payment-plans/{source.id}")
    login.wait_for_text(source.unicef_id, '[data-cy="pp-unicef-id"]')
    login.wait_for_element_clickable('[data-cy="button-create-topup"]').click()

    login.wait_for_element_visible('input[name="dispersionStartDate"]')
    _fill_date(login, "dispersionStartDate", "2027-01-01")
    login.wait_for_element_clickable('input[name="dispersionEndDate"]')
    _fill_date(login, "dispersionEndDate", "2027-12-31")
    # The file wins on submit, so a fixed amount typed first must not survive the upload.
    _fill_fixed_amount(login, "25")
    login.choose_file('input[type="file"]', amount_file)
    # The count is read from the workbook in the browser, before anything is sent.
    login.wait_for_text("New Top-Up will be created for 1 payment", '[data-cy="top-up-funded-rows"]')
    login.assert_value('input[data-cy="input-fixedAmount"]', "")
    login.assert_attribute('input[data-cy="input-fixedAmount"]', "disabled")
    # Clearing the amount must not leave its error standing next to a file that satisfies it.
    login.assert_text_not_visible("Enter a fixed amount or upload an amount file")
    login.click('[data-cy="button-submit"]')

    login.wait_for_text("Payment Plan Created")
    top_up = PaymentPlan.objects.get(source_payment_plan=source, plan_type=PaymentPlan.PlanType.TOP_UP)
    assert top_up.payment_items.count() == 1
    assert top_up.payment_items.first().entitlement_quantity == Decimal("40.00")
    assert source.eligible_payments_for_top_up().count() == 2


def test_top_up_dialog_without_dispersion_dates_shows_validation_errors(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    topup_program: Program,
    topup_eligible_plan: PaymentPlan,
) -> None:
    """Submitting with the required dates empty must say so rather than sit silent."""
    source = topup_eligible_plan
    base_url = f"/{business_area.slug}/programs/{topup_program.code}"

    login.open(f"{base_url}/payment-module/payment-plans/{source.id}")
    login.wait_for_text(source.unicef_id, '[data-cy="pp-unicef-id"]')
    login.wait_for_element_clickable('[data-cy="button-create-topup"]').click()

    login.wait_for_element_visible('input[name="dispersionStartDate"]')
    _fill_fixed_amount(login, "25")
    login.click('[data-cy="button-submit"]')

    login.assert_text("Dispersion Start Date is required")


def test_top_up_requires_a_fixed_amount_or_an_amount_file(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    topup_program: Program,
    topup_eligible_plan: PaymentPlan,
) -> None:
    """Submitting with neither funding source is caught in the dialog, not by the server."""
    source = topup_eligible_plan
    base_url = f"/{business_area.slug}/programs/{topup_program.code}"

    login.open(f"{base_url}/payment-module/payment-plans/{source.id}")
    login.wait_for_text(source.unicef_id, '[data-cy="pp-unicef-id"]')
    login.wait_for_element_clickable('[data-cy="button-create-topup"]').click()

    login.wait_for_element_visible('input[name="dispersionStartDate"]')
    _fill_date(login, "dispersionStartDate", "2027-01-01")
    login.wait_for_element_clickable('input[name="dispersionEndDate"]')
    _fill_date(login, "dispersionEndDate", "2027-12-31")
    login.click('[data-cy="button-submit"]')

    login.wait_for_text("Enter a fixed amount or upload an amount file")
    assert not PaymentPlan.objects.filter(source_payment_plan=source, plan_type=PaymentPlan.PlanType.TOP_UP).exists()


@pytest.fixture
def topup_plan_with_pending_payments(topup_program: Program, topup_eligible_plan: PaymentPlan) -> PaymentPlan:
    """An Accepted Top-Up whose own payments are still pending — already amendable."""
    top_up = _create_source_plan(topup_program, payment_statuses=[Payment.STATUS_PENDING] * 2)
    top_up.plan_type = PaymentPlan.PlanType.TOP_UP
    top_up.source_payment_plan = topup_eligible_plan
    top_up.save(update_fields=["plan_type", "source_payment_plan"])
    return top_up


@pytest.fixture
def pending_top_up_amount_file(topup_plan_with_pending_payments: PaymentPlan) -> str:
    return _amount_file_funding_first_beneficiary(topup_plan_with_pending_payments)


def test_create_top_up_amendment_from_pending_top_up(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    topup_program: Program,
    topup_plan_with_pending_payments: PaymentPlan,
) -> None:
    """The Amendment dialog funds the same two ways a Top-Up does, on payments of any status."""
    source = topup_plan_with_pending_payments
    base_url = f"/{business_area.slug}/programs/{topup_program.code}"

    login.open(f"{base_url}/payment-module/payment-plans/{source.id}")
    login.wait_for_text(source.unicef_id, '[data-cy="pp-unicef-id"]')
    login.wait_for_element_clickable('[data-cy="button-create-amendment"]').click()

    login.wait_for_element_visible('input[name="dispersionStartDate"]')
    # The amount section is the Top-Up one, reused verbatim.
    login.assert_text("Fixed:")
    login.assert_text("Custom / per Beneficiary:")
    _fill_date(login, "dispersionStartDate", "2027-01-01")
    login.wait_for_element_clickable('input[name="dispersionEndDate"]')
    _fill_date(login, "dispersionEndDate", "2027-12-31")
    _fill_fixed_amount(login, "30")
    login.click('[data-cy="button-submit"]')

    login.wait_for_text("Payment Plan Created")
    amendment = PaymentPlan.objects.get(source_payment_plan=source, plan_type=PaymentPlan.PlanType.TOP_UP_AMENDMENT)
    assert amendment.payment_items.count() == 2
    assert set(amendment.payment_items.values_list("entitlement_quantity", flat=True)) == {Decimal("30.00")}


def test_create_second_top_up_for_the_beneficiaries_left_over(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    topup_program: Program,
    topup_finished_plan_with_mixed_payments: PaymentPlan,
    mixed_plan_amount_file: str,
) -> None:
    """Beneficiaries left out of the first Top-Up can be picked up by a second one."""
    source = topup_finished_plan_with_mixed_payments
    amount_file = mixed_plan_amount_file
    plan_url = f"/{business_area.slug}/programs/{topup_program.code}/payment-module/payment-plans/{source.id}"

    login.open(plan_url)
    login.wait_for_text(source.unicef_id, '[data-cy="pp-unicef-id"]')
    login.wait_for_element_clickable('[data-cy="button-create-topup"]').click()
    login.wait_for_element_visible('input[name="dispersionStartDate"]')
    _fill_date(login, "dispersionStartDate", "2027-01-01")
    login.wait_for_element_clickable('input[name="dispersionEndDate"]')
    _fill_date(login, "dispersionEndDate", "2027-12-31")
    login.choose_file('input[type="file"]', amount_file)
    login.click('[data-cy="button-submit"]')
    login.wait_for_text("Payment Plan Created")

    # Back on the source plan the action is still offered, because two beneficiaries are free.
    login.open(plan_url)
    login.wait_for_text(source.unicef_id, '[data-cy="pp-unicef-id"]')
    login.wait_for_element_clickable('[data-cy="button-create-topup"]').click()
    login.wait_for_element_visible('input[name="dispersionStartDate"]')
    _fill_date(login, "dispersionStartDate", "2027-01-01")
    login.wait_for_element_clickable('input[name="dispersionEndDate"]')
    _fill_date(login, "dispersionEndDate", "2027-12-31")
    _fill_fixed_amount(login, "15")
    login.click('[data-cy="button-submit"]')
    login.wait_for_text("Payment Plan Created")

    first, second = PaymentPlan.objects.filter(
        source_payment_plan=source, plan_type=PaymentPlan.PlanType.TOP_UP
    ).order_by("created_at")
    assert first.payment_items.count() == 1
    assert second.payment_items.count() == 2
    assert not set(first.payment_items.values_list("household_id", flat=True)) & set(
        second.payment_items.values_list("household_id", flat=True)
    )
    assert source.eligible_payments_for_top_up().count() == 0


@pytest.fixture
def topup_plan_with_failed_payments(topup_program: Program, topup_eligible_plan: PaymentPlan) -> PaymentPlan:
    """A Finished Top-Up whose own payments failed — the raw material for a Follow-Up."""
    top_up = _create_source_plan(
        topup_program,
        payment_statuses=[Payment.STATUS_ERROR] * 2,
        plan_status=PaymentPlan.Status.FINISHED,
    )
    top_up.plan_type = PaymentPlan.PlanType.TOP_UP
    top_up.source_payment_plan = topup_eligible_plan
    top_up.save(update_fields=["plan_type", "source_payment_plan"])
    return top_up


def test_create_follow_up_from_top_up_with_failed_payments(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    topup_program: Program,
    topup_plan_with_failed_payments: PaymentPlan,
) -> None:
    """A Top-Up is an ordinary plan for Follow-Up purposes: its failures can be retried."""
    source = topup_plan_with_failed_payments
    base_url = f"/{business_area.slug}/programs/{topup_program.code}"

    login.open(f"{base_url}/payment-module/payment-plans/{source.id}")
    login.wait_for_text(source.unicef_id, '[data-cy="pp-unicef-id"]')
    login.wait_for_element_clickable('[data-cy="button-create-followup"]').click()

    login.wait_for_element_visible('input[name="dispersionStartDate"]')
    _fill_date(login, "dispersionStartDate", "2027-01-01")
    login.wait_for_element_clickable('input[name="dispersionEndDate"]')
    _fill_date(login, "dispersionEndDate", "2027-12-31")
    login.click('[data-cy="button-submit"]')

    login.wait_for_text("Payment Plan Created")
    follow_up = PaymentPlan.objects.get(source_payment_plan=source, plan_type=PaymentPlan.PlanType.FOLLOW_UP)
    assert follow_up.payment_items.count() == 2


def test_create_top_up_amendment_with_amount_file(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    topup_program: Program,
    topup_plan_with_pending_payments: PaymentPlan,
    pending_top_up_amount_file: str,
) -> None:
    """The Amendment upload goes out through its own generated client, so it is worth its own run."""
    source = topup_plan_with_pending_payments
    amount_file = pending_top_up_amount_file
    base_url = f"/{business_area.slug}/programs/{topup_program.code}"

    login.open(f"{base_url}/payment-module/payment-plans/{source.id}")
    login.wait_for_text(source.unicef_id, '[data-cy="pp-unicef-id"]')
    login.wait_for_element_clickable('[data-cy="button-create-amendment"]').click()

    login.wait_for_element_visible('input[name="dispersionStartDate"]')
    _fill_date(login, "dispersionStartDate", "2027-01-01")
    login.wait_for_element_clickable('input[name="dispersionEndDate"]')
    _fill_date(login, "dispersionEndDate", "2027-12-31")
    login.choose_file('input[type="file"]', amount_file)
    login.wait_for_text("New Top-Up Amendment will be created for 1 payment", '[data-cy="top-up-funded-rows"]')
    login.click('[data-cy="button-submit"]')

    login.wait_for_text("Payment Plan Created")
    amendment = PaymentPlan.objects.get(source_payment_plan=source, plan_type=PaymentPlan.PlanType.TOP_UP_AMENDMENT)
    assert amendment.payment_items.count() == 1
    assert amendment.payment_items.first().entitlement_quantity == Decimal("40.00")
    assert source.eligible_payments_for_top_up_amendment().count() == 1
