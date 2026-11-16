from decimal import Decimal
import importlib
from types import SimpleNamespace
from typing import Any

from django.db import connection
import pytest

MIGRATION_CASES = (
    ("payment", "0083_migration", "Payment", "PAYMENT_COLUMNS", "change_payment_columns", 15),
    ("payment", "0084_migration", "PaymentPlan", "PAYMENT_PLAN_COLUMNS", "change_payment_plan_columns", 15),
    ("household", "0053_migration", "Household", "HOUSEHOLD_CASH_COLUMNS", "change_household_cash_columns", 64),
)


@pytest.fixture(params=MIGRATION_CASES, ids=("payment", "payment_plan", "household"))
def migration_case(request: pytest.FixtureRequest, db: None) -> SimpleNamespace:
    app_name, migration_name, model_name, columns_name, change_name, legacy_digits = request.param
    module = importlib.import_module(f"hope.apps.{app_name}.migrations.{migration_name}")
    return SimpleNamespace(
        app_name=app_name,
        model_name=model_name,
        columns=getattr(module, columns_name),
        change=getattr(module, change_name),
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


def test_currency_migration_expands_columns_without_adding_database_checks(
    legacy_currency_table: SimpleNamespace,
) -> None:
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
            "SELECT count(*) FROM pg_constraint WHERE conrelid = %s::regclass AND contype = 'c'",
            [case.table_name],
        )
        assert cursor.fetchone() == (0,)
        cursor.execute(f"SELECT {case.first_column} FROM {case.table}")
        assert cursor.fetchone() == (Decimal("123.45"),)

        # Raw SQL bypasses HopeCurrencyField's Python validation; the database column itself is unbounded numeric.
        raw_value = Decimal("-100000000000000000000.12345678912")
        cursor.execute(f"UPDATE {case.table} SET {case.first_column} = %s", [raw_value])
        cursor.execute(f"SELECT {case.first_column} FROM {case.table}")
        assert cursor.fetchone() == (raw_value,)
