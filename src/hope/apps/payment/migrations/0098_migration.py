from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0097_migration"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="paymentplansupportingdocument",
            name="payment_plan",
        ),
        migrations.AddConstraint(
            model_name="paymentplansupportingdocument",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("follow_up_instruction__isnull", True), ("payment_plan_group__isnull", False)),
                    models.Q(("follow_up_instruction__isnull", False), ("payment_plan_group__isnull", True)),
                    _connector="OR",
                ),
                name="supporting_document_has_one_owner",
            ),
        ),
    ]
