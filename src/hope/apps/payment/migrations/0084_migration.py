from collections import defaultdict

from django.db import migrations
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.db.models import Count, Exists, F, Max, Min, OuterRef, Q, Subquery, Sum

# These plans have no exchange rate yet: it is fetched when a plan is opened.
PLAN_STATUSES_WITHOUT_RATE = frozenset(
    {"TP_OPEN", "TP_LOCKED", "STEFICON_WAIT", "STEFICON_RUN", "STEFICON_COMPLETED", "STEFICON_ERROR", "DRAFT"}
)


# A plan before the FSP lock belongs to an OPEN group; the FSP lock is the group lock.
PRE_LOCK_PLAN_STATUSES = PLAN_STATUSES_WITHOUT_RATE | {"OPEN", "LOCKED"}
# Other statuses map to themselves.
GROUP_STAGE_BY_PLAN_STATUS = dict.fromkeys(PRE_LOCK_PLAN_STATUSES, "OPEN") | {"LOCKED_FSP": "LOCKED"}
MID_APPROVAL_STATUSES = ("IN_APPROVAL", "IN_AUTHORIZATION", "IN_REVIEW")
CHILD_GROUP_LABELS = {"FOLLOW_UP": "Follow Up", "TOP_UP": "Top Up", "TOP_UP_AMENDMENT": "Top Up Amendment"}
OWNER_FIELDS = ("payment_plan_group", "follow_up_instruction")


# When a group is split, the part whose plans are furthest along stays in the group; the rest move to new groups.
STAGE_ORDER = (
    "ABORTED",
    "OPEN",
    "LOCKED",
    "IN_APPROVAL",
    "IN_AUTHORIZATION",
    "IN_REVIEW",
    "ACCEPTED",
    "FINISHED",
    "READY_FOR_CLOSURE",
    "CLOSED",
)


PLAN_FIELDS = (
    "id",
    "payment_plan_group_id",
    "plan_type",
    "follow_up_instruction_id",
    "source_payment_plan_id",
    "status",
    "financial_service_provider_id",
    "currency_id",
    "use_payment_gateway",
    "exchange_rate",
)


def split_groups_whose_plans_differ(apps, schema_editor):
    """Split every group whose plans differ in status stage, FSP, currency, payment gateway flag or exchange rate."""
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    PaymentPlanGroup = apps.get_model("payment", "PaymentPlanGroup")
    plans_by_group = defaultdict(list)
    for plan in (
        PaymentPlan.objects.filter(is_removed=False, payment_plan_group__isnull=False)
        .order_by("created_at")
        .values(*PLAN_FIELDS)
    ):
        plans_by_group[plan["payment_plan_group_id"]].append(plan)

    for group_id, plans in plans_by_group.items():
        parts = split_plans_into_parts(plans)
        if len(parts) == 1:
            continue
        group = PaymentPlanGroup.objects.get(pk=group_id)
        for part in parts[1:]:
            new_group = PaymentPlanGroup.objects.create(
                cycle_id=group.cycle_id, name=_free_split_name(PaymentPlanGroup.objects, group)
            )
            PaymentPlan.objects.filter(pk__in=[plan["id"] for plan in part]).update(payment_plan_group=new_group)


def split_plans_into_parts(plans):
    """Return the plans of one group in parts that can each share a group, the part that stays in the group first.

    Regular plans decide the parts; a missing FSP, currency or rate does not count as a difference. Follow-ups, top-ups
    and Follow-Up Instruction children (still in their source plan's group until move_instruction_children_out_of_groups
    takes them out) go with their source plan; when the source plan is in another group, they stay in this one.
    """
    regular = [plan for plan in plans if _is_regular(plan)]
    followers = [plan for plan in plans if not _is_regular(plan)]
    if not regular:
        return [plans]

    plans_by_key = {}
    # Place plans that have every value first, so they decide the parts; a plan missing a value then just joins one.
    for plan in sorted(regular, key=lambda plan: _split_key(plan).count(None)):
        key = _split_key(plan)
        matching_key = next((part_key for part_key in plans_by_key if _same_values(part_key, key)), key)
        plans_by_key.setdefault(matching_key, []).append(plan)
    furthest_along_first = sorted(plans_by_key, key=lambda key: STAGE_ORDER.index(key[0]), reverse=True)
    parts = [plans_by_key[key] for key in furthest_along_first]

    part_by_plan_id = {plan["id"]: part for part in parts for plan in part}
    for follower in followers:
        part_by_plan_id.get(follower["source_payment_plan_id"], parts[0]).append(follower)
    return parts


