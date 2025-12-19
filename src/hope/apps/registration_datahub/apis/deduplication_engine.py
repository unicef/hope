import dataclasses
from functools import reduce
from itertools import batched
from operator import add
from typing import cast

from constance import config

from hope.apps.core.api.mixins import BaseAPI


@dataclasses.dataclass
class SimilarityPair:
    score: float
    status_code: str
    first: str | None = None
    second: str | None = None


@dataclasses.dataclass
class DeduplicationSetData:
    state: str
    error: str = ""


@dataclasses.dataclass
class DeduplicationSet:
    reference_pk: str  # program.id
    notification_url: str  # webhook url


@dataclasses.dataclass
class DeduplicationImage:
    reference_pk: str  # individual.id
    filename: str  # individual.photo.name


@dataclasses.dataclass
class IgnoredFilenamesPair:
    first: str  # individual.photo.name
    second: str  # individual.photo.name


class DeduplicationEngineAPI(BaseAPI):
    API_KEY_ENV_NAME = "DEDUPLICATION_ENGINE_API_KEY"
    API_URL_ENV_NAME = "DEDUPLICATION_ENGINE_API_URL"

    class DeduplicationEngineAPIError(Exception):
        pass

    class DeduplicationEngineMissingAPICredentialsError(Exception):
        pass

    API_EXCEPTION_CLASS = DeduplicationEngineAPIError  # type: ignore
    API_MISSING_CREDENTIALS_EXCEPTION_CLASS = DeduplicationEngineMissingAPICredentialsError  # type: ignore

    class Endpoints:
        GET_DEDUPLICATION_SETS = "deduplication_sets/"  # GET - List view
        GET_DEDUPLICATION_SET = "deduplication_sets/{program_slug}/"  # GET - Detail view
        CREATE_DEDUPLICATION_SET = "deduplication_sets/"  # POST - Create view
        DELETE_DEDUPLICATION_SET = "deduplication_sets/{program_slug}/"  # DELETE - Delete view
        PROCESS_DEDUPLICATION = "deduplication_sets/{program_slug}/process/"  # POST
        INDIVIDUALS_STATUS = "deduplication_sets/{program_slug}/approve_or_reject/"  # POST

        BULK_UPLOAD_IMAGES = "deduplication_sets/{program_slug}/images_bulk/"  # POST - Create view
        BULK_DELETE_IMAGES = "deduplication_sets/{program_slug}/images_bulk/clear/"

        GET_DUPLICATES = "deduplication_sets/{program_slug}/duplicates/"  # GET - List view
        IGNORED_KEYS = "deduplication_sets/{program_slug}/ignored/reference_pks/"  # POST/GET
        IGNORED_FILENAMES = "deduplication_sets/{program_slug}/ignored/filenames/"  # POST/GET

    def delete_deduplication_set(self, program_slug: str) -> dict:
        response_data, _ = self._delete(self.Endpoints.DELETE_DEDUPLICATION_SET.format(program_slug=program_slug))
        return response_data

    def create_deduplication_set(self, deduplication_set: DeduplicationSet) -> dict:
        response_data, _ = self._post(
            self.Endpoints.CREATE_DEDUPLICATION_SET,
            dataclasses.asdict(deduplication_set),
        )
        return response_data

    def get_deduplication_set(self, program_slug: str) -> dict:
        response_data, _ = self._get(self.Endpoints.GET_DEDUPLICATION_SET.format(program_slug=program_slug))
        return response_data

    def _bulk_upload_image_batch(self, program_slug: str, images: tuple[DeduplicationImage, ...]) -> list:
        response_data, _ = self._post(
            self.Endpoints.BULK_UPLOAD_IMAGES.format(program_slug=program_slug),
            [dataclasses.asdict(image) for image in images],
        )
        # API returns a list of objects
        # empty dict means we got a JSON parsing error
        if isinstance(response_data, dict):
            return []
        return cast("list", response_data)

    def bulk_upload_images(self, program_slug: str, images: list[DeduplicationImage]) -> list:
        response_data = [
            self._bulk_upload_image_batch(program_slug, batch)
            for batch in batched(images, config.DEDUPLICATION_IMAGE_UPLOAD_BATCH_SIZE, strict=False)
        ]
        return reduce(add, response_data, [])

    def bulk_delete_images(self, program_slug: str) -> dict:
        response_data, _ = self._delete(self.Endpoints.BULK_UPLOAD_IMAGES.format(program_slug=program_slug))
        return response_data

    def get_duplicates(self, program_slug: str, individual_ids: list[str]) -> list[dict]:
        return self._get_paginated(
            self.Endpoints.GET_DUPLICATES.format(program_slug=program_slug),
            params={"reference_pk": ",".join(individual_ids)},
        )

    def process_deduplication(self, program_slug: str) -> tuple[dict, int]:
        response_data, status = self._post(
            self.Endpoints.PROCESS_DEDUPLICATION.format(program_slug=program_slug),
            validate_response=False,
        )
        return response_data, status

    def report_false_positive_duplicate(self, false_positive_pair: IgnoredFilenamesPair, program_slug: str) -> None:
        self._post(
            self.Endpoints.IGNORED_FILENAMES.format(program_slug=program_slug),
            dataclasses.asdict(false_positive_pair),
        )

    def report_individuals_status(self, program_slug: str, data: dict) -> None:
        self._post(
            self.Endpoints.INDIVIDUALS_STATUS.format(program_slug=program_slug),
            data,
        )
