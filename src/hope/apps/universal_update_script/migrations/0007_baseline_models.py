import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion

import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("universal_update_script", "0001_migration"),
        ("universal_update_script", "0002_migration"),
        ("universal_update_script", "0003_migration"),
        ("universal_update_script", "0004_migration"),
        ("universal_update_script", "0005_migration"),
        ("universal_update_script", "0006_migration"),
        ("universal_update_script", "0007_migration"),
    ]

    dependencies = [
        ("household", "0052_baseline_models"),
        ("payment", "0081_baseline_models"),
        ("program", "0023_baseline_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="UniversalUpdate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "individual_fields",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=255),
                        default=list,
                        help_text="Selected Individual Fields which can be updated",
                        size=None,
                    ),
                ),
                (
                    "individual_flex_fields_fields",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=255),
                        default=list,
                        help_text="Selected Individual Flex Fields which can be updated",
                        size=None,
                    ),
                ),
                (
                    "household_fields",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=255),
                        default=list,
                        help_text="Selected Household Fields which can be updated",
                        size=None,
                    ),
                ),
                (
                    "household_flex_fields_fields",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=255),
                        default=list,
                        help_text="Selected Household Flex Fields which can be updated",
                        size=None,
                    ),
                ),
                (
                    "template_file",
                    models.FileField(
                        blank=True,
                        help_text="Generated Template XLSX File, contains columns for data to be updated. Contains also rows for unicef_ids to be updated",
                        null=True,
                        upload_to="",
                    ),
                ),
                (
                    "update_file",
                    models.FileField(
                        blank=True,
                        help_text="Uploaded File, contains data to be updated. After clicking a button to update, data will be updated",
                        null=True,
                        upload_to="",
                    ),
                ),
                (
                    "backup_snapshot",
                    models.FileField(
                        blank=True,
                        help_text="Backup Snapshot File, contains data before update. File updated on each start of update process.",
                        null=True,
                        upload_to="",
                    ),
                ),
                (
                    "saved_logs",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Logs of the update process, saved in db",
                        null=True,
                    ),
                ),
                (
                    "unicef_ids",
                    models.TextField(
                        blank=True,
                        help_text="Unicef IDs used only to generate template file",
                        null=True,
                    ),
                ),
                (
                    "account_types",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Selected Account Types of which Wallets data can be updated",
                        to="payment.accounttype",
                    ),
                ),
                (
                    "document_types",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Selected Document Types of which Documents can be updated",
                        to="household.documenttype",
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="program.program",
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
                "permissions": [
                    ("can_run_universal_update", "Can run universal update"),
                    (
                        "can_generate_universal_update_template",
                        "Can generate universal update template",
                    ),
                ],
                "indexes": [
                    hope.models.utils.LongNameIndex(
                        fields=["created_at"],
                        name="universal_update_script_universalupdate_created_at_827043a2",
                    ),
                    hope.models.utils.LongNameIndex(
                        fields=["updated_at"],
                        name="universal_update_script_universalupdate_updated_at_fc896500",
                    ),
                ],
            },
        ),
    ]
