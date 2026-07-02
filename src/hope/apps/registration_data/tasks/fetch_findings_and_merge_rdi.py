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

    def execute(self, registration_data_import_id: str) -> None:
        # Lightweight read (no lock) — just enough to know whether biometric dedup is on and
        # to get the country_workspace_id, so findings can be fetched before the transaction.
        rdi = (
            RegistrationDataImport.objects.select_related("program")
            .filter(pk=registration_data_import_id, status__in=self._PROCESSABLE_STATUSES)
            .first()
        )
        if rdi is None:
            return
        if rdi.country_workspace_id is None:
            logger.warning(
                f"RDI {registration_data_import_id} does not have country_workspace_id and can't be processed."
            )
            return

        # Fetch findings from the Deduplication Engine *before* the transaction: it is a slow
        # external call with no DB side effect, and a failure here must not hold a transaction
        # open (nor is there any ES doc to clean up yet).
        dedupe_service: BiometricDeduplicationService | None = None
        findings: list[dict] | None = None
        if rdi.program.biometric_deduplication_enabled:
            dedupe_service = BiometricDeduplicationService()
            findings = dedupe_service.get_rdi_findings(rdi.country_workspace_id)

        # All DB side effects — the MERGE_SCHEDULED→MERGING transition, storing findings, and
        # the synchronous merge — run in one transaction. Elasticsearch is not covered by it,
        # so on any failure the DB rolls back automatically and we remove the ES docs by hand
        # before re-raising; the caller (fetch_findings_and_merge_rdi_action) parks the RDI in
        # MERGE_ERROR.
        try:
            with transaction.atomic():
                rdi = (
                    RegistrationDataImport.objects.select_for_update(skip_locked=True, of=("self",))
                    .select_related("program")
                    .filter(pk=registration_data_import_id, status__in=self._PROCESSABLE_STATUSES)
                    .first()
                )
                if rdi is None:
                    # Picked up by another worker between the read above and this lock.
                    return

                if rdi.status in (RegistrationDataImport.IMPORT_ERROR, RegistrationDataImport.MERGE_ERROR):
                    self._reset_rdi_state_for_cw_retry(rdi)
                rdi.status = RegistrationDataImport.MERGING
                rdi.save(update_fields=["status"])
                logger.info(
                    f"RDI:{registration_data_import_id} CW arrival hook starting "
                    f"(country_workspace_id={rdi.country_workspace_id})"
                )

                if dedupe_service is not None and findings is not None:
                    similarity_pairs = dedupe_service.parse_findings(findings)
                    dedupe_service.store_similarity_pairs(
                        cast("Program", rdi.program), similarity_pairs, id_field_name="country_workspace_id"
                    )
                    logger.info(
                        f"RDI:{registration_data_import_id} parsed {len(similarity_pairs)} similarity"
                        " pairs from findings"
                    )
                    dedupe_service.store_rdi_deduplication_statistics(rdi)
                    logger.info(f"RDI:{registration_data_import_id} stored deduplication statistics")

                RdiMergeTask().execute(str(rdi.id))
        except Exception:
            self._remove_es_docs(rdi)
            raise

    def _reset_rdi_state_for_cw_retry(self, rdi: RegistrationDataImport) -> None:
        rdi.error_message = ""
        rdi.sentry_id = ""
        rdi.save(update_fields=["error_message", "sentry_id"])

    def _remove_es_docs(self, rdi: RegistrationDataImport) -> None:
        # The DB transaction rolls back on its own; Elasticsearch does not. Remove any
        # documents the (now rolled-back) merge may have indexed for this RDI's individuals
        # and households — they are back to Pending after the rollback, so query by RDI.
        program_id = str(rdi.program_id)
        individual_ids = list(
            PendingIndividual.objects.filter(registration_data_import=rdi).values_list("id", flat=True)
        )
        household_ids = list(PendingHousehold.objects.filter(registration_data_import=rdi).values_list("id", flat=True))
        remove_elasticsearch_documents_by_matching_ids(individual_ids, get_individual_doc(program_id))
        remove_elasticsearch_documents_by_matching_ids(household_ids, get_household_doc(program_id))
