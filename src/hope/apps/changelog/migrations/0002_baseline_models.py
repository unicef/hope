import datetime as dt

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("changelog", "0001_migration"),
    ]

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Changelog",
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
                ("description", models.TextField(blank=True)),
                ("version", models.CharField(help_text="HOPE version", max_length=30)),
                ("active", models.BooleanField(default=False)),
                ("date", models.DateField(default=dt.date.today)),
            ],
            options={
                "ordering": ("-date",),
            },
        ),
    ]
