from collections import defaultdict

from django.db import migrations
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.db.models import Max, OuterRef, Subquery, Sum

CHILD_GROUP_LABELS = {"FOLLOW_UP": "Follow Up", "TOP_UP": "Top Up", "TOP_UP_AMENDMENT": "Top Up Amendment"}
# A plan before the FSP lock belongs to an OPEN group; the FSP lock is the group lock.
PRE_LOCK_PLAN_STATUSES = frozenset(
    {
        "TP_OPEN",
        "TP_LOCKED",
        "STEFICON_WAIT",
        "STEFICON_RUN",
        "STEFICON_COMPLETED",
        "STEFICON_ERROR",
        "DRAFT",
        "OPEN",
        "LOCKED",
    }
)
MID_APPROVAL_GROUP_STATUSES = ("IN_APPROVAL", "IN_AUTHORIZATION", "IN_REVIEW")


def group_status_for_plan_statuses(plan_statuses):
    """Return the one group status all plans imply, or None when they disagree. An empty group is OPEN."""
    implied = set()
    for plan_status in plan_statuses:
        if plan_status in PRE_LOCK_PLAN_STATUSES:
            implied.add("OPEN")
        elif plan_status == "LOCKED_FSP":
            implied.add("LOCKED")
        else:
            implied.add(plan_status)
    if not implied:
        return "OPEN"
    if len(implied) > 1:
        return None
    return implied.pop()


def move_legacy_child_plans_into_linked_groups(apps, schema_editor):
    """Give every follow-up / top-up / amendment still sitting in a Standard group a linked group of its own.

    Children of one source group, one type and one status share a linked group, so each new group has one status.
    Follow-Up Instruction children are not in any group and are left alone.
    """
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    PaymentPlanGroup = apps.get_model("payment", "PaymentPlanGroup")
    legacy_children = (
        PaymentPlan.objects.filter(is_removed=False, payment_plan_group__plan_type="REGULAR")
        .exclude(plan_type="REGULAR")
        .select_related("payment_plan_group")
        .order_by("created_at")
    )
    buckets = defaultdict(list)
    for child in legacy_children:
        buckets[(child.payment_plan_group, child.plan_type, group_status_for_plan_statuses([child.status]))].append(
            child
        )
    for (source_group, plan_type, status), children in buckets.items():
        linked_group = PaymentPlanGroup.objects.create(
            cycle_id=source_group.cycle_id,
            name=_free_linked_group_name(PaymentPlanGroup.objects, source_group, plan_type),
            plan_type=plan_type,
            source_group=source_group,
            financial_service_provider_id=source_group.financial_service_provider_id,
            currency_id=source_group.currency_id,
            status=status,
            status_date=max(child.status_date for child in children if child.status_date),
        )
        PaymentPlan.objects.filter(pk__in=[child.pk for child in children]).update(payment_plan_group=linked_group)


def _free_linked_group_name(groups, source_group, plan_type):
    sequence_number = groups.filter(source_group=source_group, plan_type=plan_type).count() + 1
    while True:
        name = f"{source_group.name} {CHILD_GROUP_LABELS[plan_type]} {sequence_number}"
        if not groups.filter(cycle_id=source_group.cycle_id, name=name).exists():
            return name
        sequence_number += 1


def set_group_statuses_from_plans(apps, schema_editor):
    """Give every group the status its components agree on; refuse, naming the groups, while any group is mixed."""
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    PaymentPlanGroup = apps.get_model("payment", "PaymentPlanGroup")
    plans = PaymentPlan.objects.filter(is_removed=False, payment_plan_group__isnull=False).values_list(
        "payment_plan_group_id", "status"
    )
    statuses_by_group = defaultdict(list)
    for group_id, status in plans:
        statuses_by_group[group_id].append(status)

    mixed = []
    for group in PaymentPlanGroup.objects.all():
        status = group_status_for_plan_statuses(statuses_by_group.get(group.id, []))
        if status is None:
            mixed.append(group.unicef_id)
            continue
        status_date = PaymentPlan.objects.filter(payment_plan_group=group, is_removed=False).aggregate(
            latest=Max("status_date")
        )["latest"]
        PaymentPlanGroup.objects.filter(pk=group.pk).update(status=status, status_date=status_date or group.status_date)
    if mixed:
        raise RuntimeError(
            "Payment Plan Groups whose plans are in different statuses must be aligned before this migration can "
            f"run: {', '.join(sorted(mixed))}"
        )


def move_approval_processes_to_groups(apps, schema_editor):
    """Attach every approval process of a grouped plan to the plan's group, then size the open ones from the group total.

    Instruction children keep their own processes. A group with several moved processes shows them all; the newest
    is the active one and gets the required numbers for the group's summed USD total.
    """
    ApprovalProcess = apps.get_model("payment", "ApprovalProcess")
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    PaymentPlanGroup = apps.get_model("payment", "PaymentPlanGroup")
    AcceptanceProcessThreshold = apps.get_model("payment", "AcceptanceProcessThreshold")

    plan_group = PaymentPlan.objects.filter(pk=OuterRef("payment_plan_id")).values("payment_plan_group_id")[:1]
    ApprovalProcess.objects.filter(payment_plan__isnull=False, payment_plan__payment_plan_group__isnull=False).update(
        payment_plan_group_id=Subquery(plan_group), payment_plan=None
    )

    for group in PaymentPlanGroup.objects.filter(status__in=MID_APPROVAL_GROUP_STATUSES).select_related(
        "cycle__program__business_area"
    ):
        active_process = ApprovalProcess.objects.filter(payment_plan_group=group).order_by("-created_at").first()
        if active_process is None:
            continue
        total_usd = int(
            PaymentPlan.objects.filter(payment_plan_group=group, is_removed=False).aggregate(
                total=Sum("total_entitled_quantity_usd")
            )["total"]
            or 0
        )
        threshold = AcceptanceProcessThreshold.objects.filter(
            business_area=group.cycle.program.business_area,
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


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0084_migration"),
    ]

    # Not reversible: approval processes moved to a group cannot be handed back to one plan. The database copy
    # taken before the release is the rollback.
    operations = [
        migrations.RunPython(move_legacy_child_plans_into_linked_groups, migrations.RunPython.noop),
        migrations.RunPython(set_group_statuses_from_plans, migrations.RunPython.noop),
        migrations.RunPython(move_approval_processes_to_groups, migrations.RunPython.noop),
    ]
