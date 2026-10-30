from collections import defaultdict
from collections.abc import Iterable
import logging
from typing import Any
from uuid import UUID

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
from hope.apps.registration_data.utils import post_process_dedupe_results
from hope.models import (
    BiographicDedupeSimilarityPair,
    BiometricDedupeSimilarityPair,
    Individual,
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

    def store_biographic_deduplication_statistics(self, rdi: RegistrationDataImport) -> None:
        # Setup
        rdi_individuals = PendingIndividual.objects.filter(registration_data_import=rdi)
        rdi_individuals_ids = set(rdi_individuals.values_list("id", flat=True))

        population_pairs = BiographicDedupeSimilarityPair.objects.for_rdi_against_population(rdi).select_related(
            "individual1__household__admin2", "individual2__household__admin2"
        )
        batch_pairs = BiographicDedupeSimilarityPair.objects.for_rdi_against_batch(rdi).select_related(
            "individual1__household__admin2", "individual2__household__admin2"
        )

        population_pairs_by_individual = defaultdict(list)
        for pair in population_pairs:
            rdi_side_id = pair.individual1_id if pair.individual1_id in rdi_individuals_ids else pair.individual2_id
            population_pairs_by_individual[rdi_side_id].append(pair)

        batch_pairs_by_individual = defaultdict(list)
        for pair in batch_pairs:
            batch_pairs_by_individual[pair.individual1_id].append(pair)
            batch_pairs_by_individual[pair.individual2_id].append(pair)

        # Let's mark individuals in population, outside incoming RDI
        # as duplicates. We'll use this information later on when
        # counting other statistics.
        #
        # in legacy flow it's being done here: deduplicate.py:143-145
        self.mark_population_individuals_as_duplicates(
            self._get_population_matches_outside_rdi_ids(population_pairs, rdi_individuals_ids)
        )

        individuals_to_bulk_update = []
        for individual in rdi_individuals:
            # Looking at legacy biographic deduplication we're interested ONLY in
            # deduplication_golden_record_status
            #   DUPLICATE           - individual has duplicates within population
            #   NEEDS_ADJUDICATION  - Possible duplicate - we drop this in cw flow
            #   UNIQUE              - no duplicates found
            #
            # deduplication_golden_record_results
            #   JSON Field containing information about duplicates found in population.
            #   Data points reported here are described in
            #   BiographicDedupeSimilarityPair.serialize_for_individual
            #
            # deduplication_batch_status
            #   See DEDUPLICATION_BATCH_STATUS_CHOICE.
            #   (NOT_PROCESSED, "Not Processed")        - All records are processed instant in CW flow
            #   (SIMILAR_IN_BATCH, "Similar in RDI"),   - ? Not sure, I think we need only DUPLICATE and UNIQUE
            #
            # deduplication_batch_results
            #   Same case as with deduplication_golden_record_results
            #
            self._set_golden_record_results(individual, population_pairs_by_individual[individual.id])
            self._set_batch_results(individual, batch_pairs_by_individual[individual.id])
            post_process_dedupe_results(individual)  # this part needs to be checked if it should stay
            individuals_to_bulk_update.append(individual)

        PendingIndividual.objects.bulk_update(
            individuals_to_bulk_update,
            (
                "deduplication_golden_record_results",
                "deduplication_golden_record_status",
                "deduplication_batch_results",
                "deduplication_batch_status",
            ),
            batch_size=1000,
        )

        rdi.golden_record_duplicates = self.count_individuals(rdi, "deduplication_golden_record_status", DUPLICATE)
        rdi.golden_record_unique = self.count_individuals(rdi, "deduplication_golden_record_status", UNIQUE)
        rdi.batch_duplicates = self.count_individuals(rdi, "deduplication_batch_status", DUPLICATE_IN_BATCH)
        rdi.batch_unique = self.count_individuals(rdi, "deduplication_batch_status", UNIQUE_IN_BATCH)
        rdi.save(update_fields=["golden_record_duplicates", "golden_record_unique", "batch_duplicates", "batch_unique"])

    def _get_population_matches_outside_rdi_ids(
        self, similarity_pairs: Iterable[BiographicDedupeSimilarityPair], rdi_individuals_ids: set[UUID]
    ) -> set[UUID]:
        population_individual_ids: set[UUID] = set()
        for pair in similarity_pairs:
            for individual_id in (pair.individual1_id, pair.individual2_id):
                if individual_id and individual_id not in rdi_individuals_ids:
                    population_individual_ids.add(individual_id)
        return population_individual_ids

    def _set_golden_record_results(
        self, individual: PendingIndividual, population_pairs: list[BiographicDedupeSimilarityPair]
    ) -> None:
        golden_results = BiographicDedupeSimilarityPair.serialize_for_individual(individual, population_pairs)
        individual.deduplication_golden_record_results = golden_results
        individual.deduplication_golden_record_status = DUPLICATE if golden_results["duplicates"] else UNIQUE

    def _set_batch_results(
        self, individual: PendingIndividual, batch_pairs: list[BiographicDedupeSimilarityPair]
    ) -> None:
        batch_results = BiographicDedupeSimilarityPair.serialize_for_individual(individual, batch_pairs)
        individual.deduplication_batch_results = batch_results
        individual.deduplication_batch_status = DUPLICATE_IN_BATCH if batch_results["duplicates"] else UNIQUE_IN_BATCH

    def mark_population_individuals_as_duplicates(self, ids: set[UUID]) -> None:
        Individual.objects.filter(id__in=ids).update(deduplication_golden_record_status=DUPLICATE)

    def count_individuals(self, rdi: RegistrationDataImport, status_field: str, status: str) -> int:
        return PendingIndividual.objects.filter(registration_data_import=rdi, **{status_field: status}).count()

    def create_grievance_tickets_for_biographic_duplicates(self, rdi: RegistrationDataImport) -> None:
        from hope.apps.grievance.services.needs_adjudication_ticket_services import (
            create_needs_adjudication_tickets_for_biographic,
        )

        # After merge this covers RDI-vs-population and intra-batch pairs. No score-0 filter: it's biometric-only.
        deduplication_pairs = BiographicDedupeSimilarityPair.objects.for_rdi_against_population(
            rdi, rdi_merged=True
        ).select_related("individual1__household__admin2", "individual2__household__admin2")
        create_needs_adjudication_tickets_for_biographic(deduplication_pairs, rdi)
