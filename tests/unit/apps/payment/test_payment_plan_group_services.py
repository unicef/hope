import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    ProgramCycleFactory,
)
from extras.test_utils.factories.core import CurrencyFactory
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
)
from hope.apps.payment.services.payment_plan_group_services import PaymentPlanGroupService
from hope.models import PaymentPlan, PaymentPlanGroup

pytestmark = pytest.mark.django_db


@pytest.fixture
def cycle():
    return ProgramCycleFactory()


@pytest.fixture
def delivery_mechanism():
    return DeliveryMechanismFactory()


@pytest.fixture
def financial_service_provider(delivery_mechanism):
    fsp = FinancialServiceProviderFactory()
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
    )
    return fsp


@pytest.fixture
def currency():
    return CurrencyFactory()


@pytest.fixture
def open_group(cycle):
    return PaymentPlanGroupFactory(cycle=cycle, status=PaymentPlanGroup.Status.OPEN)


@pytest.fixture
def locked_payment_plan(cycle, open_group, financial_service_provider, delivery_mechanism, currency):
    return PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=open_group,
        status=PaymentPlan.Status.LOCKED,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=delivery_mechanism,
        currency=currency,
    )


def test_lock_sets_group_locked(open_group, locked_payment_plan):
    PaymentPlanGroupService(open_group).lock()

    open_group.refresh_from_db()
    assert open_group.status == PaymentPlanGroup.Status.LOCKED


def test_lock_sets_status_date(open_group, locked_payment_plan):
    PaymentPlanGroupService(open_group).lock()

    open_group.refresh_from_db()
    assert open_group.status_date is not None


def test_lock_locks_fsp_on_every_payment_plan(
    cycle, open_group, locked_payment_plan, financial_service_provider, delivery_mechanism, currency
):
    second_payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=open_group,
        status=PaymentPlan.Status.LOCKED,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=delivery_mechanism,
        currency=currency,
    )

    PaymentPlanGroupService(open_group).lock()

    locked_payment_plan.refresh_from_db()
    second_payment_plan.refresh_from_db()
    assert locked_payment_plan.status == PaymentPlan.Status.LOCKED_FSP
    assert second_payment_plan.status == PaymentPlan.Status.LOCKED_FSP


def test_lock_rejects_group_that_is_already_locked(cycle, locked_payment_plan):
    already_locked = locked_payment_plan.payment_plan_group
    already_locked.status = PaymentPlanGroup.Status.LOCKED
    already_locked.save(update_fields=["status"])

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(already_locked).lock()
    assert error.value.detail[0] == "Lock Payment Plan Group is possible only within Status OPEN"


def test_lock_rejects_group_without_payment_plans(open_group):
    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).lock()
    assert error.value.detail[0] == "Lock is not possible for a Payment Plan Group without Payment Plans."


def test_lock_rejects_payment_plan_that_is_not_locked(
    cycle, open_group, locked_payment_plan, financial_service_provider, delivery_mechanism, currency
):
    open_payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=open_group,
        status=PaymentPlan.Status.OPEN,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=delivery_mechanism,
        currency=currency,
    )

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).lock()
    assert error.value.detail[0] == (
        f"Every Payment Plan must be locked before the Payment Plan Group can be locked. "
        f"Not locked: {open_payment_plan.unicef_id}."
    )


def test_lock_rejects_payment_plans_with_different_fsps(
    cycle, open_group, locked_payment_plan, delivery_mechanism, currency
):
    other_fsp = FinancialServiceProviderFactory()
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=other_fsp,
        delivery_mechanism=delivery_mechanism,
    )
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=open_group,
        status=PaymentPlan.Status.LOCKED,
        financial_service_provider=other_fsp,
        delivery_mechanism=delivery_mechanism,
        currency=currency,
    )

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).lock()
    assert error.value.detail[0] == "Payment Plans in the group must share the same Financial Service Provider."


def test_lock_rejects_payment_plans_with_different_currencies(
    cycle, open_group, locked_payment_plan, financial_service_provider, delivery_mechanism
):
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=open_group,
        status=PaymentPlan.Status.LOCKED,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=delivery_mechanism,
        currency=CurrencyFactory(code="EUR", name="Euro"),
    )

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).lock()
    assert error.value.detail[0] == "Payment Plans in the group must share the same Currency."


def test_lock_rejects_payment_plan_without_delivery_template(
    cycle, open_group, locked_payment_plan, financial_service_provider, currency
):
    payment_plan_without_template = PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=open_group,
        status=PaymentPlan.Status.LOCKED,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=DeliveryMechanismFactory(),
        currency=currency,
    )

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).lock()
    assert error.value.detail[0] == (
        f"Every Payment Plan needs an FSP XLSX Template for its Financial Service Provider and "
        f"Delivery Mechanism. Missing for: {payment_plan_without_template.unicef_id}."
    )


def test_unlock_sets_group_open(open_group, locked_payment_plan):
    PaymentPlanGroupService(open_group).lock()

    PaymentPlanGroupService(open_group).unlock()

    open_group.refresh_from_db()
    assert open_group.status == PaymentPlanGroup.Status.OPEN


def test_unlock_releases_fsp_lock_on_every_payment_plan(open_group, locked_payment_plan):
    PaymentPlanGroupService(open_group).lock()

    PaymentPlanGroupService(open_group).unlock()

    locked_payment_plan.refresh_from_db()
    assert locked_payment_plan.status == PaymentPlan.Status.LOCKED


def test_unlock_rejects_group_that_is_open(open_group, locked_payment_plan):
    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).unlock()
    assert error.value.detail[0] == "Unlock Payment Plan Group is possible only within Status LOCKED"
