import logging

from django.db import migrations, models
import django.db.models.deletion

logger = logging.getLogger(__name__)


def populate_currency_fk(apps, schema_editor):
    Household = apps.get_model("household", "Household")
    Currency = apps.get_model("core", "Currency")

    currency_map = dict(Currency.objects.values_list("code", "pk"))

    qs = Household.objects.exclude(currency_old="").exclude(currency_old__isnull=True)
    for currency_code, pk_value in currency_map.items():
        qs.filter(currency_old=currency_code, currency__isnull=True).update(currency_id=pk_value)


def reverse_populate(apps, schema_editor):
    Household = apps.get_model("household", "Household")
    Currency = apps.get_model("core", "Currency")

    currency_map = dict(Currency.objects.values_list("pk", "code"))

    for pk_value, currency_code in currency_map.items():
        Household.objects.filter(currency_id=pk_value).update(currency_old=currency_code)


class Migration(migrations.Migration):
    dependencies = [
        ("household", "0036_migration"),
        ("core", "0020_migration"),
    ]

    operations = [
        migrations.RenameField(
            model_name="household",
            old_name="currency",
            new_name="currency_old",
        ),
        migrations.AlterField(
            model_name="household",
            name="currency_old",
            field=models.CharField(
                default="",
                help_text="Household currency (legacy, pending removal)",
                max_length=250,
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="currency",
            field=models.ForeignKey(
                blank=True,
                help_text="Household currency",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="households",
                to="core.currency",
            ),
        ),
        migrations.RunPython(populate_currency_fk, reverse_populate),
    ]
