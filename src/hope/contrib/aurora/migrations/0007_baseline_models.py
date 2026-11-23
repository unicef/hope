from django.db import migrations, models
import strategy_field.fields

import hope.contrib.aurora.models
import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("aurora", "0003_migration"),
        ("aurora", "0004_migration"),
        ("aurora", "0005_migration"),
        ("aurora", "0006_migration"),
    ]

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Organization",
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
                ("source_id", models.BigIntegerField()),
                ("name", models.CharField(max_length=1000)),
                ("slug", models.SlugField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name="Project",
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
                ("source_id", models.BigIntegerField()),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Registration",
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
                ("source_id", models.BigIntegerField()),
                ("name", models.CharField(max_length=500)),
                ("slug", models.SlugField()),
                ("extra", models.JSONField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, null=True)),
                (
                    "rdi_parser",
                    strategy_field.fields.StrategyField(blank=True, null=True),
                ),
                (
                    "rdi_policy",
                    models.IntegerField(
                        choices=hope.contrib.aurora.models.get_rdi_policy_choices,
                        default=1,
                    ),
                ),
                ("mapping", models.JSONField(blank=True, null=True)),
                (
                    "private_key",
                    models.TextField(blank=True, editable=False, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Record",
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
                ("registration", models.IntegerField()),
                ("timestamp", models.DateTimeField()),
                ("storage", models.BinaryField(blank=True, null=True)),
                ("ignored", models.BooleanField(blank=True, default=False, null=True)),
                ("source_id", models.IntegerField()),
                ("data", models.JSONField(blank=True, default=dict, null=True)),
                ("error_message", models.TextField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=hope.contrib.aurora.models.get_record_status_choices,
                        max_length=16,
                        null=True,
                    ),
                ),
                (
                    "unique_field",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("size", models.IntegerField(blank=True, null=True)),
                ("counters", models.JSONField(blank=True, null=True)),
                ("fields", models.JSONField(blank=True, null=True)),
                ("files", models.BinaryField(blank=True, null=True)),
                ("index1", models.CharField(blank=True, max_length=255, null=True)),
                ("index2", models.CharField(blank=True, max_length=255, null=True)),
                ("index3", models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                "permissions": (
                    ("can_fetch_data", "Can fetch data from aurora"),
                    ("can_add_records", "Can add records"),
                ),
                "swappable": "AURORA_RECORD_MODEL",
                "indexes": [
                    hope.models.utils.LongNameIndex(
                        fields=["registration"],
                        name="aurora_record_registration_18c617c1",
                    ),
                    hope.models.utils.LongNameIndex(fields=["timestamp"], name="aurora_record_timestamp_d68c0d5a"),
                    hope.models.utils.LongNameIndex(fields=["ignored"], name="aurora_record_ignored_1640d007"),
                    hope.models.utils.LongNameIndex(fields=["source_id"], name="aurora_record_source_id_e66ff785"),
                    hope.models.utils.LongNameIndex(
                        fields=["unique_field"],
                        name="aurora_record_unique_field_903b6acc",
                    ),
                    hope.models.utils.LongNameIndex(
                        fields=["unique_field"],
                        name="aurora_record_unique_field_903b6acc_like",
                        opclasses=["varchar_pattern_ops"],
                    ),
                    hope.models.utils.LongNameIndex(fields=["index1"], name="aurora_record_index1_359087d6"),
                    hope.models.utils.LongNameIndex(
                        fields=["index1"],
                        name="aurora_record_index1_359087d6_like",
                        opclasses=["varchar_pattern_ops"],
                    ),
                    hope.models.utils.LongNameIndex(fields=["index2"], name="aurora_record_index2_cfcbc3b9"),
                    hope.models.utils.LongNameIndex(
                        fields=["index2"],
                        name="aurora_record_index2_cfcbc3b9_like",
                        opclasses=["varchar_pattern_ops"],
                    ),
                    hope.models.utils.LongNameIndex(fields=["index3"], name="aurora_record_index3_21b563c6"),
                    hope.models.utils.LongNameIndex(
                        fields=["index3"],
                        name="aurora_record_index3_21b563c6_like",
                        opclasses=["varchar_pattern_ops"],
                    ),
                ],
            },
        ),
    ]
