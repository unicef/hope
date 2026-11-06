import importlib

from django.apps import apps
from django.db import connection
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
import pytest

from extras.test_utils.factories.steficon import RuleFactory
from hope.models import Rule, RuleCommit

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.steficon.migrations.0009_migration")


@pytest.fixture
def schema_editor() -> BaseDatabaseSchemaEditor:
    return connection.schema_editor()


@pytest.fixture
def old_rule() -> Rule:
    return RuleFactory(
        type=Rule.TYPE_PAYMENT_LIST,
        definition="result.value = payment_plan.exchange_rate * household.size\nplan = payment_plan_id",
    )


@pytest.fixture
def new_rule() -> Rule:
    return RuleFactory(type=Rule.TYPE_PAYMENT_LIST, definition="result.value = payment_list.exchange_rate")


@pytest.fixture
def household_rule() -> Rule:
    return RuleFactory(type=Rule.TYPE_TARGETING, definition="result.value = household.size > 3")


def test_forwards_renames_the_variable_in_the_rule(old_rule: Rule, schema_editor: BaseDatabaseSchemaEditor) -> None:
    migration_module.forwards(apps, schema_editor)

    old_rule.refresh_from_db()
    assert old_rule.definition == "result.value = payment_list.exchange_rate * household.size\nplan = payment_plan_id"


def test_forwards_renames_the_variable_in_the_commit(old_rule: Rule, schema_editor: BaseDatabaseSchemaEditor) -> None:
    migration_module.forwards(apps, schema_editor)

    commit = RuleCommit.objects.get(rule=old_rule)
    assert commit.definition == "result.value = payment_list.exchange_rate * household.size\nplan = payment_plan_id"


def test_forwards_leaves_other_rules_alone(household_rule: Rule, schema_editor: BaseDatabaseSchemaEditor) -> None:
    migration_module.forwards(apps, schema_editor)

    household_rule.refresh_from_db()
    assert household_rule.definition == "result.value = household.size > 3"


def test_backwards_restores_the_old_variable(new_rule: Rule, schema_editor: BaseDatabaseSchemaEditor) -> None:
    migration_module.backwards(apps, schema_editor)

    new_rule.refresh_from_db()
    assert new_rule.definition == "result.value = payment_plan.exchange_rate"
    assert RuleCommit.objects.get(rule=new_rule).definition == "result.value = payment_plan.exchange_rate"
