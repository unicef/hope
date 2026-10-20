from decimal import Decimal

import django.core.validators
from django.db import migrations, models
from django.db.models.functions import Abs, Round
from django.db.models.lookups import LessThan

import hope.apps.core.fields

PAYMENT_VERIFICATION_COLUMNS = ("received_amount",)


def payment_verification_currency_precision_constraint() -> models.CheckConstraint:
    column = "received_amount"
    condition = models.Q(**{f"{column}__isnull": True}) | (
        models.Q(LessThan(Abs(column), Decimal(100000000000000000000))) & models.Q(**{column: Round(column, 10)})
    )
    return models.CheckConstraint(condition=condition, name="payment_verification_currency_precision")


def change_verification_amount_column(apps, schema_editor):
    connection = schema_editor.connection
    table = schema_editor.quote_name(apps.get_model("payment", "PaymentVerification")._meta.db_table)
    column = schema_editor.quote_name("received_amount")
    constraint = schema_editor.quote_name("payment_verification_currency_precision")
    with connection.cursor() as cursor:
        cursor.execute("SET LOCAL lock_timeout = '1s'")
        cursor.execute("SET LOCAL statement_timeout = '30s'")
        cursor.execute(f"ALTER TABLE {table} ALTER COLUMN {column} TYPE numeric")
        cursor.execute(
            f"ALTER TABLE {table} ADD CONSTRAINT {constraint} CHECK ("
            f"{column} IS NULL OR "
            f"(abs({column}) < 100000000000000000000 AND {column} = round({column}, 10))"
            ") NOT VALID"
        )


class Migration(migrations.Migration):
    atomic = True

    dependencies = [("payment", "0083_migration")]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunPython(change_verification_amount_column)],
            state_operations=[
                migrations.AlterField(
                    model_name="paymentverification",
                    name="received_amount",
                    field=hope.apps.core.fields.HopeCurrencyField(
                        blank=True,
                        decimal_places=10,
                        help_text="Amount reported received in the payment currency, with up to 10 decimal places.",
                        max_digits=30,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.0000000001"))],
                        verbose_name="Received amount in base currency",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="paymentverification",
                    constraint=payment_verification_currency_precision_constraint(),
                ),
            ],
        ),
    ]
