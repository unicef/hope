from importlib import import_module

from django.apps import apps
from flags.models import FlagState
import pytest

from extras.test_utils.factories import FlagStateFactory

pytestmark = pytest.mark.django_db

migration = import_module("hope.apps.payment.migrations.0089_migration")


@pytest.fixture
def old_flag_on() -> FlagState:
    return FlagStateFactory(name="WU_PAYMENT_PLAN_INVOICES_NOTIFICATIONS_ENABLED")


@pytest.fixture
def new_flag_on() -> FlagState:
    return FlagStateFactory(name="WU_PAYMENT_LIST_INVOICES_NOTIFICATIONS_ENABLED")


def test_forwards_renames_the_flag_and_keeps_its_value(old_flag_on: FlagState) -> None:
    migration.forwards(apps, None)

    old_flag_on.refresh_from_db()
    assert old_flag_on.name == "WU_PAYMENT_LIST_INVOICES_NOTIFICATIONS_ENABLED"
    assert old_flag_on.condition == "boolean"
    assert old_flag_on.value == "True"


def test_forwards_drops_the_old_flag_when_the_new_one_has_the_same_state(
    old_flag_on: FlagState, new_flag_on: FlagState
) -> None:
    migration.forwards(apps, None)

    assert list(FlagState.objects.filter(name__startswith="WU_PAYMENT_").values_list("id", flat=True)) == [
        new_flag_on.id
    ]


def test_backwards_restores_the_old_flag_name(new_flag_on: FlagState) -> None:
    migration.backwards(apps, None)

    new_flag_on.refresh_from_db()
    assert new_flag_on.name == "WU_PAYMENT_PLAN_INVOICES_NOTIFICATIONS_ENABLED"
