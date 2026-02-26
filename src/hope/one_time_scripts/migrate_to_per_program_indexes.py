"""
Migrate to per-program Elasticsearch indexes.

Run from Django shell:
    from hope.one_time_scripts.migrate_to_per_program_indexes import migrate_to_per_program_indexes
    migrate_to_per_program_indexes()
"""
import logging
from django.conf import settings
from elasticsearch import Elasticsearch
from hope.models import Program
from hope.apps.household.index_management import rebuild_program_indexes

logger = logging.getLogger(__name__)


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
            logger.info(f"Deleted old index: {index}")
        else:
            logger.info(f"Old index not found (skipping): {index}")


def migrate_to_per_program_indexes(batch_size: int = 1000) -> None:
    _delete_old_indexes()

    active_programs = Program.objects.filter(status=Program.ACTIVE).select_related("business_area")
    total = active_programs.count()
    logger.info(f"Found {total} active programs")

    success_count = 0
    failed = []

    for i, program in enumerate(active_programs, 1):
        logger.info(f"[{i}/{total}] {program.name} ({program.business_area.slug})")
        success, message = rebuild_program_indexes(str(program.id), batch_size=batch_size)
        if success:
            logger.info(f"{message}")
            success_count += 1
        else:
            logger.error(f"{message}")
            failed.append(program.name)

    logger.info(f"Done: {success_count}/{total} succeeded")
    if failed:
        logger.error(f"Failed: {', '.join(failed)}")
