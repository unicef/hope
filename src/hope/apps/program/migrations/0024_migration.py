from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0042_migration"),
        ("program", "0023_migration"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="beneficiarygroup",
            options={
                "ordering": ("name",),
                "permissions": (("reset_sync_date", "Can reset sync date"),),
                "verbose_name": "Payee Label",
                "verbose_name_plural": "Payee Labels",
            },
        ),
        migrations.AddField(
            model_name="beneficiarygroup",
            name="payee_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payee_labels",
                to="core.payeetype",
            ),
        ),
        migrations.AddField(
            model_name="beneficiarygroup",
            name="data_collecting_types",
            field=models.ManyToManyField(
                blank=True,
                help_text="Leave empty to allow every Data Collecting Type of the Payee Type",
                related_name="payee_labels",
                to="core.datacollectingtype",
            ),
        ),
        migrations.AddField(
            model_name="beneficiarygroup",
            name="active",
            field=models.BooleanField(default=True, help_text="Inactive Payee Labels cannot be used in new programs"),
        ),
        migrations.AlterField(
            model_name="program",
            name="beneficiary_group",
            field=models.ForeignKey(
                help_text="Program payee label",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="programs",
                to="program.beneficiarygroup",
            ),
        ),
    ]
