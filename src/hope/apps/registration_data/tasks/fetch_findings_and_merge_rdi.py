import logging
from typing import cast

from django.db import transaction

from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.apps.registration_data.services.biometric_deduplication import BiometricDeduplicationService
from hope.apps.registration_data.tasks.rdi_merge import RdiMergeTask
from hope.apps.utils.elasticsearch_utils import remove_elasticsearch_documents_by_matching_ids
from hope.models import (
    PendingHousehold,
    PendingIndividual,
    Program,
    RegistrationDataImport,
)

logger = logging.getLogger(__name__)


class FetchFindingsAndMergeRdi:
    _PROCESSABLE_STATUSES = [
        RegistrationDataImport.MERGE_SCHEDULED,
        RegistrationDataImport.MERGE_ERROR,
        RegistrationDataImport.IMPORT_ERROR,
    ]

    def execute(self, registration_data_import_id: str) -> bool:
        rdi = self._load_and_guard_rdi(registration_data_import_id)
        if rdi is None:
            return False

        dedupe_service, findings = self._fetch_biometric_findings(rdi)

        try:
            with transaction.atomic():
                locked_rdi = self._lock_rdi(registration_data_import_id)
                if locked_rdi is None:
                    return False
                self._transition_to_merging(locked_rdi)
                self._store_deduplication_results(locked_rdi, dedupe_service, findings)
                RdiMergeTask().execute(str(locked_rdi.id))
        except Exception:
            self._remove_es_docs(rdi)
            raise
        return True

    def _load_and_guard_rdi(self, registration_data_import_id: str | None) -> RegistrationDataImport | None:
        rdi = (
            RegistrationDataImport.objects.select_related("program")
            .filter(pk=registration_data_import_id, status__in=self._PROCESSABLE_STATUSES)
            .first()
        )
        if rdi is None:
            return None
        if rdi.country_workspace_id is None:
            logger.warning(
                f"RDI {registration_data_import_id} does not have country_workspace_id and can't be processed."
            )
            return None
        return rdi

    def _fetch_biometric_findings(
        self, rdi: RegistrationDataImport
    ) -> tuple[BiometricDeduplicationService | None, list[dict] | None]:
        dedupe_service: BiometricDeduplicationService | None = None
        findings: list[dict] | None = None
        if rdi.program.biometric_deduplication_enabled:
            dedupe_service = BiometricDeduplicationService()
            findings = dedupe_service.get_rdi_findings(cast("str", rdi.country_workspace_id))
        return dedupe_service, findings

    def _lock_rdi(self, registration_data_import_id: str) -> RegistrationDataImport | None:
        # Picked up by another worker between the pre-lock read and this lock.
        return (
            RegistrationDataImport.objects.select_for_update(skip_locked=True, of=("self",))
            .select_related("program")
            .filter(pk=registration_data_import_id, status__in=self._PROCESSABLE_STATUSES)
            .first()
        )

    def _transition_to_merging(self, rdi: RegistrationDataImport) -> None:
        registration_data_import_id = str(rdi.id)
        if rdi.status in (RegistrationDataImport.IMPORT_ERROR, RegistrationDataImport.MERGE_ERROR):
            self._reset_rdi_state_for_cw_retry(rdi)
        rdi.status = RegistrationDataImport.MERGING
        rdi.save(update_fields=["status"])
        logger.info(
            f"Country Workspace RDI:{registration_data_import_id} merging started "
            f"(country_workspace_id={rdi.country_workspace_id})"
        )

    def _store_deduplication_results(
        self,
        rdi: RegistrationDataImport,
        dedupe_service: BiometricDeduplicationService | None,
        findings: list[dict] | None,
    ) -> None:
        if dedupe_service is not None and findings is not None:
            registration_data_import_id = str(rdi.id)
            similarity_pairs = dedupe_service.parse_findings(findings)
            dedupe_service.store_similarity_pairs(
                cast("Program", rdi.program), similarity_pairs, id_field_name="country_workspace_id"
            )
            logger.info(
                f"RDI:{registration_data_import_id} parsed {len(similarity_pairs)} similarity pairs from findings"
            )
            dedupe_service.store_rdi_deduplication_statistics(rdi)
            logger.info(f"RDI:{registration_data_import_id} stored deduplication statistics")

    def _reset_rdi_state_for_cw_retry(self, rdi: RegistrationDataImport) -> None:
        rdi.error_message = ""
        rdi.sentry_id = ""
        rdi.save(update_fields=["error_message", "sentry_id"])

    def _remove_es_docs(self, rdi: RegistrationDataImport) -> None:
        program_id = str(rdi.program_id)
        individual_ids = list(
            PendingIndividual.objects.filter(registration_data_import=rdi).values_list("id", flat=True)
        )
        household_ids = list(PendingHousehold.objects.filter(registration_data_import=rdi).values_list("id", flat=True))
        remove_elasticsearch_documents_by_matching_ids(individual_ids, get_individual_doc(program_id))
        remove_elasticsearch_documents_by_matching_ids(household_ids, get_household_doc(program_id))
