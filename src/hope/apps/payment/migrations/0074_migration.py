from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0073_migration"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="paymentplan",
            constraint=models.UniqueConstraint(
                condition=models.Q(export_tag__isnull=False),
                fields=["payment_plan_group", "export_tag"],
                name="unique_export_tag_per_group",
            ),
        ),
    ]
