# Generated by Django 3.2.25 on 2024-11-28 23:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0004_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="paymentverificationplan",
            name="sex_filter",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
