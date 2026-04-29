from django.db import migrations, models


def migrate_plan_type(apps, schema_editor):
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    PaymentPlan.objects.filter(is_follow_up=True).update(plan_type="FOLLOW_UP")


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0064_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentplan",
            name="plan_type",
            field=models.CharField(
                choices=[("REGULAR", "Regular"), ("TOP_UP", "Top Up"), ("FOLLOW_UP", "Follow Up")],
                default="REGULAR",
                db_index=True,
                max_length=10,
                help_text="Payment Plan type [sys]",
            ),
        ),
        migrations.RunPython(migrate_plan_type, migrations.RunPython.noop),
    ]
