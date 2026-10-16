from decimal import Decimal
import importlib
from types import SimpleNamespace
from typing import Any

from django.apps import apps as django_apps
from django.db import DatabaseError, IntegrityError, connection, transaction
import pytest

MIGRATION_CASES = (
    (
        "payment",
        "0079_migration",
        "Payment",
        "PAYMENT_COLUMNS",
        "change_payment_columns",
        "payment_currency_precision",
        15,
    ),
    (
        "payment",
        "0080_migration",
        "PaymentPlan",
        "PAYMENT_PLAN_COLUMNS",
        "change_payment_plan_columns",
        "payment_plan_currency_precision",
        15,
    ),
    (
        "payment",
        "0081_migration",
        "PaymentVerification",
        "PAYMENT_VERIFICATION_COLUMNS",
        "change_verification_amount_column",
        "payment_verification_currency_precision",
        15,
    ),
    (
        "household",
        "0051_migration",
        "Household",
        "HOUSEHOLD_CASH_COLUMNS",
        "change_household_cash_columns",
        "household_cash_precision",
        64,
    ),
)


@pytest.fixture(params=MIGRATION_CASES, ids=("payment", "payment_plan", "payment_verification", "household"))
def migration_case(request: pytest.FixtureRequest, db: None) -> SimpleNamespace:
    app_name, migration_name, model_name, columns_name, change_name, constraint_name, legacy_digits = request.param
    module = importlib.import_module(f"hope.apps.{app_name}.migrations.{migration_name}")
    return SimpleNamespace(
        module=module,
        app_name=app_name,
        model_name=model_name,
        columns=getattr(module, columns_name),
        change=getattr(module, change_name),
        constraint_name=constraint_name,
        legacy_digits=legacy_digits,
        table_name=f"test_currency_{model_name.lower()}",
    )


@pytest.fixture
def legacy_currency_table(migration_case: SimpleNamespace) -> SimpleNamespace:
    table = connection.ops.quote_name(migration_case.table_name)
    columns = ", ".join(
        f"{connection.ops.quote_name(column)} numeric({migration_case.legacy_digits},2)"
        for column in migration_case.columns
    )
    first_column = connection.ops.quote_name(migration_case.columns[0])
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE TEMP TABLE {table} ({columns})")
        cursor.execute(f"INSERT INTO {table} ({first_column}) VALUES (%s)", [Decimal("123.45")])

    historical_model = SimpleNamespace(_meta=SimpleNamespace(db_table=migration_case.table_name))

    def get_model(app_label: str, model_name: str) -> Any:
        assert (app_label, model_name) == (migration_case.app_name, migration_case.model_name)
        return historical_model

    migration_case.apps = SimpleNamespace(get_model=get_model)
    migration_case.table = table
    migration_case.first_column = first_column
    return migration_case


@pytest.fixture
def conflicting_legacy_currency_table(legacy_currency_table: SimpleNamespace) -> SimpleNamespace:
    constraint = connection.ops.quote_name(legacy_currency_table.constraint_name)
    with connection.cursor() as cursor:
        cursor.execute(f"ALTER TABLE {legacy_currency_table.table} ADD CONSTRAINT {constraint} CHECK (TRUE)")
    return legacy_currency_table


def test_currency_migration_expands_all_columns_and_enforces_precision(legacy_currency_table: SimpleNamespace) -> None:
    case = legacy_currency_table

    with connection.schema_editor() as schema_editor:
        case.change(case.apps, schema_editor)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT count(*), count(*) FILTER (WHERE format_type(atttypid, atttypmod) = 'numeric')
            FROM pg_attribute
            WHERE attrelid = %s::regclass AND attname = ANY(%s)
            """,
            [case.table_name, list(case.columns)],
        )
        assert cursor.fetchone() == (len(case.columns), len(case.columns))
        cursor.execute(
            "SELECT convalidated FROM pg_constraint WHERE conrelid = %s::regclass AND conname = %s",
            [case.table_name, case.constraint_name],
        )
        assert cursor.fetchone() == (False,)
        cursor.execute(f"SELECT {case.first_column} FROM {case.table}")
        legacy_value = cursor.fetchone()[0]
        assert legacy_value == Decimal("123.45")
        field = django_apps.get_model(case.app_name, case.model_name)._meta.get_field(case.columns[0])
        converted_value = field.from_db_value(legacy_value, None, connection)
        assert converted_value == Decimal("123.4500000000")
        assert converted_value.as_tuple().exponent == -10
        cursor.execute(f"UPDATE {case.table} SET {case.first_column} = %s", [Decimal("123.1234567891")])
        cursor.execute(f"SELECT {case.first_column} FROM {case.table}")
        assert cursor.fetchone() == (Decimal("123.1234567891"),)

    with connection.cursor() as cursor:
        with pytest.raises(IntegrityError), transaction.atomic():
            cursor.execute(f"UPDATE {case.table} SET {case.first_column} = %s", [Decimal("123.12345678912")])


def test_currency_migration_rolls_back_both_statements_and_retries(
    conflicting_legacy_currency_table: SimpleNamespace,
) -> None:
    case = conflicting_legacy_currency_table

    with pytest.raises(DatabaseError), transaction.atomic(), connection.schema_editor() as schema_editor:
        case.change(case.apps, schema_editor)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT format_type(atttypid, atttypmod) FROM pg_attribute WHERE attrelid = %s::regclass AND attname = %s",
            [case.table_name, case.columns[0]],
        )
        assert cursor.fetchone() == (f"numeric({case.legacy_digits},2)",)
        cursor.execute(f"ALTER TABLE {case.table} DROP CONSTRAINT {connection.ops.quote_name(case.constraint_name)}")

    with connection.schema_editor() as schema_editor:
        case.change(case.apps, schema_editor)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT format_type(atttypid, atttypmod) FROM pg_attribute WHERE attrelid = %s::regclass AND attname = %s",
            [case.table_name, case.columns[0]],
        )
        assert cursor.fetchone() == ("numeric",)
