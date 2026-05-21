import dataclasses
from functools import reduce
from itertools import batched
import logging
from operator import add
from typing import cast
from urllib.parse import urlencode

from constance import config

from hope.apps.core.api.mixins import BaseAPI

logger = logging.getLogger(__name__)


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

    API_EXCEPTION_CLASS = DeduplicationEngineAPIError
    API_MISSING_CREDENTIALS_EXCEPTION_CLASS = DeduplicationEngineMissingAPICredentialsError

    class Endpoints:
        GET_DEDUPLICATION_SETS = "deduplication_sets/"  # GET - List view
        GET_DEDUPLICATION_SET = "deduplication_sets/{program_unicef_id}/"  # GET - Detail view
        CREATE_DEDUPLICATION_SET = "deduplication_sets/"  # POST - Create view
        DELETE_DEDUPLICATION_SET = "deduplication_sets/{program_unicef_id}/"  # DELETE - Delete view
        PROCESS_DEDUPLICATION = "deduplication_sets/{program_unicef_id}/process/"  # POST
        INDIVIDUALS_STATUS = "deduplication_sets/{program_unicef_id}/approve_or_reject/"  # POST

        BULK_UPLOAD_IMAGES = "deduplication_sets/{program_unicef_id}/images_bulk/"  # POST - Create view
        BULK_DELETE_IMAGES = "deduplication_sets/{program_unicef_id}/images_bulk/clear/"

        GET_DUPLICATES = "deduplication_sets/{program_unicef_id}/duplicates/"  # GET - List view
        IGNORED_KEYS = "deduplication_sets/{program_unicef_id}/ignored/reference_pks/"  # POST/GET
        IGNORED_FILENAMES = "deduplication_sets/{program_unicef_id}/ignored/filenames/"  # POST/GET

        GET_GROUP_FINDINGS = "deduplication_set_groups/{rdi_reference_id}/findings/"  # GET - List view
        APPROVE_GROUP = "deduplication_set_groups/{rdi_reference_id}/approve/"  # POST

    def delete_deduplication_set(self, program_unicef_id: str) -> dict:
        url = self.get_url(self.Endpoints.DELETE_DEDUPLICATION_SET.format(program_unicef_id=program_unicef_id))
        response_data, _ = self._delete(url)
        return response_data

    def create_deduplication_set(self, deduplication_set: DeduplicationSet) -> dict:
        url = self.get_url(self.Endpoints.CREATE_DEDUPLICATION_SET)
        response_data, _ = self._post(
            url,
            dataclasses.asdict(deduplication_set),
        )
        return response_data

    def get_deduplication_set(self, program_unicef_id: str) -> dict:
        url = self.get_url(self.Endpoints.GET_DEDUPLICATION_SET.format(program_unicef_id=program_unicef_id))
        response_data, _ = self._get(url)
        return response_data

    def _bulk_upload_image_batch(self, program_unicef_id: str, images: tuple[DeduplicationImage, ...]) -> list:
        url = self.get_url(self.Endpoints.BULK_UPLOAD_IMAGES.format(program_unicef_id=program_unicef_id))
        response_data, _ = self._post(
            url,
            [dataclasses.asdict(image) for image in images],
        )
        # API returns a list of objects
        # empty dict means we got a JSON parsing error
        if isinstance(response_data, dict):
            return []
        return cast("list", response_data)

    def bulk_upload_images(self, program_unicef_id: str, images: list[DeduplicationImage]) -> list:
        response_data = [
            self._bulk_upload_image_batch(program_unicef_id, batch)
            for batch in batched(images, config.DEDUPLICATION_IMAGE_UPLOAD_BATCH_SIZE, strict=False)
        ]
        return reduce(add, response_data, [])

    def bulk_delete_images(self, program_unicef_id: str) -> dict:
        url = self.get_url(self.Endpoints.BULK_UPLOAD_IMAGES.format(program_unicef_id=program_unicef_id))
        response_data, _ = self._delete(url)
        return response_data

    def get_duplicates(self, program_unicef_id: str, individual_ids: list[str]) -> list[dict]:
        url = self.get_url(self.Endpoints.GET_DUPLICATES.format(program_unicef_id=program_unicef_id))

        # Build query string but keep commas unescaped
        params_str = urlencode({"reference_pk": ",".join(individual_ids)}, safe=",")

        return self._get_paginated(url, params=params_str)

    def process_deduplication(self, program_unicef_id: str) -> tuple[dict, int]:
        url = self.get_url(self.Endpoints.PROCESS_DEDUPLICATION.format(program_unicef_id=program_unicef_id))
        response_data, status = self._post(
            url,
            validate_response=False,
        )
        return response_data, status

    def report_false_positive_duplicate(
        self, false_positive_pair: IgnoredFilenamesPair, program_unicef_id: str
    ) -> None:
        url = self.get_url(self.Endpoints.IGNORED_FILENAMES.format(program_unicef_id=program_unicef_id))
        self._post(
            url,
            dataclasses.asdict(false_positive_pair),
        )

    def report_individuals_status(self, program_unicef_id: str, data: dict) -> None:
        url = self.get_url(self.Endpoints.INDIVIDUALS_STATUS.format(program_unicef_id=program_unicef_id))
        self._post(
            url,
            data,
        )

    @staticmethod
    def _create_get_group_findings_params(
        individual_reference_pks: list[str] | None,
        status_code: str | None,
        updated_after: str | None,
        updated_before: str | None,
    ) -> str | None:
        filters: dict[str, str] = {}
        if individual_reference_pks:
            filters["reference_pk"] = ",".join(individual_reference_pks)
        if status_code:
            filters["status_code"] = status_code
        if updated_after:
            filters["updated_after"] = updated_after
        if updated_before:
            filters["updated_before"] = updated_before
        return urlencode(filters, safe=",") if filters else None

    def get_group_findings(
        self,
        rdi_reference_id: str,
        *,
        individual_reference_pks: list[str] | None = None,
        status_code: str | None = None,
        updated_after: str | None = None,
        updated_before: str | None = None,
    ) -> list[dict]:
        url = self.get_url(self.Endpoints.GET_GROUP_FINDINGS.format(rdi_reference_id=rdi_reference_id))
        params = self._create_get_group_findings_params(
            individual_reference_pks=individual_reference_pks,
            status_code=status_code,
            updated_after=updated_after,
            updated_before=updated_before,
        )
        logger.info(f"Engine: GET findings rdi_reference_id={rdi_reference_id} params={params}")
        return self._get_paginated(url, params=params)

    def approve_group(self, rdi_reference_id: str) -> tuple[dict, int]:
        url = self.get_url(self.Endpoints.APPROVE_GROUP.format(rdi_reference_id=rdi_reference_id))
        logger.info(f"Engine: POST approve rdi_reference_id={rdi_reference_id}")
        return self._post(url)
