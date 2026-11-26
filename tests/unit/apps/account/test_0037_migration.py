import importlib

from django.apps import apps
from django.db import connection
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
import pytest

from extras.test_utils.factories.account import RoleFactory
from hope.models import Role

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.account.migrations.0037_migration")


@pytest.fixture
def schema_editor() -> BaseDatabaseSchemaEditor:
    return connection.schema_editor()


@pytest.fixture
def payment_list_role() -> Role:
    return RoleFactory(name="Payment list role", permissions=["PM_VIEW_LIST", "PM_VIEW_DETAILS", "PM_CREATE"])


@pytest.fixture
def role_with_plan_view_list() -> Role:
    return RoleFactory(name="Plan view role", permissions=["PM_VIEW_LIST", "PM_PAYMENT_PLAN_VIEW_LIST"])


@pytest.fixture
def unrelated_role() -> Role:
    return RoleFactory(name="Unrelated role", permissions=["PM_SPLIT"])


def test_forwards_grants_plan_permissions_matching_the_list_ones(
    payment_list_role: Role, schema_editor: BaseDatabaseSchemaEditor
) -> None:
    migration_module.forwards(apps, schema_editor)

    payment_list_role.refresh_from_db()
    assert payment_list_role.permissions == [
        "PM_VIEW_LIST",
        "PM_VIEW_DETAILS",
        "PM_CREATE",
        "PM_PAYMENT_PLAN_VIEW_LIST",
        "PM_PAYMENT_PLAN_VIEW_DETAIL",
        "PM_PAYMENT_PLAN_CREATE",
        "PM_PAYMENT_PLAN_UPDATE",
    ]


def test_forwards_does_not_duplicate_a_plan_permission_the_role_has(
    role_with_plan_view_list: Role, schema_editor: BaseDatabaseSchemaEditor
) -> None:
    migration_module.forwards(apps, schema_editor)

    role_with_plan_view_list.refresh_from_db()
    assert role_with_plan_view_list.permissions == ["PM_VIEW_LIST", "PM_PAYMENT_PLAN_VIEW_LIST"]


def test_forwards_leaves_roles_without_list_permissions_alone(
    unrelated_role: Role, schema_editor: BaseDatabaseSchemaEditor
) -> None:
    migration_module.forwards(apps, schema_editor)

    unrelated_role.refresh_from_db()
    assert unrelated_role.permissions == ["PM_SPLIT"]
