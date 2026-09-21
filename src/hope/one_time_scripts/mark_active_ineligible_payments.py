"""Mark active, pending payments with an ineligibility condition as Not Eligible.

Run from a production Django shell:
    from hope.one_time_scripts.mark_active_ineligible_payments import mark_active_ineligible_payments

    mark_active_ineligible_payments()  # dry run
    mark_active_ineligible_payments(dry_run=False)
"""

from django.db import transaction
from django.db.models import Count, Q, QuerySet

from hope.models import BusinessArea, Payment, Program


def _candidate_payments() -> QuerySet[Payment]:
    return Payment.objects.filter(
        Q(conflicted=True) | Q(excluded=True) | Q(has_valid_wallet=False),
        is_removed=False,
        status=Payment.STATUS_PENDING,
    )


def mark_active_ineligible_payments(*, dry_run: bool = True) -> dict[str, object]:
    mode = "dry run" if dry_run else "live run"
    print(f"Starting {mode}: scanning for active ineligible Pending payments...", flush=True)
    candidate_groups = list(
        _candidate_payments().values("business_area_id", "program_id").annotate(candidate_count=Count("pk"))
    )
    business_areas = BusinessArea.objects.in_bulk({group["business_area_id"] for group in candidate_groups})
    programs = Program._base_manager.in_bulk(
        {group["program_id"] for group in candidate_groups if group["program_id"] is not None}
    )
    candidate_groups.sort(
        key=lambda group: (
            business_areas[group["business_area_id"]].slug,
            group["program_id"] is None,
            programs[group["program_id"]].name if group["program_id"] is not None else "",
        )
    )
    group_summaries: list[dict[str, object]] = []
    total_candidate_count = 0
    total_updated_count = 0
    total_groups = len(candidate_groups)
    discovered_candidate_count = sum(group["candidate_count"] for group in candidate_groups)
    print(
        f"Found {discovered_candidate_count:,} candidate payments across {total_groups:,} "
        "business area/program groups.",
        flush=True,
    )

    for group_number, candidate_group in enumerate(candidate_groups, start=1):
        business_area_id = candidate_group["business_area_id"]
        program_id = candidate_group["program_id"]
        candidate_count = candidate_group["candidate_count"]
        group_filter: dict[str, object] = {"business_area_id": business_area_id}
        if program_id is None:
            group_filter["program_id__isnull"] = True
        else:
            group_filter["program_id"] = program_id

        business_area = business_areas[business_area_id].slug
        program = programs[program_id].name if program_id is not None else None
        group_label = f"[{group_number:,}/{total_groups:,}] {business_area} / {program or '[no program]'}"
        candidate_label = "candidate" if candidate_count == 1 else "candidates"
        updated_count = 0
        if dry_run:
            print(f"{group_label}: {candidate_count:,} {candidate_label} (dry run).", flush=True)
        else:
            print(f"{group_label}: updating {candidate_count:,} {candidate_label}...", flush=True)
            with transaction.atomic():
                updated_count = _candidate_payments().filter(**group_filter).update(status=Payment.STATUS_NOT_ELIGIBLE)
            print(f"{group_label}: committed {updated_count:,} updates.", flush=True)

        group_summaries.append(
            {
                "business_area_id": str(business_area_id),
                "business_area": business_area,
                "program_id": str(program_id) if program_id else None,
                "program": program,
                "candidate_count": candidate_count,
                "updated_count": updated_count,
            }
        )
        total_candidate_count += candidate_count
        total_updated_count += updated_count

    if dry_run:
        print(
            f"Dry run complete: {total_candidate_count:,} payments would be marked across "
            f"{total_groups:,} business area/program groups.",
            flush=True,
        )
    else:
        print(
            f"Live run complete: committed {total_updated_count:,} updates across "
            f"{total_groups:,} business area/program groups.",
            flush=True,
        )
    return {
        "dry_run": dry_run,
        "candidate_count": total_candidate_count,
        "updated_count": total_updated_count,
        "groups": group_summaries,
    }
