from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

import hope.apps.account.fields
import hope.models.grant


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("api", "0002_migration"),
        ("api", "0003_migration"),
        ("api", "0004_migration"),
        ("api", "0005_migration"),
        ("api", "0006_migration"),
        ("api", "0007_migration"),
    ]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="APILogEntry",
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
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                ("url", models.URLField()),
                ("method", models.CharField(max_length=10)),
                ("status_code", models.IntegerField()),
            ],
            options={
                "verbose_name_plural": "Api Log Entries",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="APIToken",
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
                (
                    "key",
                    models.CharField(blank=True, max_length=40, unique=True, verbose_name="Key"),
                ),
                (
                    "grants",
                    hope.apps.account.fields.ChoiceArrayField(
                        base_field=models.CharField(choices=hope.models.grant.Grant.choices, max_length=255),
                        size=None,
                    ),
                ),
                ("valid_from", models.DateField(default=django.utils.timezone.now)),
                ("valid_to", models.DateField(blank=True, null=True)),
                (
                    "allowed_ips",
                    models.CharField(blank=True, max_length=200, null=True, verbose_name="IPs"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
                "permissions": (("resend_token_email", "Can resend an email with token"),),
            },
        ),
    ]
