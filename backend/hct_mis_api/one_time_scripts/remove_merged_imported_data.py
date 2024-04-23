import logging

from hct_mis_api.apps.registration_data.models import (
    ImportedHousehold,
    RegistrationDataImport,
)

logger = logging.getLogger(__name__)


def remove_merged_imported_households(page_count: int = 500) -> None:
    try:
        merged_rdis = (
            RegistrationDataImport.objects.filter(status=RegistrationDataImport.MERGED)
            .values_list("datahub_id", flat=True)
            .order_by("created_at")
        )

        i, count = 0, merged_rdis.count() // page_count
        while i <= count:
            logger.info(f"Page {i}/{count} processing...")
            rdi_datahub_ids_page = list(merged_rdis[i * page_count : (i + 1) * page_count])
            ImportedHousehold.objects.filter(registration_data_import_id__in=rdi_datahub_ids_page).delete()
            i += 1

    except Exception:
        logger.error("Removing merged imported household and related data failed")
        raise
