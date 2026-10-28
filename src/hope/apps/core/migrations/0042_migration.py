import uuid

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0041_migration"),
    ]

    operations = [
        migrations.CreateModel(
            name="PayeeType",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "gl_code",
                    models.CharField(blank=True, help_text="General Ledger code shown on the Program", max_length=32),
                ),
                ("description", models.TextField(blank=True)),
                (
                    "active",
                    models.BooleanField(default=True, help_text="Inactive Payee Types cannot be used in new programs"),
                ),
                (
                    "weight",
                    models.PositiveSmallIntegerField(
                        default=0, help_text="Ordering weight: types with a higher weight are listed first"
                    ),
                ),
                (
                    "default_data_collecting_type",
                    models.ForeignKey(
                        blank=True,
                        help_text="Data Collecting Type preselected when this Payee Type is chosen",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="core.datacollectingtype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Payee Type",
                "verbose_name_plural": "Payee Types",
                "ordering": ("-weight", "name"),
            },
        ),
        migrations.AddField(
            model_name="datacollectingtype",
            name="payee_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="data_collecting_types",
                to="core.payeetype",
            ),
        ),
    ]
