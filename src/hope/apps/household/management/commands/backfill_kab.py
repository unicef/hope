"""Backfill known affected beneficiaries (KAB) counters on households.

Idempotent, safe to re-run. Iterates program by program so every query is bounded
by the indexed program_id instead of scanning the whole household table, and only
pk lists are ever held in memory.

Two phases per program:
  1. Composition present (any age-group field set) -> bulk-copy stored composition into kab_ columns.
  2. Composition absent + DCT collects individual data -> recompute from linked individuals.
     kab_size is never NULL once computed, so already-processed households are skipped
     and an interrupted run resumes where it left off.
Households matching neither phase keep NULL KAB (unknown, by definition).
"""

from collections.abc import Iterator
import functools
import operator
import time

from django.core.management.base import BaseCommand, CommandParser
from django.db.models import F, Q, QuerySet

from hope.apps.household.services.household_recalculate_data import (
    AGE_GROUP_FIELDS,
    KAB_SOURCE_FIELDS,
    aggregate_composition_by_household_id,
)
from hope.models import Household, Program

COMPOSITION_PRESENT = functools.reduce(operator.or_, (Q(**{f"{field}__isnull": False}) for field in AGE_GROUP_FIELDS))
KAB_FIELDS = [f"kab_{field}" for field in KAB_SOURCE_FIELDS]


def _pk_batches(queryset: QuerySet, batch_size: int) -> Iterator[list]:
    last_pk = None
    while True:
        batch = queryset if last_pk is None else queryset.filter(pk__gt=last_pk)
        pks = list(batch.order_by("pk").values_list("pk", flat=True)[:batch_size])
        if not pks:
            return
        yield pks
        last_pk = pks[-1]


class Command(BaseCommand):
    help = "Backfill kab_* counters on households (idempotent, program by program)."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--batch-size", type=int, default=5000)

    def handle(self, *args: str, **options: str) -> None:
        batch_size = int(options["batch_size"])
        copy = {f"kab_{field}": F(field) for field in KAB_SOURCE_FIELDS}
        copied = 0
        computed = 0
        programs = list(
            Program.all_objects.order_by("pk").values_list("pk", "data_collecting_type__collects_individual_data")
        )
        self.stdout.write(f"Backfilling KAB: {len(programs)} program(s), batch size {batch_size}")
        for index, (program_id, collects_individual_data) in enumerate(programs, start=1):
            prefix = f"[{index}/{len(programs)}] program {program_id}"
            program_copied = 0
            program_computed = 0
            households = Household.objects.filter(program_id=program_id)
            for pks in _pk_batches(households.filter(COMPOSITION_PRESENT), batch_size):
                batch_start = time.monotonic()
                program_copied += Household.objects.filter(pk__in=pks).update(**copy)
                self.stdout.write(
                    f"{prefix}: copied batch of {len(pks)} in {time.monotonic() - batch_start:.1f}s,"
                    f" total copied {program_copied}"
                )
            if collects_individual_data:
                to_compute = households.filter(~COMPOSITION_PRESENT, kab_size__isnull=True)
                for pks in _pk_batches(to_compute, batch_size):
                    batch_start = time.monotonic()
                    # ponytail: no per-row lock/transaction — the backfill is idempotent and any
                    # concurrent write re-triggers recalculate_data for its household anyway.
                    counts = aggregate_composition_by_household_id(pks)
                    updates = []
                    for pk in pks:
                        household = Household(pk=pk)
                        row = counts.get(pk)
                        for field in KAB_SOURCE_FIELDS:
                            setattr(household, f"kab_{field}", row[field] if row else 0)
                        updates.append(household)
                    Household.objects.bulk_update(updates, KAB_FIELDS, batch_size=500)
                    program_computed += len(pks)
                    self.stdout.write(
                        f"{prefix}: computed batch of {len(pks)} in {time.monotonic() - batch_start:.1f}s,"
                        f" total computed {program_computed}"
                    )
            copied += program_copied
            computed += program_computed
            self.stdout.write(f"{prefix}: done, copied {program_copied}, computed {program_computed}")
        self.stdout.write(
            self.style.SUCCESS(f"Copied stored composition: {copied}, recomputed from individuals: {computed}")
        )
