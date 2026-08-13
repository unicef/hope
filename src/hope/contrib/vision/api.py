from datetime import datetime, timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
import requests

from hope.apps.core.api.mixins import BaseAPI
from hope.contrib.api.serializers.vision import PaymentPlanPayloadSerializer
from hope.contrib.vision.choices import VISION_SEND_MUTABLE_STATUSES, VisionLogEntryType, VisionStatus
from hope.contrib.vision.services import VisionService
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
    SEND_MUTABLE_STATUSES = VISION_SEND_MUTABLE_STATUSES

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

    @classmethod
    def _persist_send_result(
        cls,
        payment_plan: PaymentPlan,
        entry: dict,
        send_status: VisionStatus,
        *,
        sent: bool = False,
    ) -> None:
        with transaction.atomic():
            locked_payment_plan = PaymentPlan.objects.select_for_update().get(pk=payment_plan.pk)
            vision_data = cls._vision_data(locked_payment_plan)
            vision_data.setdefault("log", []).append(entry)

            current_status = str(vision_data.get("status") or VisionStatus.NOT_SENT.value)
            if (
                locked_payment_plan.status == PaymentPlan.Status.IN_REVIEW
                and current_status in cls.SEND_MUTABLE_STATUSES
            ):
                if sent:
                    vision_data["sent"] = True
                VisionService.set_status(locked_payment_plan, send_status)

            PaymentPlan.objects.filter(pk=locked_payment_plan.pk).update(
                internal_data=locked_payment_plan.internal_data
            )

        # Keep the caller's instance aligned with the row merged under lock. In particular, do not leave the async
        # task holding the stale pre-callback JSON after a callback wins the race with the outbound response.
        payment_plan.internal_data = locked_payment_plan.internal_data

    def send_payment_plan(self, payment_plan: PaymentPlan) -> dict:
        if getattr(payment_plan, "sent_to_vision", False) is True:
            raise VisionAPIError("Payment plan has already been sent to Vision")

        payload = PaymentPlanPayloadSerializer(payment_plan).data
        entry = {
            "timestamp": timezone.now().isoformat(),
            "type": VisionLogEntryType.API_CALL.value,
            "payload": {k: str(v) for k, v in payload.items()},
            "response": {},
        }
        try:
            self._ensure_token()
            response, _ = self._post(self.payment_plan_creation_url, payload)
            entry["response"] = response
        except VisionAPIMissingCredentialsError:
            entry["response"] = {"error": "Vision API credentials are not configured"}
            self._persist_send_result(payment_plan, entry, VisionStatus.SEND_FAILED)
            raise
        except (BaseAPI.APIError, VisionAPIError, requests.RequestException) as e:
            entry["response"] = {"error": str(e)}
            self._persist_send_result(payment_plan, entry, VisionStatus.SEND_FAILED)
            raise VisionAPIError(str(e)) from e
        self._persist_send_result(
            payment_plan,
            entry,
            VisionStatus.WAITING_FOR_CALLBACK,
            sent=True,
        )
        return response
