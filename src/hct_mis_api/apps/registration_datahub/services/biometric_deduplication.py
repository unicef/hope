import logging
import uuid
from typing import List

from django.conf import settings
from django.db import transaction
from django.db.models import Q, QuerySet

from hct_mis_api.apps.household.models import Individual, PendingIndividual
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import (
    DeduplicationEngineSimilarityPair,
    RegistrationDataImport,
)
from hct_mis_api.apps.registration_datahub.apis.deduplication_engine import (
    DeduplicationEngineAPI,
    DeduplicationImage,
    DeduplicationSet,
    DeduplicationSetConfig,
    DeduplicationSetData,
    IgnoredFilenamesPair,
    SimilarityPair,
)

logger = logging.getLogger(__name__)


class BiometricDeduplicationService:
    class BiometricDeduplicationServiceException(Exception):
        pass

    def __init__(self) -> None:
        self.api = DeduplicationEngineAPI()

    def create_deduplication_set(self, program: Program) -> None:
        deduplication_set = DeduplicationSet(
            reference_pk=str(program.id),
            notification_url=f"https://{settings.DOMAIN_NAME}/api/rest/{program.business_area.slug}/programs/{str(program.id)}/registration-data/webhookdeduplication/",
            # notification_url=reverse("registration-data:webhook_deduplication", kwargs={"program_id": str(program.id), "business_area": program.business_area.slug}), # TODO MB why reverse is not working
            config=DeduplicationSetConfig(
                face_distance_threshold=1 - (program.business_area.biometric_deduplication_threshold / 100)
            ),
        )
        response_data = self.api.create_deduplication_set(deduplication_set)
        program.deduplication_set_id = uuid.UUID(response_data["id"])
        program.save(update_fields=["deduplication_set_id"])

    def get_deduplication_set_results(self, deduplication_set_id: str) -> dict:
        return self.api.get_duplicates(deduplication_set_id)

    def get_deduplication_set(self, deduplication_set_id: str) -> DeduplicationSetData:
        response_data = self.api.get_deduplication_set(deduplication_set_id)
        return DeduplicationSetData(state=response_data["state"])

    def upload_individuals(self, deduplication_set_id: str, rdi: RegistrationDataImport) -> None:
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
                self.api.bulk_upload_images(deduplication_set_id, images)

            except DeduplicationEngineAPI.DeduplicationEngineAPIException:
                logging.exception(f"Failed to upload images for RDI {rdi} to deduplication set {deduplication_set_id}")
                rdi.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_UPLOAD_ERROR
                rdi.save(update_fields=["deduplication_engine_status"])
                return

        rdi.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_UPLOADED
        rdi.save(update_fields=["deduplication_engine_status"])

    def process_deduplication_set(self, deduplication_set_id: str, rdis: QuerySet[RegistrationDataImport]) -> None:
        response_data, status = self.api.process_deduplication(deduplication_set_id)
        if status == 409:
            raise self.BiometricDeduplicationServiceException(
                f"Deduplication is already in progress for deduplication set {deduplication_set_id}"
            )
        elif status == 200:
            rdis.update(deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS)

        else:
            logging.error(
                f"Failed to process deduplication set {deduplication_set_id}. Response[{status}]: {response_data}"
            )
            rdis.update(deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_ERROR)

    def upload_and_process_deduplication_set(self, program: Program) -> None:
        if not program.biometric_deduplication_enabled:
            raise self.BiometricDeduplicationServiceException("Biometric deduplication is not enabled for this program")

        if not program.deduplication_set_id:
            self.create_deduplication_set(program)

        if RegistrationDataImport.objects.filter(
            program=program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS
        ).exists():
            raise self.BiometricDeduplicationServiceException("Deduplication is already in progress for some RDIs")

        deduplication_set_id = str(program.deduplication_set_id)

        pending_rdis = RegistrationDataImport.objects.filter(
            program=program,
            deduplication_engine_status__in=[
                RegistrationDataImport.DEDUP_ENGINE_PENDING,
                RegistrationDataImport.DEDUP_ENGINE_UPLOAD_ERROR,
                RegistrationDataImport.DEDUP_ENGINE_ERROR,
            ],
        ).exclude(
            status__in=[
                RegistrationDataImport.REFUSED_IMPORT,
            ]
        )
        for rdi in pending_rdis:
            self.upload_individuals(deduplication_set_id, rdi)

        all_uploaded = not pending_rdis.all().exists()  # refetch qs
        if all_uploaded:
            uploaded_rdis = RegistrationDataImport.objects.filter(
                deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_UPLOADED
            ).exclude(
                status__in=[
                    RegistrationDataImport.REFUSED_IMPORT,
                ]
            )
            self.process_deduplication_set(deduplication_set_id, uploaded_rdis)
        else:
            raise self.BiometricDeduplicationServiceException("Failed to upload images for all RDIs")

    def delete_deduplication_set(self, program: Program) -> None:
        if program.deduplication_set_id:
            self.api.delete_deduplication_set(str(program.deduplication_set_id))
            DeduplicationEngineSimilarityPair.objects.filter(program=program).delete()

        program.deduplication_set_id = None
        program.save(update_fields=["deduplication_set_id"])

    def store_similarity_pairs(self, deduplication_set_id: str, similarity_pairs: List[SimilarityPair]) -> None:
        DeduplicationEngineSimilarityPair.remove_pairs(deduplication_set_id)
        DeduplicationEngineSimilarityPair.bulk_add_pairs(deduplication_set_id, similarity_pairs)

    @staticmethod
    def mark_rdis_as_pending(program: Program) -> None:
        RegistrationDataImport.objects.filter(program=program, deduplication_engine_status__isnull=True).update(
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING
        )

    @staticmethod
    def mark_rdis_as_deduplicated(deduplication_set_id: str) -> None:
        program = Program.objects.get(deduplication_set_id=deduplication_set_id)
        RegistrationDataImport.objects.filter(
            program=program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PROCESSING
        ).update(deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED)

    @staticmethod
    def mark_rdis_as_deduplication_error(deduplication_set_id: str) -> None:
        program = Program.objects.get(deduplication_set_id=deduplication_set_id)
        RegistrationDataImport.objects.filter(
            program=program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PROCESSING
        ).update(deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_ERROR)

    @staticmethod
    def mark_rdis_as_processing(deduplication_set_id: str) -> None:
        program = Program.objects.get(deduplication_set_id=deduplication_set_id)
        RegistrationDataImport.objects.filter(
            program=program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS
        ).update(deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PROCESSING)

    def store_rdis_deduplication_statistics(self, deduplication_set_id: str) -> None:
        program = Program.objects.get(deduplication_set_id=deduplication_set_id)
        rdis = RegistrationDataImport.objects.filter(
            status=RegistrationDataImport.IN_REVIEW,
            program=program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PROCESSING,
        )
        for rdi in rdis:
            rdi.dedup_engine_batch_duplicates = self.get_duplicate_individuals_for_rdi_against_batch_count(rdi)
            rdi.dedup_engine_golden_record_duplicates = self.get_duplicate_individuals_for_rdi_against_population_count(
                rdi
            )
            rdi.save(update_fields=["dedup_engine_batch_duplicates", "dedup_engine_golden_record_duplicates"])

    def update_rdis_deduplication_statistics(self, program_id: str) -> None:
        program = Program.objects.get(id=program_id)
        rdis = RegistrationDataImport.objects.filter(
            status=RegistrationDataImport.IN_REVIEW,
            program=program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        )
        for rdi in rdis:
            rdi.dedup_engine_batch_duplicates = self.get_duplicate_individuals_for_rdi_against_batch_count(rdi)
            rdi.dedup_engine_golden_record_duplicates = self.get_duplicate_individuals_for_rdi_against_population_count(
                rdi
            )
            rdi.save(update_fields=["dedup_engine_batch_duplicates", "dedup_engine_golden_record_duplicates"])

    def get_duplicates_for_rdi_against_batch(
        self, rdi: RegistrationDataImport
    ) -> QuerySet[DeduplicationEngineSimilarityPair]:
        """Used in RDI statistics"""
        rdi_individuals = PendingIndividual.objects.filter(registration_data_import=rdi).only("id")
        return DeduplicationEngineSimilarityPair.objects.filter(
            Q(individual1__in=rdi_individuals) & Q(individual2__in=rdi_individuals),
            program=rdi.program,
        ).distinct()

    def get_duplicate_individuals_for_rdi_against_batch_count(self, rdi: RegistrationDataImport) -> int:
        """Used in RDI statistics"""
        duplicates = self.get_duplicates_for_rdi_against_batch(rdi)

        unique_individuals = set()

        for pair in duplicates:
            unique_individuals.add(pair.individual1_id)
            unique_individuals.add(pair.individual2_id)

        return len(unique_individuals)

    def get_duplicates_for_merged_rdi_against_population(
        self, rdi: RegistrationDataImport
    ) -> QuerySet[DeduplicationEngineSimilarityPair]:
        """Used in Grievance tickets creation for merging RDI"""
        rdi_pending_individuals = PendingIndividual.objects.filter(is_removed=False, registration_data_import=rdi).only(
            "id"
        )
        other_pending_individuals = PendingIndividual.objects.filter(is_removed=False, program=rdi.program).exclude(
            id__in=rdi_pending_individuals
        )

        return (
            DeduplicationEngineSimilarityPair.objects.filter(
                Q(individual1__in=rdi_pending_individuals) | Q(individual2__in=rdi_pending_individuals),
                Q(individual1__duplicate=False) & Q(individual2__duplicate=False),
                Q(individual1__withdrawn=False) & Q(individual2__withdrawn=False),
                program=rdi.program,
            )
            .exclude(Q(individual1__in=other_pending_individuals) | Q(individual2__in=other_pending_individuals))
            .distinct()
        )

    def get_duplicates_for_rdi_against_population(
        self, rdi: RegistrationDataImport
    ) -> QuerySet[DeduplicationEngineSimilarityPair]:
        """Used in RDI statistics"""
        rdi_pending_individuals = PendingIndividual.objects.filter(is_removed=False, registration_data_import=rdi).only(
            "id"
        )
        other_pending_individuals = PendingIndividual.objects.filter(is_removed=False, program=rdi.program).exclude(
            id__in=rdi_pending_individuals
        )

        from hct_mis_api.apps.utils.models import MergeStatusModel

        return (
            DeduplicationEngineSimilarityPair.objects.filter(
                Q(individual1__in=rdi_pending_individuals) | Q(individual2__in=rdi_pending_individuals),
                Q(individual1__duplicate=False) & Q(individual2__duplicate=False),
                Q(individual1__withdrawn=False) & Q(individual2__withdrawn=False),
                Q(individual1__rdi_merge_status=MergeStatusModel.MERGED)
                | Q(individual2__rdi_merge_status=MergeStatusModel.MERGED),
                program=rdi.program,
            )
            .exclude(Q(individual1__in=other_pending_individuals) | Q(individual2__in=other_pending_individuals))
            .distinct()
        )

    def get_duplicate_individuals_for_rdi_against_population_count(self, rdi: RegistrationDataImport) -> int:
        """Used in RDI statistics"""
        duplicates = self.get_duplicates_for_rdi_against_population(rdi)
        rdi_individuals = PendingIndividual.objects.filter(is_removed=False, registration_data_import=rdi).values_list(
            "id", flat=True
        )

        unique_individuals = set()

        for pair in duplicates:
            if pair.individual1_id in rdi_individuals:
                unique_individuals.add(pair.individual1_id)
            if pair.individual2_id in rdi_individuals:
                unique_individuals.add(pair.individual2_id)  # pragma: no cover

        return len(unique_individuals)

    def create_grievance_tickets_for_duplicates(self, rdi: RegistrationDataImport) -> None:
        # create tickets only against merged individuals
        from hct_mis_api.apps.grievance.services.needs_adjudication_ticket_services import (
            create_needs_adjudication_tickets_for_biometrics,
        )

        deduplication_pairs = self.get_duplicates_for_merged_rdi_against_population(rdi)

        create_needs_adjudication_tickets_for_biometrics(deduplication_pairs, rdi)

    def fetch_biometric_deduplication_results_and_process(self, deduplication_set_id: str) -> None:
        deduplication_set_data = self.get_deduplication_set(deduplication_set_id)

        if deduplication_set_data.state == "Clean":
            data = self.get_deduplication_set_results(deduplication_set_id)
            similarity_pairs = [
                SimilarityPair(
                    score=item["score"],
                    first=item["first"]["reference_pk"],
                    second=item["second"]["reference_pk"],
                )
                for item in data
            ]
            with transaction.atomic():
                self.store_similarity_pairs(deduplication_set_id, similarity_pairs)
                self.store_rdis_deduplication_statistics(deduplication_set_id)
                self.mark_rdis_as_deduplicated(deduplication_set_id)

        elif deduplication_set_data.state == "Processing":
            self.mark_rdis_as_processing(deduplication_set_id)

        elif deduplication_set_data.state == "Error":
            self.mark_rdis_as_deduplication_error(deduplication_set_id)
            logger.error(
                f"Failed to process deduplication set {deduplication_set_id},"
                f" dedupe engine state: {deduplication_set_data.state}"
            )

    def report_false_positive_duplicate(
        self, individual1_photo: str, individual2_photo: str, deduplication_set_id: str
    ) -> None:
        false_positive_pair = IgnoredFilenamesPair(first=individual1_photo, second=individual2_photo)
        self.api.report_false_positive_duplicate(false_positive_pair, deduplication_set_id)
