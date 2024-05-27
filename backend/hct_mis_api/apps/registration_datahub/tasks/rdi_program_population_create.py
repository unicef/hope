import logging

from django.db import transaction

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import RegistrationDataImportDatahub
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
from hct_mis_api.apps.registration_datahub.tasks.objects_to_imported_objects import CreateImportedObjectsFromObjectsTask


logger = logging.getLogger(__name__)


class RdiProgramPopulationCreateTask:
    @transaction.atomic(using="registration_datahub")
    def execute(
        self,
            registration_data_import_id: str,
            business_area_id: str,
            import_from_program_id: str,
            import_to_program_id: str,
    ) -> None:
        registration_data_import = RegistrationDataImportDatahub.objects.select_for_update().get(
            id=registration_data_import_id,
        )
        registration_data_import.import_done = RegistrationDataImportDatahub.STARTED
        registration_data_import.save()

        self.business_area = BusinessArea.objects.get(id=business_area_id)

        CreateImportedObjectsFromObjectsTask().execute(
            registration_data_import.hct_id,
            import_from_program_id,
        )
        registration_data_import.import_done = RegistrationDataImportDatahub.DONE
        registration_data_import.save()
        old_rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import.hct_id)
        if not self.business_area.postpone_deduplication:
            logger.info("Starting deduplication of %s", registration_data_import.id)
            rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import.hct_id)
            rdi_mis.status = RegistrationDataImport.DEDUPLICATION
            rdi_mis.save()
            DeduplicateTask(self.business_area.slug, str(import_to_program_id)).deduplicate_imported_individuals(
                registration_data_import_datahub=registration_data_import
            )
            logger.info("Finished deduplication of %s", registration_data_import.id)
        else:
            rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import.hct_id)
            rdi_mis.status = RegistrationDataImport.IN_REVIEW
            rdi_mis.save()
            log_create(
                RegistrationDataImport.ACTIVITY_LOG_MAPPING,
                "business_area",
                None,
                rdi_mis.program_id,
                old_rdi_mis,
                rdi_mis,
            )
