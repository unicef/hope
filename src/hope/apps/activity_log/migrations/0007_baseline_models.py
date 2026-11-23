from django.db import migrations, models

import hope.models.log_entry


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("activity_log", "0003_migration"),
        ("activity_log", "0004_migration"),
        ("activity_log", "0005_migration"),
        ("activity_log", "0006_migration"),
    ]

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LogEntry",
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
                ("object_id", models.UUIDField(blank=True, null=True)),
                (
                    "action",
                    models.CharField(
                        choices=hope.models.log_entry.get_log_entry_action_choices,
                        max_length=100,
                        verbose_name="action",
                    ),
                ),
                ("object_repr", models.TextField(blank=True)),
                (
                    "changes",
                    models.JSONField(blank=True, null=True, verbose_name="change message"),
                ),
                (
                    "timestamp",
                    models.DateTimeField(auto_now_add=True, verbose_name="timestamp"),
                ),
            ],
            options={
                "verbose_name": "log entry",
                "verbose_name_plural": "log entries",
                "ordering": ["-timestamp"],
                "get_latest_by": "timestamp",
            },
        ),
    ]
