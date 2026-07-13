import dataclasses
import logging
from urllib.parse import urlencode

from hope.apps.core.api.mixins import BaseAPI

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SimilarityPair:
    score: float
    status_code: str
    first: str | None = None
    second: str | None = None


class BiometricDeduplicationEngineAPI(BaseAPI):
    API_KEY_ENV_NAME = "DEDUPLICATION_ENGINE_API_KEY"
    API_URL_ENV_NAME = "DEDUPLICATION_ENGINE_API_URL"

    class BiometricDeduplicationEngineAPIError(Exception):
        pass

    class BiometricDeduplicationEngineMissingAPICredentialsError(Exception):
        pass

    API_EXCEPTION_CLASS = BiometricDeduplicationEngineAPIError
    API_MISSING_CREDENTIALS_EXCEPTION_CLASS = BiometricDeduplicationEngineMissingAPICredentialsError

    class Endpoints:
        GET_RDI_FINDINGS = "deduplication_sets/{rdi_country_workspace_id}/findings/"

    @staticmethod
    def _create_get_rdi_findings_params(
        status_code: str | None,
        updated_after: str | None,
        updated_before: str | None,
    ) -> str | None:
        filters: dict[str, str] = {}
        if status_code:
            filters["status_code"] = status_code
        if updated_after:
            filters["updated_after"] = updated_after
        if updated_before:
            filters["updated_before"] = updated_before
        return urlencode(filters, safe=",") if filters else None

    def get_rdi_findings(
        self,
        rdi_country_workspace_id: str,
        *,
        status_code: str | None = None,
        updated_after: str | None = None,
        updated_before: str | None = None,
    ) -> list[dict]:
        url = self.get_url(self.Endpoints.GET_RDI_FINDINGS.format(rdi_country_workspace_id=rdi_country_workspace_id))
        params = self._create_get_rdi_findings_params(
            status_code=status_code,
            updated_after=updated_after,
            updated_before=updated_before,
        )
        return self._get_paginated(url, params=params)
