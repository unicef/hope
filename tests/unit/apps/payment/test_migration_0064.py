import importlib

from django.apps import apps as django_apps
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    PaymentPlanPurposeFactory,
    ProgramCycleFactory,
    ProgramFactory,
)
from hope.models import PaymentPlanGroup, PaymentPlanPurpose, Program

_migration = importlib.import_module("hope.apps.payment.migrations.0064_migration")
create_default_purpose_and_backfill = _migration.create_default_purpose_and_backfill

pytestmark = pytest.mark.django_db


@pytest.fixture
def program():
    return ProgramFactory(status=Program.DRAFT)


@pytest.fixture
def cycle(program):
    return ProgramCycleFactory(program=program)


@pytest.fixture
def purpose(program):
    return PaymentPlanPurposeFactory(business_area=program.business_area)


@pytest.fixture
def plan(cycle):
    return PaymentPlanFactory(program_cycle=cycle)


@pytest.fixture
def plan_purpose(plan):
    return PaymentPlanPurposeFactory(business_area=plan.business_area)


@pytest.fixture
def other_group(cycle):
    return PaymentPlanGroupFactory(cycle=cycle)


@pytest.fixture
def plan_with_group(cycle, other_group):
    return PaymentPlanFactory(program_cycle=cycle, payment_plan_group=other_group)


@pytest.fixture
def plan_without_group(cycle):
    return PaymentPlanFactory(program_cycle=cycle, payment_plan_group=None)


def test_default_purpose_is_created_per_business_area():
    ba = BusinessAreaFactory()

    create_default_purpose_and_backfill(django_apps, None)

    assert PaymentPlanPurpose.objects.filter(name="Default Purpose", business_area=ba).exists()


def test_program_without_purpose_gets_default_purpose(program):
    create_default_purpose_and_backfill(django_apps, None)

    assert program.payment_plan_purposes.filter(name="Default Purpose", business_area=program.business_area).exists()


def test_program_with_existing_purpose_keeps_it_and_gets_no_extra(program, purpose):
    program.payment_plan_purposes.set([purpose])

    create_default_purpose_and_backfill(django_apps, None)

    assert program.payment_plan_purposes.count() == 1
    assert program.payment_plan_purposes.filter(pk=purpose.pk).exists()


def test_payment_plan_without_purpose_gets_default_purpose(plan):
    create_default_purpose_and_backfill(django_apps, None)

    assert plan.payment_plan_purposes.filter(name="Default Purpose", business_area=plan.business_area).exists()


def test_payment_plan_with_existing_purpose_keeps_it_and_gets_no_extra(plan, plan_purpose):
    plan.payment_plan_purposes.set([plan_purpose])

    create_default_purpose_and_backfill(django_apps, None)

    assert plan.payment_plan_purposes.count() == 1
    assert plan.payment_plan_purposes.filter(pk=plan_purpose.pk).exists()


def test_cycle_without_group_gets_default_group(cycle):
    PaymentPlanGroup.objects.filter(cycle=cycle, name="Default Group").delete()

    create_default_purpose_and_backfill(django_apps, None)

    assert PaymentPlanGroup.objects.filter(cycle=cycle, name="Default Group").exists()


def test_cycle_already_with_group_gets_no_duplicate(cycle):
    assert PaymentPlanGroup.objects.filter(cycle=cycle, name="Default Group").count() == 1

    create_default_purpose_and_backfill(django_apps, None)

    assert PaymentPlanGroup.objects.filter(cycle=cycle, name="Default Group").count() == 1


def test_plan_without_group_gets_assigned_to_cycles_default_group(plan_without_group, cycle):
    default_group = PaymentPlanGroup.objects.get(cycle=cycle, name="Default Group")

    create_default_purpose_and_backfill(django_apps, None)

    plan_without_group.refresh_from_db()
    assert plan_without_group.payment_plan_group == default_group


def test_plan_with_existing_group_is_not_reassigned(plan_with_group, other_group):
    create_default_purpose_and_backfill(django_apps, None)

    plan_with_group.refresh_from_db()
    assert plan_with_group.payment_plan_group == other_group
