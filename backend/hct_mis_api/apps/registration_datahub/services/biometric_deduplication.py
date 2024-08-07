import uuid

from hct_mis_api.apps.household.models import PendingIndividual
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.apis.deduplication_engine import (
    DeduplicationEngineAPI,
    DeduplicationImage,
    DeduplicationImageSet,
    DeduplicationSet,
)


class BiometricDeduplicationService:
    # TODO MB add async task that collects RDIs waiting for dedup and starts deduplication

    def __init__(self) -> None:
        self.api = DeduplicationEngineAPI()

    def create_deduplication_set_for_program(self, program: Program) -> None:
        program.deduplication_set_id = uuid.uuid4()
        program.save(update_fields=["deduplication_set_id"])

        deduplication_set = DeduplicationSet(name=program.name, reference_id=str(program.deduplication_set_id))
        self.api.create_deduplication_set(deduplication_set)

        images = DeduplicationImageSet(
            data=[
                DeduplicationImage(id=str(individual.id), image_url=individual.photo.name)
                for individual in program.individuals.exclude(photo="")
            ]
        )  # TODO MB exclude withdrawn/duplicate

        self.api.bulk_upload_images(deduplication_set.reference_id, images)

        # if process lock not aquired mark all program rdis as waiting for dedup
        self.api.process_deduplication(deduplication_set.reference_id)

    def update_deduplication_set_for_rdi(self, rdi: RegistrationDataImport) -> None:
        # CHeck if other rdis are not waiting for dedup
        deduplication_set_id = str(rdi.program.deduplication_set_id)

        individuals = PendingIndividual.objects.filter(registration_data_import=rdi)

        images = DeduplicationImageSet(
            data=[
                DeduplicationImage(id=str(individual.id), image_url=individual.photo.name)
                for individual in individuals.exclude(photo="")
            ]
        )  # TODO MB exclude withdrawn/duplicate

        self.api.bulk_upload_images(deduplication_set_id, images)

        # if process lock not aquired mark rdi as waiting for dedup
        self.api.process_deduplication(deduplication_set_id)

    def delete_deduplication_set(self, program: Program) -> None:
        # delete na finish program
        # delete na delete rdi?
        self.api.delete_deduplication_set(str(program.deduplication_set_id))
        program.deduplication_set_id = None
        program.save(update_fields=["deduplication_set_id"])
