import logging

from hct_mis_api.apps.household.models import (
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    NEEDS_ADJUDICATION,
    SIMILAR_IN_BATCH,
    UNIQUE,
    UNIQUE_IN_BATCH,
    Individual,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport

logger = logging.getLogger(__name__)


def migrate_rdi_deduplication_statistics() -> None:
    rdi_to_update = []
    logger.info("Updating RDI deduplication stats started")

    try:
        for (
            registration_data_import
        ) in RegistrationDataImport.objects.all():  # 2800 objects in prod, we can do it in one shot
            registration_data_import.batch_duplicates = Individual.objects.filter(
                registration_data_import_id=registration_data_import.id,
                deduplication_batch_status=DUPLICATE_IN_BATCH,
            ).count()
            registration_data_import.batch_possible_duplicates = Individual.objects.filter(
                registration_data_import_id=registration_data_import.id,
                deduplication_batch_status=SIMILAR_IN_BATCH,
            ).count()
            registration_data_import.batch_unique = Individual.objects.filter(
                registration_data_import_id=registration_data_import.id,
                deduplication_batch_status=UNIQUE_IN_BATCH,
            ).count()
            registration_data_import.golden_record_duplicates = Individual.objects.filter(
                registration_data_import_id=registration_data_import.id,
                deduplication_golden_record_status=DUPLICATE,
            ).count()
            registration_data_import.golden_record_possible_duplicates = Individual.objects.filter(
                registration_data_import_id=registration_data_import.id,
                deduplication_golden_record_status=NEEDS_ADJUDICATION,
            ).count()
            registration_data_import.golden_record_unique = Individual.objects.filter(
                registration_data_import_id=registration_data_import.id,
                deduplication_golden_record_status=UNIQUE,
            ).count()

            rdi_to_update.append(registration_data_import)

        RegistrationDataImport.objects.bulk_update(
            rdi_to_update,
            [
                "batch_duplicates",
                "batch_possible_duplicates",
                "batch_unique",
                "golden_record_duplicates",
                "golden_record_possible_duplicates",
                "golden_record_unique",
            ],
        )
    except Exception as e:
        logger.error(e)
        raise

    logger.info("Updating RDI deduplication stats finished")
