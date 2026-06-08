from datetime import datetime, timedelta

from django.conf import settings
import requests
from requests import session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from hope.apps.core.api.mixins import BaseAPI
from hope.models import PaymentPlan


class VisionAPIError(Exception):
    pass


class VisionAPIMissingCredentialsError(Exception):
    pass


class VisionAPI(BaseAPI):
    API_URL_ENV_NAME = "VISION_API_URL"

    def __init__(self) -> None:
        self.api_url = settings.VISION_API_URL
        if not self.api_url:
            raise VisionAPIMissingCredentialsError(f"Missing {self.__class__.__name__} URL")
        self._client = session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[502, 503, 504],
            allowed_methods=None,
        )
        self._client.mount(self.api_url, HTTPAdapter(max_retries=retries))
        self._token_expiry: datetime | None = None

    def _acquire_token(self) -> None:
        token_url = f"{self.api_url.rstrip('/')}/v1/OAuthService/GenerateToken"
        client_id = settings.VISION_CLIENT_ID
        client_secret = settings.VISION_CLIENT_SECRET
        grant_type = settings.VISION_TOKEN_GRANT_TYPE
        timeout = settings.VISION_DEFAULT_TIMEOUT

        if not client_id or not client_secret:
            raise VisionAPIMissingCredentialsError("Missing Vision OAuth credentials")

        response = requests.post(
            token_url,
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": grant_type,
            },
            timeout=timeout,
        )

        if response.status_code == 401:
            raise VisionAPIError(f"Vision OAuth authentication failed: {response.json()}")

        response.raise_for_status()
        data = response.json()
        self._client.headers["Authorization"] = f"Bearer {data['access_token']}"
        expires_in = int(data.get("expires_in", 3600))
        self._token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)

    def _ensure_token(self) -> None:
        if not self._token_expiry or datetime.now() >= self._token_expiry:
            self._acquire_token()

    class Endpoints:
        PP_CREATION = "ps/ezcash/PaymentPlan"

    def get_url(self, endpoint: str) -> str:
        base = self.api_url.rstrip("/")
        return f"{base}/{endpoint.lstrip('/')}"

    def _post_to(self, endpoint: str, data: dict) -> dict:
        return self._post(self.get_url(endpoint), data)[0]

    def _get_from(self, endpoint: str, params: dict | None = None) -> dict:
        return self._get(self.get_url(endpoint), params)[0]

    def send_payment_plan(self, payment_plan: PaymentPlan) -> dict:
        self._ensure_token()
        payload = {
            "businessArea": payment_plan.business_area.code,
            "vendorNumber": payment_plan.financial_service_provider.vision_vendor_number,
            "payplanSno": payment_plan.unicef_id,
            "payplanDesc": payment_plan.name,
            "currency": payment_plan.currency.code,
            "authAmt": payment_plan.total_entitled_quantity,
            "authAmtUsd": payment_plan.total_entitled_quantity_usd,
            "status": payment_plan.status,
            "headVendor": payment_plan.financial_service_provider.name,
            "creationDate": payment_plan.created_at.strftime("%Y%m%d"),
        }
        try:
            response = self._post_to(self.Endpoints.PP_CREATION, payload)
            entry = {"payload": {k: str(v) for k, v in payload.items()}, "response": response}
        except BaseAPI.APIError as e:
            entry = {"payload": {k: str(v) for k, v in payload.items()}, "response": {"error": str(e)}}
            vision_log = payment_plan.internal_data.setdefault("vision", [])
            vision_log.append(entry)
            payment_plan.save(update_fields=["internal_data"])
            raise VisionAPIError(str(e)) from e
        vision_log = payment_plan.internal_data.setdefault("vision", [])
        vision_log.append(entry)
        payment_plan.save(update_fields=["internal_data"])
        return response
