import logging

from django.db import transaction

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import \
    DeduplicateTask
from hct_mis_api.apps.registration_datahub.tasks.import_program_population import \
    import_program_population

logger = logging.getLogger(__name__)


class RdiProgramPopulationCreateTask:
    @transaction.atomic()
    def execute(
        self,
        registration_data_import_id: str,
        business_area_id: str,
        import_from_program_id: str,
        import_to_program_id: str,
    ) -> None:
        business_area = BusinessArea.objects.get(id=business_area_id)
        old_rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import_id)
        import_program_population(
            import_from_program_id,
            import_to_program_id,
            old_rdi_mis,
        )
        old_rdi_mis.bulk_update_household_size()

        if not business_area.postpone_deduplication:
            logger.info("Starting deduplication of %s", registration_data_import_id)
            registration_data_import = RegistrationDataImport.objects.get(id=registration_data_import_id)
            registration_data_import.status = RegistrationDataImport.DEDUPLICATION
            registration_data_import.save()
            DeduplicateTask(business_area.slug, str(import_to_program_id)).deduplicate_pending_individuals(
                registration_data_import=registration_data_import
            )
            logger.info("Finished deduplication of %s", registration_data_import_id)
        else:
            registration_data_import = RegistrationDataImport.objects.get(id=registration_data_import_id)
            registration_data_import.status = RegistrationDataImport.IN_REVIEW
            registration_data_import.save()
            log_create(
                RegistrationDataImport.ACTIVITY_LOG_MAPPING,
                "business_area",
                None,
                registration_data_import.program_id,
                old_rdi_mis,
                registration_data_import,
            )
