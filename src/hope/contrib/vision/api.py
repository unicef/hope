from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
import requests

from hope.apps.core.api.mixins import BaseAPI
from hope.contrib.api.serializers.vision import PaymentPlanPayloadSerializer
from hope.contrib.vision.choices import VisionLogEntryType
from hope.models import PaymentPlan


class VisionAPIError(Exception):
    pass


class VisionAPIMissingCredentialsError(Exception):
    pass


class VisionAPI(BaseAPI):
    API_URL_SETTING_NAME = "VISION_API_URL"
    API_AUTHENTICATION_REQUIRED = False
    API_EXCEPTION_CLASS = VisionAPIError
    API_MISSING_CREDENTIALS_EXCEPTION_CLASS = VisionAPIMissingCredentialsError

    def __init__(self) -> None:
        super().__init__()
        base_url = self.api_url.rstrip("/")
        self.token_url = f"{base_url}/v1/OAuthService/GenerateToken"
        self.payment_plan_creation_url = f"{base_url}/ps/ezcash/PaymentPlan"
        self._token_expiry: datetime | None = None

    def _acquire_token(self) -> None:
        client_id = settings.VISION_CLIENT_ID
        client_secret = settings.VISION_CLIENT_SECRET
        grant_type = settings.VISION_TOKEN_GRANT_TYPE
        timeout = settings.VISION_DEFAULT_TIMEOUT

        if not client_id or not client_secret:
            raise VisionAPIMissingCredentialsError("Missing Vision OAuth credentials")

        response = requests.post(
            self.token_url,
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

    @staticmethod
    def _vision_data(payment_plan: PaymentPlan) -> dict:
        return payment_plan.internal_data.setdefault("vision", {})

    def _append_log(self, payment_plan: PaymentPlan, entry: dict) -> dict:
        vision_data = self._vision_data(payment_plan)
        vision_data.setdefault("log", []).append(entry)
        return vision_data

    def send_payment_plan(self, payment_plan: PaymentPlan) -> dict:
        if getattr(payment_plan, "sent_to_vision", False) is True:
            raise VisionAPIError("Payment plan has already been sent to Vision")

        self._ensure_token()
        payload = PaymentPlanPayloadSerializer(payment_plan).data
        entry = {
            "timestamp": timezone.now().isoformat(),
            "type": VisionLogEntryType.API_CALL.value,
            "payload": {k: str(v) for k, v in payload.items()},
            "response": {},
        }
        try:
            response, _ = self._post(self.payment_plan_creation_url, payload)
            entry["response"] = response
        except (BaseAPI.APIError, VisionAPIError) as e:
            entry["response"] = {"error": str(e)}
            self._append_log(payment_plan, entry)
            payment_plan.save(update_fields=["internal_data"])
            raise VisionAPIError(str(e)) from e
        vision_data = self._append_log(payment_plan, entry)
        vision_data["sent"] = True
        payment_plan.save(update_fields=["internal_data"])
        return response
