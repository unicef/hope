import logging
from typing import Any

from django.db.models import Q, QuerySet

from hope.apps.household.const import (
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    UNIQUE,
    UNIQUE_IN_BATCH,
)
from hope.apps.registration_data.api.deduplication_engine import (
    BiographicHDEFinding,
    BiometricHDEFinding,
    DeduplicationEngineAPI,
)
from hope.models import (
    BiographicDedupeSimilarityPair,
    BiometricDedupeSimilarityPair,
    PendingIndividual,
    Program,
    RegistrationDataImport,
)
from hope.models.deduplication_engine_similarity_pair import IndividualIdField

logger = logging.getLogger(__name__)


PERSISTED_BIOMETRIC_FINDINGS_STATUS_CODES = (
    BiometricDedupeSimilarityPair.StatusCode.STATUS_200.value,
    BiometricDedupeSimilarityPair.StatusCode.STATUS_412.value,
    BiometricDedupeSimilarityPair.StatusCode.STATUS_429.value,
    BiometricDedupeSimilarityPair.StatusCode.STATUS_416.value,
    BiometricDedupeSimilarityPair.StatusCode.STATUS_418.value,
)


def _hde_finding_kwargs(finding: dict) -> dict[str, Any] | None:
    # Fields shared by biometric and biographic findings; None when the finding has no individual to store.
    first = finding["first"].get("reference_pk") or None
    second = finding["second"].get("reference_pk") or None
    if not (first or second):
        logger.warning("Dedup Engine Findings, finding with both reference_pks empty")
        return None
    return {
        "score": finding["score"],
        "first": str(first) if first else None,
        "second": str(second) if second else None,
    }


