import importlib

from django.apps import apps
import pytest

from extras.test_utils.factories import PaymentPlanFactory, PaymentPlanGroupFactory, ProgramCycleFactory
from extras.test_utils.factories.core import CurrencyFactory
from extras.test_utils.factories.payment import FinancialServiceProviderFactory

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.payment.migrations.0079_migration")


@pytest.fixture
def cycle():
    return ProgramCycleFactory()


@pytest.fixture
def fsp():
    return FinancialServiceProviderFactory()


@pytest.fixture
def currency():
    return CurrencyFactory(code="PLN", name="Polish Zloty")


def test_migration_copies_agreed_fsp_and_currency_onto_group(cycle, fsp, currency):
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, financial_service_provider=fsp, currency=currency)
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, financial_service_provider=fsp, currency=currency)

    migration_module.copy_values_from_payment_plans(apps, schema_editor=None)

    group.refresh_from_db()
    assert group.financial_service_provider == fsp
    assert group.currency == currency


def test_migration_leaves_group_empty_when_plans_have_no_fsp(cycle):
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, financial_service_provider=None, currency=None)

    migration_module.copy_values_from_payment_plans(apps, schema_editor=None)

    group.refresh_from_db()
    assert group.financial_service_provider is None
    assert group.currency is None


def test_migration_ignores_removed_plans(cycle, fsp, currency):
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, financial_service_provider=fsp, currency=currency)
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=group,
        financial_service_provider=FinancialServiceProviderFactory(),
        currency=CurrencyFactory(code="EUR", name="Euro"),
        is_removed=True,
    )

    migration_module.copy_values_from_payment_plans(apps, schema_editor=None)

    group.refresh_from_db()
    assert group.financial_service_provider == fsp
    assert group.currency == currency


def test_migration_stops_on_group_with_mixed_fsps(cycle, fsp, currency):
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, financial_service_provider=fsp, currency=currency)
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=group,
        financial_service_provider=FinancialServiceProviderFactory(),
        currency=currency,
    )

    with pytest.raises(RuntimeError) as error:
        migration_module.copy_values_from_payment_plans(apps, schema_editor=None)
    assert group.unicef_id in str(error.value)


def test_migration_stops_on_group_with_mixed_currencies(cycle, fsp, currency):
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, financial_service_provider=fsp, currency=currency)
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=group,
        financial_service_provider=fsp,
        currency=CurrencyFactory(code="EUR", name="Euro"),
    )

    with pytest.raises(RuntimeError) as error:
        migration_module.copy_values_from_payment_plans(apps, schema_editor=None)
    assert group.unicef_id in str(error.value)
