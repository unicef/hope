import logging

from django.db import migrations

logger = logging.getLogger(__name__)

ALL_EXCEPT_COUNTRY_WORKSPACE = "ALL_EXCEPT_COUNTRY_WORKSPACE"


def disable_biometric_deduplication_for_non_cw(apps, schema_editor):
    """Biometric deduplication is driven exclusively by the Country Workspace pipeline.

    For a business area that does not ingest from CW nothing writes
    ``dedup_engine_batch_duplicates`` / ``dedup_engine_golden_record_duplicates`` any more, so the
    counters stay at their default of 0 and the RDI details page renders them as "100% unique"
    (``number_of_individuals - 0``) — a scan that never ran, shown as a scan that found nothing.
    Turning the flag off makes the serializer omit the biometric column instead of computing it.
    """
    Program = apps.get_model("program", "Program")
    updated = Program.objects.filter(
        biometric_deduplication_enabled=True,
        business_area__ingest_source=ALL_EXCEPT_COUNTRY_WORKSPACE,
    ).update(biometric_deduplication_enabled=False)
    logger.info("Disabled biometric deduplication on %s non-CW program(s).", updated)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0033_migration"),
        ("program", "0020_migration"),
    ]

    operations = [
        # Irreversible by design: the pre-migration value is not recorded anywhere, and re-enabling
        # the flag would restore the misleading "100% unique" figures.
        migrations.RunPython(disable_biometric_deduplication_for_non_cw, migrations.RunPython.noop),
    ]
