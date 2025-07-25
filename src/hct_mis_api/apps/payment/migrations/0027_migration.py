# Generated by Django 3.2.25 on 2025-04-10 12:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("geo", "0004_migration"),
        ("payment", "0026_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="number",
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name="account",
            name="financial_institution",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="payment.financialinstitution"
            ),
        ),
    ]
