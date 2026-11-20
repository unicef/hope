from django.db import migrations

import hope.apps.core.fields

HOUSEHOLD_CASH_COLUMNS = ("total_cash_received_usd",)


def change_household_cash_columns(apps, schema_editor):
    connection = schema_editor.connection
    table = schema_editor.quote_name(apps.get_model("household", "Household")._meta.db_table)
    columns = [schema_editor.quote_name(name) for name in HOUSEHOLD_CASH_COLUMNS]
    alterations = ", ".join(f"ALTER COLUMN {column} TYPE numeric" for column in columns)
    with connection.cursor() as cursor:
        cursor.execute("SET LOCAL lock_timeout = '1s'")
        cursor.execute("SET LOCAL statement_timeout = '30s'")
        cursor.execute(f"ALTER TABLE {table} {alterations}")


class Migration(migrations.Migration):
    atomic = True

    dependencies = [
        ("household", "0055_migration"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunPython(change_household_cash_columns)],
            state_operations=[
                migrations.AlterField(
                    model_name="household",
                    name="total_cash_received_usd",
                    field=hope.apps.core.fields.HopeCurrencyField(
                        blank=True,
                        decimal_places=10,
                        help_text="Sum of delivered payments in USD, with up to 10 decimal places [sys].",
                        max_digits=30,
                        null=True,
                        verbose_name="Total cash received in USD",
                    ),
                ),
            ],
        ),
    ]