def _is_regular(plan):
    return plan["plan_type"] == "REGULAR" and not plan["follow_up_instruction_id"]


def _split_key(plan):
    status = plan["status"]
    return (
        GROUP_STAGE_BY_PLAN_STATUS.get(status, status),
        plan["use_payment_gateway"],
        plan["financial_service_provider_id"],
        plan["currency_id"],
        None if status in PLAN_STATUSES_WITHOUT_RATE else plan["exchange_rate"],
    )


def _same_values(part_key, key):
    return all(a is None or b is None or a == b for a, b in zip(part_key, key, strict=True))


def _free_split_name(groups, group):
    sequence_number = 2
    while True:
        name = f"{group.name[:240]} ({sequence_number})"
        if not groups.filter(cycle_id=group.cycle_id, name=name).exists():
            return name
        sequence_number += 1


def copy_values_from_payment_plans(apps, schema_editor):
    """Give every group the FSP / currency its payment plans agree on.

    After the split only a follow-up or top-up whose FSP or currency differs from its source plan can disagree; such a
    group stops the migration.
    """
    PaymentPlanGroup = apps.get_model("payment", "PaymentPlanGroup")
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    counted = PaymentPlanGroup.objects.annotate(
        fsps=Count(
            "payment_plans__financial_service_provider", distinct=True, filter=Q(payment_plans__is_removed=False)
        ),
        currencies=Count("payment_plans__currency", distinct=True, filter=Q(payment_plans__is_removed=False)),
    )
    mixed = list(counted.filter(Q(fsps__gt=1) | Q(currencies__gt=1)).values_list("unicef_id", flat=True))
    if mixed:
        raise RuntimeError(
            "Payment Plan Groups whose plans use more than one FSP or currency must be aligned before "
            f"this migration can run: {', '.join(mixed)}"
        )
    PaymentPlanGroup.objects.update(
        financial_service_provider_id=_first_value(PaymentPlan, "financial_service_provider"),
        currency_id=_first_value(PaymentPlan, "currency"),
    )


def _first_value(payment_plan_model, field):
    return Subquery(
        payment_plan_model.objects.filter(
            payment_plan_group=OuterRef("pk"), is_removed=False, **{f"{field}__isnull": False}
        ).values(f"{field}_id")[:1]
    )


def move_instruction_children_out_of_groups(apps, schema_editor):
    """Give every Follow-Up Instruction the FSP / currency its children had through their group, then take them out.

    An instruction is only created over source plans sharing one FSP and one currency, so any child's group has them.
    """
    FollowUpInstruction = apps.get_model("payment", "FollowUpInstruction")
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    children_in_group = PaymentPlan.objects.filter(
        follow_up_instruction=OuterRef("pk"), payment_plan_group__isnull=False
    ).order_by("created_at")
    FollowUpInstruction.objects.filter(Exists(children_in_group)).update(
        financial_service_provider_id=Subquery(
            children_in_group.values("payment_plan_group__financial_service_provider")[:1]
        ),
        currency_id=Subquery(children_in_group.values("payment_plan_group__currency")[:1]),
    )
    PaymentPlan.objects.filter(follow_up_instruction__isnull=False).update(payment_plan_group=None)


