from collections import Counter
import logging
from typing import cast

from django.db import transaction

from hope.apps.registration_data.api.deduplication_engine import DeduplicationEngineAPI, SimilarityPair
from hope.apps.registration_data.services.biometric_deduplication import BiometricDeduplicationService
from hope.models import (
    DeduplicationEngineSimilarityPair,
    Program,
    RegistrationDataImport,
)

logger = logging.getLogger(__name__)


PERSISTED_FINDINGS_STATUS_CODES = (
    DeduplicationEngineSimilarityPair.StatusCode.STATUS_200.value,
    DeduplicationEngineSimilarityPair.StatusCode.STATUS_412.value,
    DeduplicationEngineSimilarityPair.StatusCode.STATUS_429.value,
    DeduplicationEngineSimilarityPair.StatusCode.STATUS_416.value,
    DeduplicationEngineSimilarityPair.StatusCode.STATUS_418.value,
)


class CwArrivalHookTask:
    def execute(self, registration_data_import_id: str) -> None:
        rdi = RegistrationDataImport.objects.select_related("program").get(pk=registration_data_import_id)
        logger.info(
            f"RDI:{registration_data_import_id} CW arrival hook starting "
            f"(country_workspace_id={rdi.country_workspace_id}, status={rdi.status})"
        )

        if rdi.status in (
            RegistrationDataImport.MERGING,
            RegistrationDataImport.MERGED,
        ):
            logger.info(f"RDI:{registration_data_import_id} arrival hook no-op (status={rdi.status})")
            return

        if rdi.status == RegistrationDataImport.IMPORT_ERROR and rdi.is_coming_from_cw:
            self._reset_rdi_state_for_cw_retry(rdi)
            logger.info(f"RDI:{registration_data_import_id} self-healed IMPORT_ERROR → MERGE_SCHEDULED")

        findings = DeduplicationEngineAPI().get_group_findings(cast("str", rdi.country_workspace_id))
        status_counts = dict(Counter(str(f["status_code"]) for f in findings))
        logger.info(f"RDI:{registration_data_import_id} fetched findings (status_codes={status_counts})")

        similarity_pairs = self._parse_findings_to_similarity_pairs(findings)
        DeduplicationEngineSimilarityPair.bulk_add_pairs(
            cast("Program", rdi.program), similarity_pairs, id_name="country_workspace_id"
        )
        logger.info(f"RDI:{registration_data_import_id} parsed {len(similarity_pairs)} similarity pairs from findings")

        BiometricDeduplicationService().store_rdi_deduplication_statistics(rdi)
        logger.info(f"RDI:{registration_data_import_id} stored deduplication statistics")

        self._schedule_merge(registration_data_import_id)

    def _parse_findings_to_similarity_pairs(self, findings: list[dict]) -> list[SimilarityPair]:
        similarity_pairs: list[SimilarityPair] = []
        for finding in findings:
            status_code = str(finding["status_code"])
            if status_code not in PERSISTED_FINDINGS_STATUS_CODES:
                logger.debug(f"Dedup Engine Findings, skipping non-persisted status_code={status_code}")
                continue
            first = finding["first"].get("reference_pk") or None
            second = finding["second"].get("reference_pk") or None
            if not (first or second):
                logger.warning("Dedup Engine Findings, finding with both reference_pks empty")
                continue
            similarity_pairs.append(
                SimilarityPair(
                    score=finding["score"],
                    status_code=status_code,
                    first=str(first) if first else None,
                    second=str(second) if second else None,
                )
            )
        return similarity_pairs

    def _reset_rdi_state_for_cw_retry(self, rdi: RegistrationDataImport) -> None:
        rdi.status = RegistrationDataImport.MERGE_SCHEDULED
        rdi.error_message = ""
        rdi.sentry_id = ""
        rdi.save(update_fields=["status", "error_message", "sentry_id"])

    def _schedule_merge(self, registration_data_import_id: str) -> None:
        from hope.apps.registration_data.celery_tasks import merge_registration_data_import_async_task

        with transaction.atomic():
            locked_rdi = RegistrationDataImport.objects.select_for_update().get(pk=registration_data_import_id)
            if locked_rdi.status != RegistrationDataImport.MERGE_SCHEDULED:
                logger.info(f"RDI:{registration_data_import_id} skipping merge enqueue (status={locked_rdi.status})")
                return
            locked_rdi.status = RegistrationDataImport.MERGING
            locked_rdi.save(update_fields=["status"])
            merge_registration_data_import_async_task(locked_rdi)
            logger.info(f"RDI:{registration_data_import_id} status → MERGING, merge task enqueued")
