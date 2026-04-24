import time
from typing import List

from django.db import transaction
from django.db.models import Q

from hope.apps.household.utils import to_latin
from hope.models import Individual


def _bulk_update(batch_list: List[Individual], batch_size: int) -> None:
    with transaction.atomic():
        Individual.objects.bulk_update(
            batch_list,
            fields=[
                "full_name_latin",
                "given_name_latin",
                "middle_name_latin",
                "family_name_latin",
            ],
            batch_size=batch_size,
        )


def migrate_to_latin_names(batch_size: int = 500) -> None:
    """
    Populate latin name fields for Individual model
    """
    total_processed = 0
    total_updated = 0
    started_at = time.time()

    print("Starting latin name migration...")

    qs = (
        Individual.objects
        .filter(
            Q(full_name_latin__isnull=True) |
            Q(given_name_latin__isnull=True) |
            Q(middle_name_latin__isnull=True) |
            Q(family_name_latin__isnull=True)
        )
        .order_by("id")
        .iterator(chunk_size=batch_size)
    )

    to_update: List[Individual] = []

    for ind in qs:
        total_processed += 1
        updated = False

        if ind.full_name and not ind.full_name_latin:
            ind.full_name_latin = to_latin(ind.full_name)
            updated = True

        if ind.given_name and not ind.given_name_latin:
            ind.given_name_latin = to_latin(ind.given_name)
            updated = True

        if ind.middle_name and not ind.middle_name_latin:
            ind.middle_name_latin = to_latin(ind.middle_name)
            updated = True

        if ind.family_name and not ind.family_name_latin:
            ind.family_name_latin = to_latin(ind.family_name)
            updated = True

        if updated:
            to_update.append(ind)

        if len(to_update) >= batch_size:
            _bulk_update(to_update, batch_size)
            total_updated += len(to_update)
            to_update.clear()

            print(
                f"processed={total_processed}, updated={total_updated}"
            )

    # Final update
    if to_update:
        _bulk_update(to_update, batch_size)
        total_updated += len(to_update)

    duration = time.time() - started_at

    print(
        f"Done in {duration:.2f}s | processed={total_processed}, updated={total_updated}"
    )
