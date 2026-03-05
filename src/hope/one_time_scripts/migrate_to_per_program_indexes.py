"""
Migrate to per-program Elasticsearch indexes.

Run from Django shell:
    from hope.one_time_scripts.migrate_to_per_program_indexes import migrate_to_per_program_indexes
    migrate_to_per_program_indexes()  # default: 8 parallel workers
"""
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.conf import settings
from elasticsearch import Elasticsearch
from hope.models import Program
from hope.apps.household.services.index_management import rebuild_program_indexes


OLD_INDEXES = [
    "individuals_afghanistan",
    "individuals_ukraine",
    "individuals_others",
    "households",
]


def _delete_old_indexes() -> None:
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    prefix = settings.ELASTICSEARCH_INDEX_PREFIX
    for name in OLD_INDEXES:
        index = f"{prefix}{name}"
        if es.indices.exists(index=index):
            es.indices.delete(index=index)
            print(f"Deleted old index: {index}")
        else:
            print(f"Old index not found (skipping): {index}")


def migrate_to_per_program_indexes(batch_size: int = 1000, max_workers: int = 8) -> None:
    _delete_old_indexes()

    active_programs = list(Program.objects.filter(status=Program.ACTIVE).select_related("business_area"))
    total = len(active_programs)
    print(f"Found {total} active programs")

    success_count = 0
    failed = []

    def _rebuild(program):
        print(f"{program.name} ({program.business_area.slug}) - starting")
        success, message = rebuild_program_indexes(str(program.id), batch_size=batch_size)
        return program.name, success, message

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_rebuild, p): p for p in active_programs}
        for i, future in enumerate(as_completed(futures), 1):
            name, success, message = future.result()
            if success:
                print(f"[{i}/{total}] {name}: {message}")
                success_count += 1
            else:
                print(f"[ERROR] [{i}/{total}] {name}: {message}")
                failed.append(name)

    print(f"Done: {success_count}/{total} succeeded")
    if failed:
        print(f"Failed: {', '.join(failed)}")