class BiometricDeduplicationEngineService:
    class DeduplicationEngineServiceError(Exception):
        pass

    def __init__(self) -> None:
        self.api = DeduplicationEngineAPI()

    def parse_findings(self, findings: list[dict]) -> list[BiometricHDEFinding]:
        hde_findings = []
        for finding in findings:
            status_code = str(finding["status_code"])
            if status_code not in PERSISTED_BIOMETRIC_FINDINGS_STATUS_CODES:
                logger.debug(f"Dedup Engine Findings, skipping non-persisted status_code={status_code}")
                continue
            if (kwargs := _hde_finding_kwargs(finding)) is not None:
                hde_findings.append(BiometricHDEFinding(**kwargs, status_code=status_code))
        return hde_findings

    def store_biometric_similarity_pairs(
        self,
        program: Program,
        hde_findings: list[BiometricHDEFinding],
        id_field_name: IndividualIdField = "id",
    ) -> None:
        BiometricDedupeSimilarityPair.bulk_add_pairs(program, hde_findings, id_field_name=id_field_name)

    def store_rdi_deduplication_statistics(self, rdi: RegistrationDataImport) -> None:
        rdi_individuals = PendingIndividual.objects.filter(registration_data_import=rdi)
        rdi_individuals_ids = rdi_individuals.values_list("id", flat=True)

        batch_duplicates = self.get_duplicates_for_rdi_against_batch(rdi)
        batch_unique_individuals = set()
        for pair in batch_duplicates:
            batch_unique_individuals.add(pair.individual1_id)
            batch_unique_individuals.add(pair.individual2_id)
        rdi.dedup_engine_batch_duplicates = len(batch_unique_individuals)

        population_duplicates = self.get_duplicates_for_rdi_against_population(rdi, rdi_merged=False)
        population_unique_individuals = set()
        for pair in population_duplicates:
            if pair.individual1_id in rdi_individuals_ids:
                population_unique_individuals.add(pair.individual1_id)
            if pair.individual2_id in rdi_individuals_ids:
                population_unique_individuals.add(pair.individual2_id)  # pragma: no cover
        rdi.dedup_engine_golden_record_duplicates = len(population_unique_individuals)

        rdi.save(update_fields=["dedup_engine_batch_duplicates", "dedup_engine_golden_record_duplicates"])

        for individual in rdi_individuals:
            population_ind_duplicates = population_duplicates.filter(
                Q(individual1=individual) | Q(individual2=individual)
            )
            golden_results = BiometricDedupeSimilarityPair.serialize_for_individual(
                individual,
                population_ind_duplicates,
            )
            individual.biometric_deduplication_golden_record_results = golden_results
            individual.biometric_deduplication_golden_record_status = (
                DUPLICATE if population_ind_duplicates.exists() else UNIQUE
            )

            batch_ind_duplicates = batch_duplicates.filter(
                Q(individual1=individual) | Q(individual2=individual),
            )
            batch_results = BiometricDedupeSimilarityPair.serialize_for_individual(
                individual,
                batch_ind_duplicates,
            )
            individual.biometric_deduplication_batch_results = batch_results
            individual.biometric_deduplication_batch_status = (
                DUPLICATE_IN_BATCH if batch_ind_duplicates.exists() else UNIQUE_IN_BATCH
            )

            individual.save(
                update_fields=[
                    "biometric_deduplication_golden_record_results",
                    "biometric_deduplication_golden_record_status",
                    "biometric_deduplication_batch_results",
                    "biometric_deduplication_batch_status",
                ]
            )

    def get_duplicates_for_rdi_against_batch(
        self, rdi: RegistrationDataImport
    ) -> QuerySet[BiometricDedupeSimilarityPair, BiometricDedupeSimilarityPair]:
        return BiometricDedupeSimilarityPair.objects.for_rdi_against_batch(rdi).filter(similarity_score__gt=0)

    def get_duplicates_for_rdi_against_population(
        self, rdi: RegistrationDataImport, rdi_merged: bool = False, exclude_not_valid: bool = True
    ) -> QuerySet[BiometricDedupeSimilarityPair, BiometricDedupeSimilarityPair]:
        pairs = BiometricDedupeSimilarityPair.objects.for_rdi_against_population(rdi, rdi_merged)
        if exclude_not_valid:
            pairs = pairs.exclude(similarity_score=0)
        return pairs

    def create_grievance_tickets_for_biometric_duplicates(self, rdi: RegistrationDataImport) -> None:
        # create tickets only against merged individuals
        from hope.apps.grievance.services.biometric_photo_ticket import (
            create_biometrics_photo_data_change_tickets,
        )
        from hope.apps.grievance.services.needs_adjudication_ticket_services import (
            create_needs_adjudication_tickets_for_biometrics,
        )

        deduplication_pairs = self.get_duplicates_for_rdi_against_population(
            rdi, rdi_merged=True, exclude_not_valid=False
        )

        photo_error_codes = BiometricDedupeSimilarityPair.StatusCode.photo_error_codes()
        create_needs_adjudication_tickets_for_biometrics(
            deduplication_pairs.exclude(status_code__in=photo_error_codes), rdi
        )
        create_biometrics_photo_data_change_tickets(deduplication_pairs.filter(status_code__in=photo_error_codes), rdi)

    def get_rdi_biometric_findings(self, rdi_country_workspace_id: str) -> list[dict]:
        return self.api.get_rdi_biometric_findings(rdi_country_workspace_id)


class BiographicDeduplicationEngineService:
    def __init__(self) -> None:
        self.api = DeduplicationEngineAPI()

    def parse_findings(self, findings: list[dict]) -> list[BiographicHDEFinding]:
        return [
            BiographicHDEFinding(**kwargs, proximity_to_score=finding["proximity_to_score"])
            for finding in findings
            if (kwargs := _hde_finding_kwargs(finding)) is not None
        ]

    def store_biographic_similarity_pairs(
        self,
        program: Program,
        hde_findings: list[BiographicHDEFinding],
    ) -> None:
        BiographicDedupeSimilarityPair.bulk_add_pairs(program, hde_findings, id_field_name="country_workspace_id")

    def get_rdi_biographic_findings(self, rdi_country_workspace_id: str) -> list[dict]:
        return self.api.get_rdi_biographic_findings(rdi_country_workspace_id)
