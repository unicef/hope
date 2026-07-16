"""Fix the PaymentPlanGroup backfill from migration 0069.

1) Move follow-up Payment Plans into their source plan's group and drop the group that
   0069 created for them.
2) Ensure every Programme Cycle has a Default Group.

Run from Django shell:
    from hope.one_time_scripts.fix_payment_plan_groups import fix_payment_plan_groups
    fix_payment_plan_groups()
"""
from django.db import transaction

from hope.models import PaymentPlan, PaymentPlanGroup, ProgramCycle

BATCH_SIZE = 2000
DEFAULT_GROUP_NAME = "Default Group"


def fix_payment_plan_groups() -> None:
    with transaction.atomic():
        print("Step 1/2: ensuring a Default Group in every cycle...")
        created_defaults = _ensure_default_group_per_cycle()
        print(f"  created {created_defaults} Default Group(s)")

        print("Step 2/2: moving follow-ups into their source plan's group...")
        moved_follow_ups, deleted_groups = _move_follow_ups_to_source_group()
        print(f"  reassigned {moved_follow_ups} follow-up(s), deleted {deleted_groups} orphaned group(s)")

    print("Done.")


def _ensure_default_group_per_cycle() -> int:
    """Create a Default Group for every cycle that lacks one."""
    cycle_ids = (
        ProgramCycle.objects.exclude(payment_plan_groups__name=DEFAULT_GROUP_NAME)
        .distinct()
        .values_list("id", flat=True)
    )
    groups = [PaymentPlanGroup(cycle_id=cid, name=DEFAULT_GROUP_NAME) for cid in cycle_ids]
    PaymentPlanGroup.objects.bulk_create(groups, batch_size=BATCH_SIZE, ignore_conflicts=True)
    return len(groups)


def _move_follow_ups_to_source_group() -> tuple[int, int]:
    """Point each follow-up at its source plan's group, then delete the now-empty groups they vacated."""
    follow_ups = (
        PaymentPlan.objects.filter(plan_type=PaymentPlan.PlanType.FOLLOW_UP, is_removed=False)
        .select_related("source_payment_plan")
        .only("id", "unicef_id", "payment_plan_group_id", "source_payment_plan__payment_plan_group_id")
    )

    old_follow_up_group_ids = set()
    to_update = []
    for follow_up in follow_ups:
        source = follow_up.source_payment_plan
        target_group_id = source.payment_plan_group_id if source else None
        # In case source was soft-deleted
        if target_group_id is None:
            print(f"    ! {follow_up.unicef_id}: source has no group, left untouched")
            continue
        if follow_up.payment_plan_group_id == target_group_id:
            continue
        if follow_up.payment_plan_group_id:
            old_follow_up_group_ids.add(follow_up.payment_plan_group_id)
        follow_up.payment_plan_group_id = target_group_id
        to_update.append(follow_up)
        print(f"    ~ {follow_up.unicef_id} -> group {target_group_id}")

    PaymentPlan.objects.bulk_update(to_update, ["payment_plan_group_id"], batch_size=BATCH_SIZE)

    # Only remove groups that are now empty; keep any Default Group.
    orphaned = PaymentPlanGroup.objects.filter(id__in=old_follow_up_group_ids, payment_plans__isnull=True).exclude(
        name=DEFAULT_GROUP_NAME
    )
    for name, gid in orphaned.values_list("name", "id"):
        print(f"    - deleting empty group '{name}' ({gid})")
    deleted_count, _ = orphaned.delete()
    return len(to_update), deleted_count
