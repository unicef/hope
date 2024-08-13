import dataclasses
from typing import List, Tuple

from hct_mis_api.apps.core.api.mixins import BaseAPI


@dataclasses.dataclass
class DeduplicationSet:
    name: str  # program.name
    reference_id: str  # program.id


@dataclasses.dataclass
class DeduplicationImage:
    id: str  # individual.id
    image_url: str  # individual.photo.name # filter out blank photos


@dataclasses.dataclass
class DeduplicationImageSet:
    data: List[DeduplicationImage]


class DeduplicationEngineAPI(BaseAPI):
    # TODO MB add to envs
    API_KEY_ENV_NAME = "DEDUPLICATION_ENGINE_API_KEY"
    API_URL_ENV_NAME = "DEDUPLICATION_ENGINE_API_URL"

    class DeduplicationEngineAPIException(Exception):
        pass

    class DeduplicationEngineMissingAPICredentialsException(Exception):
        pass

    API_EXCEPTION_CLASS = DeduplicationEngineAPIException
    API_MISSING_CREDENTIALS_EXCEPTION_CLASS = DeduplicationEngineMissingAPICredentialsException

    class Endpoints:
        GET_DEDUPLICATION_SETS = "deduplication_sets/"  # GET - List view
        CREATE_DEDUPLICATION_SET = "deduplication_sets/"  # POST - Create view
        DELETE_DEDUPLICATION_SET = "deduplication_sets/{pk}/"  # DELETE - Delete view
        PROCESS_DEDUPLICATION = "deduplication_sets/{pk}/process/"  # POST - Start processing a deduplication set

        BULK_UPLOAD_IMAGES = "deduplication_sets/{deduplication_set_pk}/images_bulk/"  # POST - Create view
        BULK_DELETE_IMAGES = "deduplication_sets/{deduplication_set_pk}/images_bulk/clear/"  # DELETE - Delete all images for a deduplication set

        GET_DUPLICATES = "deduplication_sets/{deduplication_set_pk}/duplicates/"  # GET - List view

    def delete_deduplication_set(self, deduplication_set_id: str) -> dict:
        response_data, _ = self._delete(self.Endpoints.DELETE_DEDUPLICATION_SET.format(pk=deduplication_set_id))
        return response_data

    def create_deduplication_set(self, deduplication_set: DeduplicationSet) -> dict:
        response_data, _ = self._post(self.Endpoints.CREATE_DEDUPLICATION_SET, dataclasses.asdict(deduplication_set))
        return response_data

    def bulk_upload_images(self, deduplication_set_id: str, images: DeduplicationImageSet) -> dict:
        response_data, _ = self._post(
            self.Endpoints.BULK_UPLOAD_IMAGES.format(deduplication_set_pk=deduplication_set_id),
            dataclasses.asdict(images),
        )
        return response_data

    def bulk_delete_images(self, deduplication_set_id: str) -> dict:
        response_data, _ = self._delete(
            self.Endpoints.BULK_UPLOAD_IMAGES.format(deduplication_set_pk=deduplication_set_id)
        )
        return response_data

    def get_duplicates(self, deduplication_set_id: str) -> dict:
        response_data, _ = self._get(self.Endpoints.GET_DUPLICATES.format(pk=deduplication_set_id))
        return response_data

    def process_deduplication(self, deduplication_set_id: str) -> Tuple[dict, int]:
        response_data, status = self._post(
            self.Endpoints.PROCESS_DEDUPLICATION.format(pk=deduplication_set_id), validate_response=False
        )
        return response_data, status
