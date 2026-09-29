from unittest.mock import patch

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
from hope.models import DeliveryMechanism, PaymentPlan, PaymentPlanGroup

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
def open_group(cycle, financial_service_provider, currency):
    return PaymentPlanGroupFactory(
        cycle=cycle,
        status=PaymentPlanGroup.Status.OPEN,
        financial_service_provider=financial_service_provider,
        currency=currency,
    )


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


def test_lock_rejects_group_without_fsp(open_group, locked_payment_plan):
    open_group.financial_service_provider = None
    open_group.save(update_fields=["financial_service_provider"])

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).lock()
    assert error.value.detail[0] == "Payment Plan Group needs a Financial Service Provider before it can be locked."


def test_lock_rejects_group_without_currency(open_group, locked_payment_plan):
    open_group.currency = None
    open_group.save(update_fields=["currency"])

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).lock()
    assert error.value.detail[0] == "Payment Plan Group needs a Currency before it can be locked."


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


def test_assign_fsp_copies_it_to_open_target_populations(cycle):
    group = PaymentPlanGroupFactory(cycle=cycle)
    target_population = PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.TP_OPEN,
        financial_service_provider=None,
    )
    fsp = FinancialServiceProviderFactory()

    PaymentPlanGroupService(group).assign_financial_service_provider(fsp)
    group.save()

    target_population.refresh_from_db()
    assert group.financial_service_provider == fsp
    assert target_population.financial_service_provider == fsp


@patch("hope.apps.payment.services.payment_plan_services.payment_plan_full_rebuild_async_task")
def test_assign_fsp_rebuilds_every_target_population(mock_full_rebuild, cycle, django_capture_on_commit_callbacks):
    group = PaymentPlanGroupFactory(cycle=cycle)
    first = PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.TP_OPEN)
    second = PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.TP_OPEN)

    with django_capture_on_commit_callbacks(execute=True):
        PaymentPlanGroupService(group).assign_financial_service_provider(FinancialServiceProviderFactory())

    rebuilt = {call.args[0].pk for call in mock_full_rebuild.call_args_list}
    assert rebuilt == {first.pk, second.pk}


def test_assign_fsp_rejected_when_a_target_population_is_locked(cycle):
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.TP_LOCKED)

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(group).assign_financial_service_provider(FinancialServiceProviderFactory())
    assert error.value.detail[0] == (
        "Financial Service Provider can be changed only while every Target Population in the group is Open."
    )


def test_assign_currency_rejected_when_a_payment_plan_is_opened(cycle, currency):
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.OPEN)

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(group).assign_currency(currency)
    assert error.value.detail[0] == "Currency can be changed only before any Payment Plan in the group is opened."


def test_assign_currency_usdc_rejected_with_non_digital_delivery_mechanism(cycle, delivery_mechanism):
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.TP_OPEN,
        delivery_mechanism=delivery_mechanism,
    )

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(group).assign_currency(CurrencyFactory(code="USDC", name="USD Coin", is_crypto=True))
    assert (
        error.value.detail[0] == "For delivery mechanism Transfer to Digital Wallet only currency USDC can be assigned."
    )


def test_assign_currency_non_usdc_rejected_with_digital_wallet_delivery_mechanism(cycle, currency):
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.TP_OPEN,
        delivery_mechanism=DeliveryMechanismFactory(transfer_type=DeliveryMechanism.TransferType.DIGITAL),
    )

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(group).assign_currency(currency)
    assert (
        error.value.detail[0] == "For delivery mechanism Transfer to Digital Wallet only currency USDC can be assigned."
    )


def test_assign_currency_sets_it_on_the_group(cycle, currency, delivery_mechanism):
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.DRAFT,
        delivery_mechanism=delivery_mechanism,
    )

    PaymentPlanGroupService(group).assign_currency(currency)

    assert group.currency == currency
