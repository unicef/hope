import importlib

from django.apps import apps
from django.db import connection
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
import pytest

from extras.test_utils.factories.account import RoleFactory
from hope.models import Role

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.account.migrations.0036_migration")


@pytest.fixture
def schema_editor() -> BaseDatabaseSchemaEditor:
    return connection.schema_editor()


@pytest.fixture
def group_role() -> Role:
    return RoleFactory(name="Group role", permissions=["PM_PAYMENT_PLAN_GROUP_VIEW_LIST", "PM_VIEW_LIST"])


@pytest.fixture
def list_gateway_role() -> Role:
    return RoleFactory(name="List gateway role", permissions=["PM_SEND_TO_PAYMENT_GATEWAY"])


@pytest.fixture
def both_gateway_role() -> Role:
    return RoleFactory(
        name="Both gateway role",
        permissions=["PM_SEND_TO_PAYMENT_GATEWAY", "PM_PAYMENT_PLAN_SEND_TO_PAYMENT_GATEWAY"],
    )


@pytest.fixture
def other_role() -> Role:
    return RoleFactory(name="Other role", permissions=["PM_VIEW_LIST"])


def test_forwards_renames_the_group_permission(group_role: Role, schema_editor: BaseDatabaseSchemaEditor) -> None:
    migration_module.forwards(apps, schema_editor)

    group_role.refresh_from_db()
    assert group_role.permissions == ["PM_PAYMENT_PLAN_VIEW_LIST", "PM_VIEW_LIST"]


def test_forwards_grants_the_plan_gateway_permission_to_roles_with_the_list_one(
    list_gateway_role: Role, schema_editor: BaseDatabaseSchemaEditor
) -> None:
    migration_module.forwards(apps, schema_editor)

    list_gateway_role.refresh_from_db()
    assert list_gateway_role.permissions == ["PM_SEND_TO_PAYMENT_GATEWAY", "PM_PAYMENT_PLAN_SEND_TO_PAYMENT_GATEWAY"]


def test_forwards_does_not_duplicate_the_plan_gateway_permission(
    both_gateway_role: Role, schema_editor: BaseDatabaseSchemaEditor
) -> None:
    migration_module.forwards(apps, schema_editor)

    both_gateway_role.refresh_from_db()
    assert both_gateway_role.permissions == ["PM_SEND_TO_PAYMENT_GATEWAY", "PM_PAYMENT_PLAN_SEND_TO_PAYMENT_GATEWAY"]


def test_forwards_leaves_other_roles_alone(other_role: Role, schema_editor: BaseDatabaseSchemaEditor) -> None:
    migration_module.forwards(apps, schema_editor)

    other_role.refresh_from_db()
    assert other_role.permissions == ["PM_VIEW_LIST"]


def test_backwards_restores_the_group_permission(schema_editor: BaseDatabaseSchemaEditor) -> None:
    role = RoleFactory(name="Renamed role", permissions=["PM_PAYMENT_PLAN_VIEW_LIST"])

    migration_module.backwards(apps, schema_editor)

    role.refresh_from_db()
    assert role.permissions == ["PM_PAYMENT_PLAN_GROUP_VIEW_LIST"]
