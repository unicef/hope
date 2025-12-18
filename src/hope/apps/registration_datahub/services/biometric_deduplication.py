import logging

from django.conf import settings
from django.db import transaction
from django.db.models import Q, QuerySet
from django.urls import reverse
from flags.state import flag_state

from hope.apps.household.const import (
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    UNIQUE,
    UNIQUE_IN_BATCH,
)
from hope.apps.registration_datahub.apis.deduplication_engine import (
    DeduplicationEngineAPI,
    DeduplicationImage,
    DeduplicationSet,
    DeduplicationSetData,
    IgnoredFilenamesPair,
    SimilarityPair,
)
from hope.models import (
    DeduplicationEngineSimilarityPair,
    Individual,
    PendingIndividual,
    Program,
    RegistrationDataImport,
)
from hope.models.utils import MergeStatusModel

logger = logging.getLogger(__name__)


class BiometricDeduplicationService:
    GET_DUPLICATES_BATCH_SIZE = 100
    DEDUP_STATE_READY = "Ready"
    DEDUP_STATE_FAILED = "Failed"
    INDIVIDUALS_REFUSED = "rejected"
    INDIVIDUALS_MERGED = "merged"

    class BiometricDeduplicationServiceError(Exception):
        pass

    def __init__(self) -> None:
        self.api = DeduplicationEngineAPI()

    def create_deduplication_set(self, program: Program) -> None:
        notification_url = reverse(
            "api:registration-data:registration-data-imports-webhook-deduplication",
            args=[program.business_area.slug, program.slug],
        )
        deduplication_set = DeduplicationSet(
            reference_pk=str(program.slug),
            notification_url=f"https://{settings.DOMAIN_NAME}{notification_url}",
        )
        self.api.create_deduplication_set(deduplication_set)

    def get_deduplication_set_results(self, program_slug: str, individual_ids: list[str]) -> list[dict]:
        results: list[dict] = []
        for i in range(0, len(individual_ids), self.GET_DUPLICATES_BATCH_SIZE):
            batch = individual_ids[i : i + self.GET_DUPLICATES_BATCH_SIZE]
            results.extend(self.api.get_duplicates(program_slug, batch))
        return results

    def get_deduplication_set(self, program_slug: str) -> DeduplicationSetData:
        response_data = self.api.get_deduplication_set(program_slug)
        return DeduplicationSetData(state=response_data["state"], error=response_data.get("error", ""))

    def upload_individuals(self, program_slug: str, rdi: RegistrationDataImport) -> None:
        individuals = (
            Individual.all_objects.filter(is_removed=False, registration_data_import=rdi)
            .exclude(Q(photo="") | Q(withdrawn=True) | Q(duplicate=True))
            .only("id", "photo")
        )

        if not individuals.exists():
            rdi.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_FINISHED
            rdi.save(update_fields=["deduplication_engine_status"])
            return

        images = [
            DeduplicationImage(reference_pk=str(individual.id), filename=individual.photo.name)
            for individual in individuals
        ]

        if rdi.deduplication_engine_status in [
            RegistrationDataImport.DEDUP_ENGINE_UPLOAD_ERROR,
            RegistrationDataImport.DEDUP_ENGINE_PENDING,
        ]:
            try:
                self.api.bulk_upload_images(program_slug, images)

            except self.api.API_EXCEPTION_CLASS:
                logging.exception(f"Failed to upload images for RDI {rdi}")
                rdi.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_UPLOAD_ERROR
                rdi.save(update_fields=["deduplication_engine_status"])
                return

        rdi.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_UPLOADED
        rdi.save(update_fields=["deduplication_engine_status"])

    def process_deduplication_set(self, program_slug: str, rdis: QuerySet[RegistrationDataImport]) -> None:
        try:
            response_data, status = self.api.process_deduplication(program_slug)
            if status in [409, 200]:  # 409 - deduplication already in progress
                rdis.update(deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS)
            else:
                logging.error(
                    f"Failed to process deduplication set {program_slug}. Response[{status}]: {response_data}"
                )
                rdis.update(deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_ERROR)
        except DeduplicationEngineAPI.DeduplicationEngineAPIError:
            logging.exception(f"Failed to process deduplication set {program_slug}")
            rdis.update(deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_ERROR)

    def upload_and_process_deduplication_set(self, program: Program) -> None:
        pending_rdis = RegistrationDataImport.objects.filter(
            program=program,
            deduplication_engine_status__in=[
                RegistrationDataImport.DEDUP_ENGINE_PENDING,
                RegistrationDataImport.DEDUP_ENGINE_UPLOAD_ERROR,
                RegistrationDataImport.DEDUP_ENGINE_ERROR,
            ],
            status=RegistrationDataImport.IN_REVIEW,
        )

        if not pending_rdis:
            return

        for rdi in pending_rdis:
            self.upload_individuals(program.slug, rdi)

        uploaded_rdis = RegistrationDataImport.objects.filter(
            program=program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_UPLOADED,
            status=RegistrationDataImport.IN_REVIEW,
        )
        self.process_deduplication_set(program.slug, uploaded_rdis)

    def delete_deduplication_set(self, program: Program) -> None:
        self.api.delete_deduplication_set(program.slug)
        DeduplicationEngineSimilarityPair.objects.filter(program=program).delete()

        RegistrationDataImport.objects.filter(program=program).exclude(
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED
        ).update(deduplication_engine_status=None)

    def store_similarity_pairs(self, program: Program, similarity_pairs: list[SimilarityPair]) -> None:
        DeduplicationEngineSimilarityPair.bulk_add_pairs(program, similarity_pairs)

    @staticmethod
    def mark_rdis_as_pending(program: Program) -> None:
        RegistrationDataImport.objects.filter(program=program, deduplication_engine_status__isnull=True).update(
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING
        )

    @staticmethod
    def mark_rdis_as_deduplicated(program: Program) -> None:
        RegistrationDataImport.objects.filter(
            program=program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS
        ).update(deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED)

    @staticmethod
    def mark_rdis_as_error(program: Program) -> None:
        RegistrationDataImport.objects.filter(
            program=program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS
        ).update(deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_ERROR)

    def store_rdis_deduplication_statistics(self, program: Program) -> None:
        rdis = RegistrationDataImport.objects.filter(
            status=RegistrationDataImport.IN_REVIEW,
            program=program,
        )
        for rdi in rdis:
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
                    Q(individual1=individual) | Q(individual2=individual),
                )
                individual.biometric_deduplication_golden_record_results = (
                    DeduplicationEngineSimilarityPair.serialize_for_individual(
                        individual,
                        population_ind_duplicates,
                    )
                )
                individual.biometric_deduplication_golden_record_status = (
                    DUPLICATE if population_ind_duplicates.exists() else UNIQUE
                )

                batch_ind_duplicates = batch_duplicates.filter(
                    Q(individual1=individual) | Q(individual2=individual),
                )
                individual.biometric_deduplication_batch_results = (
                    DeduplicationEngineSimilarityPair.serialize_for_individual(
                        individual,
                        batch_ind_duplicates,
                    )
                )
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

    def update_rdis_deduplication_statistics(self, program: Program, exclude_rdi: RegistrationDataImport) -> None:
        rdis = RegistrationDataImport.objects.filter(
            status=RegistrationDataImport.IN_REVIEW,
            program=program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        ).exclude(id=exclude_rdi.id)
        for rdi in rdis:
            rdi_individuals = PendingIndividual.objects.filter(registration_data_import=rdi)
            rdi_individuals_ids = rdi_individuals.values_list("id", flat=True)
            population_duplicates = self.get_duplicates_for_rdi_against_population(rdi, rdi_merged=False)
            population_unique_individuals = set()
            for pair in population_duplicates:
                if pair.individual1_id in rdi_individuals_ids:
                    population_unique_individuals.add(pair.individual1_id)
                if pair.individual2_id in rdi_individuals_ids:
                    population_unique_individuals.add(pair.individual2_id)  # pragma: no cover

            rdi.dedup_engine_golden_record_duplicates = len(population_unique_individuals)
            rdi.save(update_fields=["dedup_engine_golden_record_duplicates"])

            for individual in rdi_individuals:
                population_ind_duplicates = population_duplicates.filter(
                    Q(individual1=individual) | Q(individual2=individual),
                )
                individual.biometric_deduplication_golden_record_results = (
                    DeduplicationEngineSimilarityPair.serialize_for_individual(
                        individual,
                        population_ind_duplicates,
                    )
                )
                individual.biometric_deduplication_golden_record_status = (
                    DUPLICATE if population_ind_duplicates.exists() else UNIQUE
                )

                individual.save(
                    update_fields=[
                        "biometric_deduplication_golden_record_results",
                        "biometric_deduplication_golden_record_status",
                    ]
                )

    def get_duplicates_for_rdi_against_batch(
        self, rdi: RegistrationDataImport
    ) -> QuerySet[DeduplicationEngineSimilarityPair]:
        rdi_individuals = PendingIndividual.objects.filter(registration_data_import=rdi).only("id")
        return DeduplicationEngineSimilarityPair.objects.filter(
            Q(individual1__in=rdi_individuals) & Q(individual2__in=rdi_individuals),
            program=rdi.program,
            similarity_score__gt=0,
        ).distinct()

    def get_duplicates_for_rdi_against_population(
        self, rdi: RegistrationDataImport, rdi_merged: bool = False, exclude_not_valid: bool = True
    ) -> QuerySet[DeduplicationEngineSimilarityPair]:
        if rdi_merged:
            rdi_individuals = Individual.objects.filter(registration_data_import=rdi).only("id")
            other_pending_rdis_individuals = PendingIndividual.objects.filter(program=rdi.program)
        else:
            rdi_individuals = PendingIndividual.objects.filter(registration_data_import=rdi).only("id")
            other_pending_rdis_individuals = PendingIndividual.objects.filter(program=rdi.program).exclude(
                id__in=rdi_individuals
            )

        qs = DeduplicationEngineSimilarityPair.objects.filter(
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

    def fetch_biometric_deduplication_results_and_process(self, program: Program) -> None:
        deduplication_set_data = self.get_deduplication_set(program.slug)

        if deduplication_set_data.state == self.DEDUP_STATE_READY:
            try:
                rdis = RegistrationDataImport.objects.filter(
                    status=RegistrationDataImport.IN_REVIEW,
                    program=program,
                    deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS,
                ).values_list("id", flat=True)
                individual_ids = [
                    str(pk)
                    for pk in PendingIndividual.objects.filter(registration_data_import__in=rdis).values_list(
                        "pk", flat=True
                    )
                ]
                data = self.get_deduplication_set_results(program.slug, individual_ids)
                similarity_pairs = [
                    SimilarityPair(
                        score=item["score"],
                        status_code=item["status_code"],
                        first=item["first"]["reference_pk"] or None,
                        second=item["second"]["reference_pk"] or None,
                    )
                    for item in data
                    if str(item["status_code"])
                    in [
                        DeduplicationEngineSimilarityPair.StatusCode.STATUS_200.value,
                        DeduplicationEngineSimilarityPair.StatusCode.STATUS_412.value,
                        DeduplicationEngineSimilarityPair.StatusCode.STATUS_429.value,
                    ]
                ]
                with transaction.atomic():
                    self.store_similarity_pairs(program, similarity_pairs)
                    self.store_rdis_deduplication_statistics(program)
                    self.mark_rdis_as_deduplicated(program)
            except Exception:
                logger.exception(f"Dedupe Engine processing results error for program {program}")
                self.mark_rdis_as_error(program)

        elif deduplication_set_data.state == self.DEDUP_STATE_FAILED:
            logger.error(f"Dedupe Engine error for program {program} \n {deduplication_set_data.error}")
            self.mark_rdis_as_error(program)

    def report_false_positive_duplicate(
        self, individual1_photo: str, individual2_photo: str, program_slug: str
    ) -> None:
        false_positive_pair = IgnoredFilenamesPair(first=individual1_photo, second=individual2_photo)
        self.api.report_false_positive_duplicate(false_positive_pair, program_slug)

    def report_individuals_status(self, program_slug: str, individual_ids: list[str], action: str) -> None:
        if not bool(flag_state("BIOMETRIC_DEDUPLICATION_REPORT_INDIVIDUALS_STATUS")):  # pragma no cover
            return

        try:
            self.api.report_individuals_status(
                program_slug,
                {"action": action, "targets": individual_ids},
            )
        except DeduplicationEngineAPI.DeduplicationEngineAPIError:  # pragma no cover
            logging.exception(f"RDI {action}, error while sending Individuals status to Deduplication Engine")
