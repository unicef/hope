from decimal import Decimal

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
from hope.models import BusinessArea, Payment, PaymentPlan, Program

pytestmark = pytest.mark.django_db()


def _fill_date(browser: HopeTestBrowser, name: str, value: str) -> None:
    browser.fill_date(f'input[name="{name}"]', value)


def _create_source_plan(program: Program, *, payment_status: str) -> PaymentPlan:
    """ACCEPTED Standard (REGULAR) plan with a single payment in ``payment_status``.

    Top-up eligibility (``eligible_payments_for_top_up``) requires the source plan
    to be REGULAR with at least one payment in a delivered/pending status on a
    non-withdrawn household. Passing a delivered status makes the plan top-up
    eligible; passing an error status leaves it ineligible while still rendering
    the Accepted-state header buttons.
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
        status=PaymentPlan.Status.ACCEPTED,
    )

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
    )
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
def topup_ineligible_plan(topup_program: Program) -> PaymentPlan:
    # Errored payment is neither delivered nor pending → no eligible payments →
    # canCreateTopUp False, even though the Accepted-state header still renders.
    return _create_source_plan(topup_program, payment_status=Payment.STATUS_ERROR)


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
    login.click('[data-cy="button-submit"]')

    login.wait_for_text("Payment Plan Created")

    # A distinct Top-Up child plan is created and the UI navigates to its detail page.
    new_pp = PaymentPlan.objects.get(source_payment_plan=source, plan_type=PaymentPlan.PlanType.TOP_UP)
    assert new_pp.id != source.id
    # Header shows the Top-Up plan-type label (backend label) for the new plan;
    # waiting on it guarantees the navigation + render to the child plan completed.
    login.wait_for_text("Top Up", '[data-cy="page-header-title"]')
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
