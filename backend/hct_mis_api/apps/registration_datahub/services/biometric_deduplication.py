import logging
import uuid
from typing import List

from django.db.models import QuerySet

from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.payment.api.dataclasses import SimilarityPair
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import (
    DeduplicationEngineSimilarityPair,
    RegistrationDataImport,
)
from hct_mis_api.apps.registration_datahub.apis.deduplication_engine import (
    DeduplicationEngineAPI,
    DeduplicationImage,
    DeduplicationImageSet,
    DeduplicationSet,
)


class BiometricDeduplicationService:
    class BiometricDeduplicationServiceException(Exception):
        pass

    def __init__(self) -> None:
        self.api = DeduplicationEngineAPI()

    def create_deduplication_set(self, program: Program) -> None:
        program.deduplication_set_id = uuid.uuid4()
        program.save(update_fields=["deduplication_set_id"])

        deduplication_set = DeduplicationSet(name=program.name, reference_id=str(program.deduplication_set_id))
        self.api.create_deduplication_set(deduplication_set)

    def upload_individuals(self, deduplication_set_id: str, rdi: RegistrationDataImport) -> None:
        individuals = (
            Individual.objects.filter(is_removed=False, registration_data_import=rdi)
            .exclude(photo="")
            .only("id", "photo")
        )  # TODO MB exclude withdrawn/duplicate?

        images = DeduplicationImageSet(
            data=[
                DeduplicationImage(id=str(individual.id), image_url=individual.photo.name) for individual in individuals
            ]
        )
        try:
            self.api.bulk_upload_images(deduplication_set_id, images)
            rdi.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_UPLOADED
            rdi.save(update_fields=["deduplication_engine_status"])

        except DeduplicationEngineAPI.DeduplicationEngineAPIException:
            logging.exception(f"Failed to upload images for RDI {rdi} to deduplication set {deduplication_set_id}")
            rdi.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_ERROR
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

        rdis = RegistrationDataImport.objects.filter(
            program=program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING
        )
        for rdi in rdis:
            self.upload_individuals(deduplication_set_id, rdi)

        all_uploaded = (
            rdis.count()
            == rdis.filter(deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_UPLOADED).count()
        )
        if all_uploaded:
            self.process_deduplication_set(deduplication_set_id, rdis)
        else:
            raise self.BiometricDeduplicationServiceException("Failed to upload images for all RDIs")

    def delete_deduplication_set(self, program: Program) -> None:
        self.api.delete_deduplication_set(str(program.deduplication_set_id))
        program.deduplication_set_id = None
        program.save(update_fields=["deduplication_set_id"])

    @classmethod
    def mark_rdis_as_pending(cls, program: Program) -> None:
        RegistrationDataImport.objects.filter(program=program, deduplication_engine_status__isnull=True).update(
            status=RegistrationDataImport.DEDUP_ENGINE_PENDING
        )

    def create_duplicates(self, deduplication_set_id: str, similarity_pairs: List[SimilarityPair]) -> None:
        DeduplicationEngineSimilarityPair.bulk_add_duplicates(deduplication_set_id, similarity_pairs)

    def mark_rdis_as_deduplicated(self, deduplication_set_id: str) -> None:
        program = Program.objects.get(deduplication_set_id=deduplication_set_id)
        RegistrationDataImport.objects.filter(
            program=program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS
        ).update(deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED)

    def create_biometric_deduplication_grievance_tickets_for_already_merged_individuals(
        self, deduplication_set_id: str
    ) -> None:
        pass
