from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0069_migration"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="paymentplan",
            name="is_follow_up",
        ),
        migrations.AddConstraint(
            model_name="paymentplan",
            constraint=models.CheckConstraint(
                condition=models.Q(is_removed=True) | models.Q(payment_plan_group__isnull=False),
                name="payment_plan_group_required_unless_removed",
            ),
        ),
    ]
