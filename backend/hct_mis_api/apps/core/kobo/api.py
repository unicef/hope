import logging
import time
import typing
from io import BytesIO
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from django.conf import settings

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from requests.exceptions import RetryError
from requests.packages.urllib3.util.retry import Retry

from hct_mis_api.apps.core.models import XLSXKoboTemplate
from hct_mis_api.apps.utils.exceptions import log_and_raise

logger = logging.getLogger(__name__)


class CountryCodeNotProvided(Exception):
    pass


class KoboRequestsSession(requests.Session):
    AUTH_DOMAINS = [urlparse(settings.KOBO_KF_URL).hostname, urlparse(settings.KOBO_KC_URL).hostname]

    def should_strip_auth(self, old_url: str, new_url: str) -> bool:
        new_parsed = urlparse(new_url)
        if new_parsed.hostname in KoboRequestsSession.AUTH_DOMAINS:  # pragma: no cover
            return False
        return super().should_strip_auth(old_url, new_url)  # type: ignore # FIXME: Call to untyped function "should_strip_auth" in typed context


class KoboAPI:
    LIMIT = 30_000
    FORMAT = "json"

    def __init__(
        self, kpi_url: Optional[str] = None, token: Optional[str] = None, project_views_id: Optional[str] = None
    ) -> None:
        self._kpi_url = kpi_url or settings.KOBO_KF_URL
        self._token = token or settings.KOBO_MASTER_API_TOKEN
        self._project_views_id = project_views_id or settings.KOBO_PROJECT_VIEWS_ID

        self._client = KoboRequestsSession()
        self._set_token()

    def _set_token(self) -> None:
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504], allowed_methods=False)
        self._client.mount(self._kpi_url, HTTPAdapter(max_retries=retries))
        self._client.headers.update({"Authorization": f"token {self._token}"})

    def _get_paginated_request(self, url: str) -> List[Dict]:
        next_url = url
        results: List = []

        while next_url:
            response = self._get_request(next_url)
            data = response.json()
            next_url = data["next"]
            results.extend(data["results"])
        return results

    def _get_request(self, url: str) -> Response:
        response = self._client.get(url=url)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:  # pragma: no cover
            logger.exception(e)
            raise
        return response

    def _post_request(
        self, url: str, data: Optional[Dict] = None, files: Optional[typing.IO] = None
    ) -> Response:  # pragma: no cover
        return self._client.post(url=url, data=data, files=files)

    def create_template_from_file(
        self, bytes_io_file: typing.IO, xlsx_kobo_template_object: XLSXKoboTemplate, template_id: str = ""
    ) -> Optional[Tuple[Dict, str]]:  # pragma: no cover
        # TODO: not sure if this actually works
        if not template_id:
            data = {
                "name": "Untitled",
                "asset_type": "template",
                "description": "",
                "sector": "",
                "country": "",
                "share-metadata": False,
            }
            endpoint = "api/v2/assets"
            query_params = f"format={self.FORMAT}"
            url = f"{self._kpi_url}/{endpoint}?{query_params}"
            asset_response = self._post_request(url=url, data=data)
            try:
                asset_response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logger.exception(e)
                raise
            asset_response_dict = asset_response.json()
            asset_uid = asset_response_dict.get("uid")
        else:
            asset_uid = template_id

        file_import_data = {
            "assetUid": asset_uid,
            "destination": f"{self._kpi_url}/assets/{asset_uid}?format={self.FORMAT}",
        }
        file_import_response = self._post_request(
            url=f"{self._kpi_url}/imports?format={self.FORMAT}",
            data=file_import_data,
            files={"file": bytes_io_file},  # type: ignore # FIXME
        )
        file_import_response_dict = file_import_response.json()
        url = file_import_response_dict.get("url")

        attempts = 5
        while attempts >= 0:
            response = self._get_request(url)
            response_dict = response.json()
            import_status = response_dict.get("status")
            if import_status == "processing":
                xlsx_kobo_template_object.status = XLSXKoboTemplate.PROCESSING
                xlsx_kobo_template_object.save()
                attempts -= 1
                time.sleep(1)
            else:
                return response_dict, asset_uid

        log_and_raise("Fetching import data took too long", error_type=RetryError)
        return None

    def get_all_projects_data(self, country_code: str) -> List:
        if not country_code:
            raise CountryCodeNotProvided("No country code provided")
        endpoint = f"api/v2/project-views/{self._project_views_id}/assets/"
        query_params = f"format={self.FORMAT}&limit={self.LIMIT}"
        query_params += f"&q=settings__country_codes__icontains:{country_code.upper()}"
        url = f"{self._kpi_url}/{endpoint}?{query_params}"
        return self._get_paginated_request(url)

    def get_single_project_data(self, uid: str) -> Dict:
        endpoint = f"api/v2/assets/{uid}/"
        query_params = f"format={self.FORMAT}&limit={self.LIMIT}"
        url = f"{self._kpi_url}/{endpoint}?{query_params}"
        response = self._get_request(url)
        return response.json()

    def get_project_submissions(self, uid: str, only_active_submissions: bool) -> List[Dict]:
        endpoint = f"api/v2/assets/{uid}/data/"
        query_params = f"format={self.FORMAT}&limit={self.LIMIT}"
        if only_active_submissions:
            additional_query_params = 'query={"_validation_status.uid":"validation_status_approved"}'
            query_params += f"&{additional_query_params}"
        url = f"{self._kpi_url}/{endpoint}?{query_params}"
        return self._get_paginated_request(url)

    def get_attached_file(self, url: str) -> BytesIO:  # pragma: no cover
        response = self._get_request(url)
        return BytesIO(response.content)
