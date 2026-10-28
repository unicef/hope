from django.db import migrations, models
from django.db.models import OuterRef, Subquery
import django.db.models.deletion


def move_documents_to_groups_and_instructions(apps, schema_editor):
    """Attach every supporting document to its plan's Follow-Up Instruction, or else to its plan's group."""
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    PaymentPlanSupportingDocument = apps.get_model("payment", "PaymentPlanSupportingDocument")
    plan = PaymentPlan.objects.filter(pk=OuterRef("payment_plan_id"))
    PaymentPlanSupportingDocument.objects.filter(payment_plan__follow_up_instruction__isnull=False).update(
        follow_up_instruction_id=Subquery(plan.values("follow_up_instruction_id")[:1])
    )
    PaymentPlanSupportingDocument.objects.filter(payment_plan__follow_up_instruction__isnull=True).update(
        payment_plan_group_id=Subquery(plan.values("payment_plan_group_id")[:1])
    )


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0095_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentplansupportingdocument",
            name="follow_up_instruction",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documents",
                to="payment.followupinstruction",
            ),
        ),
        migrations.AddField(
            model_name="paymentplansupportingdocument",
            name="payment_plan_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documents",
                to="payment.paymentplangroup",
            ),
        ),
        # Not reversible: documents of a group or instruction cannot be handed back to one plan. The database copy
        # taken before the release is the rollback.
        migrations.RunPython(move_documents_to_groups_and_instructions, migrations.RunPython.noop),
    ]
