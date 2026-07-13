import logging
from typing import cast

from django.db import transaction

from hope.apps.registration_data.services.biometric_deduplication import BiometricDeduplicationService
from hope.models import (
    Program,
    RegistrationDataImport,
)

logger = logging.getLogger(__name__)


class ProcessCountryWorkspaceRdiTask:
    @transaction.atomic
    def execute(self, registration_data_import_id: str) -> None:
        rdi = (
            RegistrationDataImport.objects.select_for_update(skip_locked=True, of=("self",))
            .select_related("program")
            .filter(
                pk=registration_data_import_id,
                status__in=[
                    RegistrationDataImport.MERGE_SCHEDULED,
                    RegistrationDataImport.MERGE_ERROR,
                    RegistrationDataImport.IMPORT_ERROR,
                ],
            )
            .first()
        )
        if rdi is None:
            return

        if rdi.country_workspace_id is None:
            logger.warning(
                f"RDI {registration_data_import_id} does not have country_workspace_id and can't be processed."
            )
            return

        if rdi.status in (RegistrationDataImport.IMPORT_ERROR, RegistrationDataImport.MERGE_ERROR):
            self._reset_rdi_state_for_cw_retry(rdi)

        rdi.status = RegistrationDataImport.MERGING
        rdi.save(update_fields=["status"])

        logger.info(
            f"RDI:{registration_data_import_id} CW arrival hook starting "
            f"(country_workspace_id={rdi.country_workspace_id}, status={rdi.status})"
        )

        dedupe_service: BiometricDeduplicationService | None = None
        findings: list[dict] | None = None
        if rdi.program.biometric_deduplication_enabled:
            dedupe_service = BiometricDeduplicationService()
            findings = dedupe_service.get_rdi_findings(rdi.country_workspace_id)

            if findings is not None:
                similarity_pairs = dedupe_service.parse_findings(findings)
                dedupe_service.store_similarity_pairs(
                    cast("Program", rdi.program), similarity_pairs, id_field_name="country_workspace_id"
                )
                logger.info(
                    f"RDI:{registration_data_import_id} parsed {len(similarity_pairs)} similarity pairs from findings"
                )
                dedupe_service.store_rdi_deduplication_statistics(rdi)
                logger.info(f"RDI:{registration_data_import_id} stored deduplication statistics")

        transaction.on_commit(lambda: self._schedule_merge(rdi))

    def _reset_rdi_state_for_cw_retry(self, rdi: RegistrationDataImport) -> None:
        rdi.error_message = ""
        rdi.sentry_id = ""
        rdi.save(update_fields=["error_message", "sentry_id"])

    def _schedule_merge(self, rdi: RegistrationDataImport) -> None:
        from hope.apps.registration_data.celery_tasks import merge_registration_data_import_async_task

        merge_registration_data_import_async_task(rdi)
        logger.info(f"RDI:{rdi.id} status → MERGING, merge task enqueued")
