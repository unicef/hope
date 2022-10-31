import logging
import time
from io import BytesIO
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from django.conf import settings

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RetryError
from requests.packages.urllib3.util.retry import Retry

from hct_mis_api.apps.core.kobo.common import filter_by_owner
from hct_mis_api.apps.core.models import BusinessArea, XLSXKoboTemplate
from hct_mis_api.apps.utils.exceptions import log_and_raise

logger = logging.getLogger(__name__)


class TokenNotProvided(Exception):
    pass


class TokenInvalid(Exception):
    pass


class KoboRequestsSession(requests.Session):
    AUTH_DOMAINS = [urlparse(settings.KOBO_KF_URL).hostname, urlparse(settings.KOBO_KC_URL).hostname]

    def should_strip_auth(self, old_url, new_url) -> bool:
        new_parsed = urlparse(new_url)
        if new_parsed.hostname in KoboRequestsSession.AUTH_DOMAINS:
            return False
        return super().should_strip_auth(old_url, new_url)


class KoboAPI:
    # KPI_URL = os.getenv("KOBO_KF_URL", "https://kobo.humanitarianresponse.info")

    def __init__(self, business_area_slug: str = None, kpi_url: str = None):
        self.KPI_URL = kpi_url or settings.KOBO_KF_URL
        if business_area_slug is not None:
            self.business_area = BusinessArea.objects.get(slug=business_area_slug)
        else:
            self.business_area = None
        self._get_token()

    def _handle_paginated_results(self, url) -> List[Dict]:
        next_url = url
        results: List = []

        # if there will be more than 30000 results,
        # we need to make additional queries
        while next_url:
            data = self._handle_request(next_url)
            next_url = data["next"]
            results.extend(data["results"])
        return results

    def _get_url(self, endpoint: str, append_api=True, add_limit=True, additional_query_params=None):
        endpoint.strip("/")
        if endpoint != "token" and append_api is True:
            endpoint = f"api/v2/{endpoint}"
        # According to the Kobo API documentation,
        # the maximum limit per page is 30000
        query_params = f"format=json{'&limit=30000' if add_limit else ''}"
        if additional_query_params is not None:
            query_params += f"&{additional_query_params}"
        return f"{self.KPI_URL}/{endpoint}?{query_params}"

    def _get_token(self):
        self._client = KoboRequestsSession()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504], method_whitelist=False)
        self._client.mount(self.KPI_URL, HTTPAdapter(max_retries=retries))

        token = settings.KOBO_MASTER_API_TOKEN

        if not token:
            logger.error("KOBO Token is not set")
            raise TokenNotProvided("Token is not set")

        self._client.headers.update({"Authorization": f"token {token}"})

    def _handle_request(self, url) -> Dict:
        response = self._client.get(url=url)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.exception(e)
            raise
        return response.json()

    def _post_request(self, url, data=None, files=None) -> requests.Response:
        response = self._client.post(url=url, data=data, files=files)
        return response

    def _patch_request(self, url, data=None, files=None) -> requests.Response:
        response = self._client.patch(url=url, data=data, files=files)
        return response

    def create_template_from_file(
        self, bytes_io_file, xlsx_kobo_template_object, template_id=""
    ) -> Optional[Tuple[Dict, str]]:
        data = {
            "name": "Untitled",
            "asset_type": "template",
            "description": "",
            "sector": "",
            "country": "",
            "share-metadata": False,
        }
        if not template_id:
            asset_response = self._post_request(url=self._get_url("assets/", add_limit=False), data=data)
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
            "destination": self._get_url(f"assets/{asset_uid}/", append_api=False, add_limit=False),
        }
        file_import_response = self._post_request(
            url=self._get_url("imports/", append_api=False, add_limit=False),
            data=file_import_data,
            files={"file": bytes_io_file},
        )
        file_import_response_dict = file_import_response.json()
        url = file_import_response_dict.get("url")

        attempts = 5
        while attempts >= 0:
            response_dict = self._handle_request(url)
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

    def get_all_projects_data(self) -> List:
        if not self.business_area:
            logger.error("Business area is not provided")
            raise ValueError("Business area is not provided")
        projects_url = self._get_url("assets")

        response_dict = self._handle_paginated_results(projects_url)
        return filter_by_owner(response_dict, self.business_area)

    def get_single_project_data(self, uid: str) -> Dict:
        projects_url = self._get_url(f"assets/{uid}")

        return self._handle_request(projects_url)

    def get_project_submissions(self, uid: str, only_active_submissions) -> List:
        additional_query_params = None
        if only_active_submissions:
            additional_query_params = 'query={"_validation_status.uid":"validation_status_approved"}'
        submissions_url = self._get_url(
            f"assets/{uid}/data",
            additional_query_params=additional_query_params,
        )

        response_dict = self._handle_paginated_results(submissions_url)
        return response_dict

    def get_attached_file(self, url: str) -> BytesIO:
        response = self._client.get(url=url)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.exception(e)
            raise
        file = BytesIO(response.content)
        return file
