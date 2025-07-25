# Generated by Django 3.2.25 on 2024-12-16 11:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0009_migration"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="paymentrecord",
            name="business_area",
        ),
        migrations.RemoveField(
            model_name="paymentrecord",
            name="delivery_type",
        ),
        migrations.RemoveField(
            model_name="paymentrecord",
            name="head_of_household",
        ),
        migrations.RemoveField(
            model_name="paymentrecord",
            name="household",
        ),
        migrations.RemoveField(
            model_name="paymentrecord",
            name="parent",
        ),
        migrations.RemoveField(
            model_name="paymentrecord",
            name="service_provider",
        ),
        migrations.RemoveField(
            model_name="paymentrecord",
            name="target_population",
        ),
        migrations.RemoveField(
            model_name="serviceprovider",
            name="business_area",
        ),
        migrations.AlterField(
            model_name="financialserviceprovider",
            name="internal_data",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="payment",
            name="internal_data",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="paymentplan",
            name="internal_data",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.DeleteModel(
            name="CashPlan",
        ),
        migrations.DeleteModel(
            name="PaymentRecord",
        ),
        migrations.DeleteModel(
            name="ServiceProvider",
        ),
    ]