def put_instruction_children_back_into_groups(apps, schema_editor):
    """Return every Follow-Up Instruction child to the group of the plan it follows up."""
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    source_plan_group = PaymentPlan.objects.filter(pk=OuterRef("source_payment_plan")).values("payment_plan_group")[:1]
    PaymentPlan.objects.filter(follow_up_instruction__isnull=False, payment_plan_group__isnull=True).update(
        payment_plan_group_id=Subquery(source_plan_group)
    )


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

    for group in PaymentPlanGroup.objects.filter(status__in=MID_APPROVAL_STATUSES).select_related(
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


def copy_dates_from_payment_plans(apps, schema_editor):
    """Use the earliest start and latest end from each owner's plans."""
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    database_alias = schema_editor.connection.alias
    for owner_model, owner_field in (
        (apps.get_model("payment", "PaymentPlanGroup"), "payment_plan_group"),
        (apps.get_model("payment", "FollowUpInstruction"), "follow_up_instruction"),
    ):
        plans = (
            PaymentPlan.objects.using(database_alias)
            .filter(**{owner_field: OuterRef("pk")}, is_removed=False)
            .values(owner_field)
        )
        owner_model.objects.using(database_alias).update(
            dispersion_start_date=Subquery(plans.annotate(value=Min("dispersion_start_date")).values("value")[:1]),
            dispersion_end_date=Subquery(plans.annotate(value=Max("dispersion_end_date")).values("value")[:1]),
        )


def copy_exchange_rates_from_payment_plans(apps, schema_editor):
    """Give every group and instruction the exchange rate of its opened plans.

    Like the split, a missing rate is not a difference: plans before OPEN have no rate yet (or a stale one), and a
    plan opened while the rate feed was down has none. Only two different rates among opened plans stop the
    migration.
    """
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    plans = PaymentPlan.objects.using(schema_editor.connection.alias).filter(is_removed=False)
    unowned = plans.filter(payment_plan_group__isnull=True, follow_up_instruction__isnull=True).filter(
        Q(exchange_rate__isnull=False) | Q(custom_exchange_rate=True) | Q(custom_exchange_rate_set_by__isnull=False)
    )
    if unowned.exists():
        raise RuntimeError("Payment plans without a group or Follow-Up Instruction have exchange-rate data.")

    rated = plans.exclude(status__in=PLAN_STATUSES_WITHOUT_RATE)
    for owner_field, model_name in (
        ("payment_plan_group", "PaymentPlanGroup"),
        ("follow_up_instruction", "FollowUpInstruction"),
    ):
        owner_model = apps.get_model("payment", model_name).objects.using(schema_editor.connection.alias)
        conflicts = (
            rated.filter(**{f"{owner_field}__isnull": False})
            .values(owner_field)
            .annotate(rate_count=Count("exchange_rate", distinct=True))
            .filter(rate_count__gt=1)
            .values_list(owner_field, flat=True)
        )
        mixed = list(owner_model.filter(pk__in=conflicts).values_list("unicef_id", flat=True))
        if mixed:
            raise RuntimeError(f"Payment plans of one {model_name} have different exchange rates: {mixed}.")

        source = rated.filter(**{owner_field: OuterRef("pk")}).order_by(
            F("exchange_rate").desc(nulls_last=True),
            F("custom_exchange_rate_set_by_id").desc(nulls_last=True),
            "created_at",
        )
        owner_model.filter(Exists(source)).update(
            exchange_rate=Subquery(source.values("exchange_rate")[:1]),
            custom_exchange_rate=Subquery(source.values("custom_exchange_rate")[:1]),
            custom_exchange_rate_set_by_id=Subquery(source.values("custom_exchange_rate_set_by_id")[:1]),
        )


def copy_exchange_rates_to_payment_plans(apps, schema_editor):
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    for owner_field, model_name in (
        ("payment_plan_group", "PaymentPlanGroup"),
        ("follow_up_instruction", "FollowUpInstruction"),
    ):
        owner_model = apps.get_model("payment", model_name)
        owner = owner_model.objects.using(schema_editor.connection.alias).filter(pk=OuterRef(f"{owner_field}_id"))
        PaymentPlan.objects.using(schema_editor.connection.alias).filter(**{f"{owner_field}__isnull": False}).update(
            exchange_rate=Subquery(owner.values("exchange_rate")[:1]),
            custom_exchange_rate=Subquery(owner.values("custom_exchange_rate")[:1]),
            custom_exchange_rate_set_by_id=Subquery(owner.values("custom_exchange_rate_set_by_id")[:1]),
        )


def copy_flag_from_payment_plans(apps, schema_editor):
    """Give every group and Follow-Up Instruction the use_payment_gateway flag of its payment plans.

    A group is sent to the payment gateway as one, so its plans must agree on the flag; a group or
    instruction whose plans disagree stops the migration until the plans are fixed.
    """
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    owner_models = {
        "payment_plan_group": apps.get_model("payment", "PaymentPlanGroup"),
        "follow_up_instruction": apps.get_model("payment", "FollowUpInstruction"),
    }
    plans = PaymentPlan.objects.filter(is_removed=False)
    mixed = {
        owner_field: list(
            plans.filter(**{f"{owner_field}__isnull": False})
            .values(f"{owner_field}__unicef_id")
            .annotate(flags=Count("use_payment_gateway", distinct=True))
            .filter(flags__gt=1)
            .values_list(f"{owner_field}__unicef_id", flat=True)
        )
        for owner_field in OWNER_FIELDS
    }
    if any(mixed.values()):
        raise RuntimeError(
            "Payment plans of one group or Follow-Up Instruction have different use_payment_gateway values; "
            f"set them to the same value first. Groups: {mixed['payment_plan_group']}. "
            f"Follow-Up Instructions: {mixed['follow_up_instruction']}."
        )
    for owner_field, owner_model in owner_models.items():
        owner_model.objects.update(
            use_payment_gateway=Exists(
                plans.filter(**{owner_field: OuterRef("pk")}, use_payment_gateway=True),
            )
        )


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


def clear_legacy_payment_plan_custom_rate_statuses(apps, schema_editor):
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    PaymentPlan._base_manager.using(schema_editor.connection.alias).filter(
        background_action_status__in=("APPLYING_CUSTOM_EXCHANGE_RATE", "APPLYING_CUSTOM_EXCHANGE_RATE_ERROR")
    ).update(background_action_status=None)


def move_documents_to_groups_and_instructions(apps, schema_editor):
    """Attach every supporting document to its plan's Follow-Up Instruction, or else to its plan's group.

    A plan removed before groups existed (0069 grouped live plans only) has neither, so its documents go with it.
    """
    PaymentPlan = apps.get_model("payment", "PaymentPlan")
    PaymentPlanSupportingDocument = apps.get_model("payment", "PaymentPlanSupportingDocument")
    PaymentPlanSupportingDocument.objects.filter(
        payment_plan__payment_plan_group__isnull=True, payment_plan__follow_up_instruction__isnull=True
    ).delete()
    plan = PaymentPlan.objects.filter(pk=OuterRef("payment_plan_id"))
    PaymentPlanSupportingDocument.objects.filter(payment_plan__follow_up_instruction__isnull=False).update(
        follow_up_instruction_id=Subquery(plan.values("follow_up_instruction_id")[:1])
    )
    PaymentPlanSupportingDocument.objects.filter(payment_plan__follow_up_instruction__isnull=True).update(
        payment_plan_group_id=Subquery(plan.values("payment_plan_group_id")[:1])
    )


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0083_migration"),
    ]

    # Only the Follow-Up Instruction children and the exchange rates go back on a rollback: split groups are not merged
    # back, and approval processes and documents moved to a group or instruction are not handed back to one plan. The
    # database copy taken before the release is the rollback.
    operations = [
        migrations.RunPython(split_groups_whose_plans_differ, migrations.RunPython.noop),
        migrations.RunPython(copy_values_from_payment_plans, migrations.RunPython.noop),
        migrations.RunPython(move_instruction_children_out_of_groups, put_instruction_children_back_into_groups),
        migrations.RunPython(move_legacy_child_plans_into_linked_groups, migrations.RunPython.noop),
        migrations.RunPython(set_group_statuses_from_plans, migrations.RunPython.noop),
        migrations.RunPython(move_approval_processes_to_groups, migrations.RunPython.noop),
        migrations.RunPython(copy_dates_from_payment_plans, migrations.RunPython.noop),
        migrations.RunPython(copy_exchange_rates_from_payment_plans, copy_exchange_rates_to_payment_plans),
        migrations.RunPython(copy_flag_from_payment_plans, migrations.RunPython.noop),
        migrations.RunPython(move_approval_processes_to_instructions, migrations.RunPython.noop),
        migrations.RunPython(copy_abort_and_closure_to_instructions, migrations.RunPython.noop),
        migrations.RunPython(clear_legacy_payment_plan_custom_rate_statuses, migrations.RunPython.noop),
        migrations.RunPython(move_documents_to_groups_and_instructions, migrations.RunPython.noop),
    ]
