import logging

from django.db.models import Q, QuerySet

from hope.apps.household.const import (
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    UNIQUE,
    UNIQUE_IN_BATCH,
)
from hope.apps.registration_data.api.deduplication_engine import (
    BiometricDeduplicationEngineAPI,
    SimilarityPair,
)
from hope.models import (
    BiometricDedupeSimilarityPair,
    Individual,
    PendingIndividual,
    Program,
    RegistrationDataImport,
)
from hope.models.deduplication_engine_similarity_pair import IndividualIdField
from hope.models.utils import MergeStatusModel

logger = logging.getLogger(__name__)


PERSISTED_FINDINGS_STATUS_CODES = (
    BiometricDedupeSimilarityPair.StatusCode.STATUS_200.value,
    BiometricDedupeSimilarityPair.StatusCode.STATUS_412.value,
    BiometricDedupeSimilarityPair.StatusCode.STATUS_429.value,
    BiometricDedupeSimilarityPair.StatusCode.STATUS_416.value,
    BiometricDedupeSimilarityPair.StatusCode.STATUS_418.value,
)


class BiometricDeduplicationService:
    class BiometricDeduplicationServiceError(Exception):
        pass

    def __init__(self) -> None:
        self.api = BiometricDeduplicationEngineAPI()

    def parse_findings(self, findings: list[dict]) -> list[SimilarityPair]:
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

    def store_similarity_pairs(
        self,
        program: Program,
        similarity_pairs: list[SimilarityPair],
        id_field_name: IndividualIdField = "id",
    ) -> None:
        BiometricDedupeSimilarityPair.bulk_add_pairs(program, similarity_pairs, id_field_name=id_field_name)

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
        rdi_individuals = PendingIndividual.objects.filter(registration_data_import=rdi).only("id")
        return BiometricDedupeSimilarityPair.objects.filter(
            Q(individual1__in=rdi_individuals) & Q(individual2__in=rdi_individuals),
            program=rdi.program,
            similarity_score__gt=0,
        ).distinct()

    def get_duplicates_for_rdi_against_population(
        self, rdi: RegistrationDataImport, rdi_merged: bool = False, exclude_not_valid: bool = True
    ) -> QuerySet[BiometricDedupeSimilarityPair, BiometricDedupeSimilarityPair]:
        if rdi_merged:
            rdi_individuals = Individual.objects.filter(registration_data_import=rdi).only("id")
            other_pending_rdis_individuals = PendingIndividual.objects.filter(program=rdi.program)
        else:
            rdi_individuals = PendingIndividual.objects.filter(registration_data_import=rdi).only("id")
            other_pending_rdis_individuals = PendingIndividual.objects.filter(program=rdi.program).exclude(
                id__in=rdi_individuals
            )

        qs = BiometricDedupeSimilarityPair.objects.filter(
            Q(individual1__in=rdi_individuals) | Q(individual2__in=rdi_individuals),
            (Q(individual1__duplicate=False) | Q(individual1__isnull=True))
            & (Q(individual2__duplicate=False) | Q(individual2__isnull=True)),
            (Q(individual1__withdrawn=False) | Q(individual1__isnull=True))
            & (Q(individual2__withdrawn=False) | Q(individual2__isnull=True)),
            (
                Q(individual1__rdi_merge_status=MergeStatusModel.MERGED)
                | Q(individual1__isnull=True)
                | Q(individual2__rdi_merge_status=MergeStatusModel.MERGED)
                | Q(individual2__isnull=True)
            ),
            program=rdi.program,
        ).exclude(Q(individual1__in=other_pending_rdis_individuals) | Q(individual2__in=other_pending_rdis_individuals))

        if exclude_not_valid:
            qs.exclude(similarity_score=0)

        return qs.distinct()

    def create_grievance_tickets_for_duplicates(self, rdi: RegistrationDataImport) -> None:
        # create tickets only against merged individuals
        from hope.apps.grievance.services.needs_adjudication_ticket_services import (
            create_needs_adjudication_tickets_for_biometrics,
        )

        deduplication_pairs = self.get_duplicates_for_rdi_against_population(
            rdi, rdi_merged=True, exclude_not_valid=False
        )

        create_needs_adjudication_tickets_for_biometrics(deduplication_pairs, rdi)

    def get_rdi_findings(self, rdi_country_workspace_id: str) -> list[dict]:
        return self.api.get_rdi_findings(rdi_country_workspace_id)
