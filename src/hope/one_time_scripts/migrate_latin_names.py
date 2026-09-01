import json
import logging
import time

from django.db import transaction
from django.db.models import Q

from hope.models import Individual, Program

logger = logging.getLogger(__name__)

LATIN_FIELDS = ["full_name_latin", "given_name_latin", "middle_name_latin", "family_name_latin"]
NAME_FIELDS = ["full_name", "given_name", "middle_name", "family_name"]
MISSING_LATIN = (
    Q(full_name_latin__isnull=True)
    | Q(given_name_latin__isnull=True)
    | Q(middle_name_latin__isnull=True)
    | Q(family_name_latin__isnull=True)
)


def _report_failure(failures_file, individual: Individual, program: Program, reason: Exception) -> None:
    failures_file.write(
        json.dumps(
            {
                "individual_id": str(individual.pk),
                "unicef_id": individual.unicef_id,
                "program_id": str(program.pk),
                "program_name": program.name,
                "business_area": program.business_area.slug,
                "reason": str(reason),
                "names": {field: getattr(individual, field) for field in NAME_FIELDS},
            }
        )
        + "\n"
    )
    failures_file.flush()
    print(f"    FAILED {individual.unicef_id or individual.pk}: {reason}")


def _migrate_program(program: Program, batch_size: int, failures_file) -> tuple[int, int]:
    """Keyset-paginated pass over one program's individuals missing any latin name.

    Each batch is one short SELECT + one short transaction - no long-running
    cursor and no long transaction. set_names_latin() fills only empty latin
    fields, so already-populated rows are never overwritten and a re-run
    resumes on whatever is still missing.
    """
    updated = failed = batch_no = 0
    last_pk = None
    while True:
        qs = Individual.all_objects.filter(MISSING_LATIN, program_id=program.pk)
        if last_pk is not None:
            qs = qs.filter(pk__gt=last_pk)
        batch = list(qs.order_by("pk").only("pk", "unicef_id", *NAME_FIELDS, *LATIN_FIELDS)[:batch_size])
        if not batch:
            return updated, failed
        batch_no += 1
        batch_started_at = time.time()
        # advance the keyset even if every row in the batch fails, so bad data
        # cannot loop the migration forever
        last_pk = batch[-1].pk
        to_update = []
        for individual in batch:
            try:
                individual.set_names_latin()
                to_update.append(individual)
            except Exception as e:  # noqa: BLE001  # one bad record must never kill the run
                failed += 1
                _report_failure(failures_file, individual, program, e)
        if to_update:
            with transaction.atomic():
                Individual.all_objects.bulk_update(to_update, LATIN_FIELDS)
            updated += len(to_update)
        print(
            f"  ba={program.business_area.slug} program={program.name} batch={batch_no} "
            f"updated={updated} failed={failed} elapsed={time.time() - batch_started_at:.2f}s"
        )


def migrate_to_latin_names(batch_size: int = 1000, failures_path: str = "latin_migration_failures.jsonl") -> None:
    """Backfill latin name fields for all individuals, program by program, grouped by business area.

    Idempotent and resumable: only rows still missing a latin field are
    selected, and existing latin values are never overwritten. Rows that fail
    transliteration are skipped and appended to `failures_path` as JSONL.
    """
    started_at = time.time()
    total_updated = total_failed = 0

    programs = Program.objects.select_related("business_area").order_by("business_area__slug", "id")
    with open(failures_path, "a") as failures_file:
        for program in programs:
            updated, failed = _migrate_program(program, batch_size, failures_file)
            total_updated += updated
            total_failed += failed
            if updated or failed:
                print(f"ba={program.business_area.slug} program={program.name} done: updated={updated} failed={failed}")

    print(f"Done in {time.time() - started_at:.2f}s | updated={total_updated}, failed={total_failed}")
    if total_failed:
        print(f"Failed records written to {failures_path}")
