from django.conf import settings
from django.db import migrations, models
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.db.models import Exists, OuterRef, Subquery, Sum
import django.db.models.deletion

MID_APPROVAL_STATUSES = ("IN_APPROVAL", "IN_AUTHORIZATION", "IN_REVIEW")


def move_approval_processes_to_instructions(apps, schema_editor):
    """Move the approval processes of instruction child plans to the instruction.

    The children were approved together, each in its own process with the same approvals. For an instruction still in
    approval, the newest process becomes the active one and its required approval, authorization and finance release
    numbers are set from the threshold for the summed USD total of the children.
    """
    ApprovalProcess = apps.get_model("payment", "ApprovalProcess")
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    FollowUpInstruction = apps.get_model("payment", "FollowUpInstruction")
    AcceptanceProcessThreshold = apps.get_model("payment", "AcceptanceProcessThreshold")

    plan_instruction = PaymentPlan.objects.filter(pk=OuterRef("payment_plan_id")).values("follow_up_instruction_id")[:1]
    ApprovalProcess.objects.filter(payment_plan__follow_up_instruction__isnull=False).update(
        follow_up_instruction_id=Subquery(plan_instruction), payment_plan=None
    )

    mid_approval_child = PaymentPlan.objects.filter(
        follow_up_instruction_id=OuterRef("pk"), is_removed=False, status__in=MID_APPROVAL_STATUSES
    )
    for instruction in FollowUpInstruction.objects.filter(Exists(mid_approval_child)).select_related("business_area"):
        active_process = (
            ApprovalProcess.objects.filter(follow_up_instruction=instruction).order_by("-created_at").first()
        )
        if active_process is None:
            continue
        total_usd = int(
            PaymentPlan.objects.filter(follow_up_instruction=instruction, is_removed=False).aggregate(
                total=Sum("total_entitled_quantity_usd")
            )["total"]
            or 0
        )
        threshold = AcceptanceProcessThreshold.objects.filter(
            business_area=instruction.business_area,
            payments_range_usd__contains=NumericRange(total_usd, total_usd, bounds="[]"),
        ).first()
        active_process.approval_number_required = threshold.approval_number_required if threshold else 1
        active_process.authorization_number_required = threshold.authorization_number_required if threshold else 1
        active_process.finance_release_number_required = threshold.finance_release_number_required if threshold else 1
        active_process.save(
            update_fields=[
                "approval_number_required",
                "authorization_number_required",
                "finance_release_number_required",
            ]
        )


def copy_abort_and_closure_to_instructions(apps, schema_editor):
    """Take the abort comment and the closing user from the child plans, which all got the same ones.

    The closure comment is not copied: closing an instruction stored a fixed placeholder on its plans.
    """
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    FollowUpInstruction = apps.get_model("payment", "FollowUpInstruction")

    aborted_child = PaymentPlan.objects.filter(
        follow_up_instruction_id=OuterRef("pk"), is_removed=False, status="ABORTED"
    ).order_by("created_at")
    FollowUpInstruction.objects.filter(Exists(aborted_child)).update(
        abort_comment=Subquery(aborted_child.values("abort_comment")[:1])
    )
    closed_child = PaymentPlan.objects.filter(
        follow_up_instruction_id=OuterRef("pk"), is_removed=False, status="CLOSED", closed_by__isnull=False
    ).order_by("created_at")
    FollowUpInstruction.objects.filter(Exists(closed_child)).update(
        closed_by_id=Subquery(closed_child.values("closed_by_id")[:1])
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0041_migration"),
        ("payment", "0094_migration"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="approvalprocess",
            name="approval_process_owned_by_plan_or_group",
        ),
        migrations.AddField(
            model_name="approvalprocess",
            name="follow_up_instruction",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="approval_process",
                to="payment.followupinstruction",
            ),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="abort_comment",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="closed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="closure_comment",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="followupinstruction",
            name="export_pdf_file_summary",
            field=models.ForeignKey(
                blank=True,
                help_text="Generated summary PDF",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.filetemp",
            ),
        ),
        migrations.AddConstraint(
            model_name="approvalprocess",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ("follow_up_instruction__isnull", True),
                        ("payment_plan__isnull", False),
                        ("payment_plan_group__isnull", True),
                    ),
                    models.Q(
                        ("follow_up_instruction__isnull", True),
                        ("payment_plan__isnull", True),
                        ("payment_plan_group__isnull", False),
                    ),
                    models.Q(
                        ("follow_up_instruction__isnull", False),
                        ("payment_plan__isnull", True),
                        ("payment_plan_group__isnull", True),
                    ),
                    _connector="OR",
                ),
                name="approval_process_has_one_owner",
            ),
        ),
        # Not reversible: approval processes moved to an instruction cannot be handed back to one plan. The database
        # copy taken before the release is the rollback.
        migrations.RunPython(move_approval_processes_to_instructions, migrations.RunPython.noop),
        migrations.RunPython(copy_abort_and_closure_to_instructions, migrations.RunPython.noop),
        migrations.AddField(
            model_name="paymentplangroup",
            name="internal_data",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
