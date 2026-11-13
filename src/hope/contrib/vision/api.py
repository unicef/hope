from datetime import datetime, timedelta
from typing import Any, cast

from django.conf import settings
from django.db import transaction
from django.utils import timezone
import requests

from hope.apps.core.api.mixins import BaseAPI
from hope.apps.utils.dates import normalize_date
from hope.apps.utils.external_urls import build_url
from hope.contrib.api.serializers.vision import PaymentPlanPayloadSerializer
from hope.contrib.vision.choices import VISION_SEND_MUTABLE_STATUSES, VisionLogEntryType, VisionStatus
from hope.contrib.vision.services import VisionService
from hope.models import PaymentPlan


class VisionAPIError(Exception):
    pass


class VisionAPIMissingCredentialsError(Exception):
    pass


# Refresh the token slightly before it actually expires, so a request started just before
# expiry does not fail with an expired token.
TOKEN_EXPIRY_BUFFER_SECONDS = 60
DEFAULT_TOKEN_LIFETIME_SECONDS = 3600


class VisionAPI(BaseAPI):
    API_URL_SETTING_NAME = "VISION_API_URL"
    API_AUTHENTICATION_REQUIRED = False
    API_EXCEPTION_CLASS = VisionAPIError
    API_MISSING_CREDENTIALS_EXCEPTION_CLASS = VisionAPIMissingCredentialsError
    SEND_MUTABLE_STATUSES = VISION_SEND_MUTABLE_STATUSES

    def __init__(self) -> None:
        super().__init__()
        self.token_url = build_url(self.api_url, "v1/OAuthService/GenerateToken")
        self.payment_plan_creation_url = build_url(self.api_url, "ps/ezcash/PaymentPlan")
        # TODO: confirm the exact closure endpoint name with the Vision team
        # (currently assumed to be ps/ezcash/PaymentPlanClosure, mirroring PaymentPlan).
        self.payment_plan_closure_url = build_url(self.api_url, "ps/ezcash/PaymentPlanClosure")
        self._token_expiry: datetime | None = None

    def _acquire_token(self) -> None:
        """Exchange the client credentials for an OAuth bearer token and cache it on the session.

        Post only to the OAuth token endpoint (``token_url``), never to the Payment Plan or
        Payment Plan closure endpoints. Store the token on the shared HTTP session, together with
        its (timezone-aware) expiry, so subsequent calls reuse it until shortly before it lapses.
        Raise ``VisionAPIMissingCredentialsError`` when credentials are not configured and
        ``VisionAPIError`` when Vision rejects the request or returns a malformed token response.
        """
        client_id = settings.VISION_CLIENT_ID
        client_secret = settings.VISION_CLIENT_SECRET
        grant_type = settings.VISION_TOKEN_GRANT_TYPE

        if not client_id or not client_secret:
            raise VisionAPIMissingCredentialsError("Missing Vision OAuth credentials")

        # Use the shared session so token requests get the same connection pooling and retries
        # (502/503/504) as the API calls that follow.
        response = self._client.post(
            self.token_url,
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": grant_type,
            },
            timeout=settings.VISION_DEFAULT_TIMEOUT,
        )

        try:
            data = response.json()
        except ValueError as error:
            raise VisionAPIError(f"Vision OAuth token response was not valid JSON: {response.text!r}") from error

        if response.status_code == 401:
            raise VisionAPIError(f"Vision OAuth authentication failed: {data}")
        self.validate_response(response)

        access_token = data.get("access_token") if isinstance(data, dict) else None
        if not access_token:
            raise VisionAPIError("Vision OAuth token response did not contain an access token")
        try:
            expires_in = int(data.get("expires_in", DEFAULT_TOKEN_LIFETIME_SECONDS))
        except (TypeError, ValueError) as error:
            raise VisionAPIError("Vision OAuth token response contained an invalid expires_in value") from error

        self._client.headers["Authorization"] = f"Bearer {access_token}"
        # Clamp at zero: a lifetime shorter than the safety buffer must expire immediately
        # rather than in the past.
        lifetime_seconds = max(expires_in - TOKEN_EXPIRY_BUFFER_SECONDS, 0)
        self._token_expiry = timezone.now() + timedelta(seconds=lifetime_seconds)

    def _ensure_token(self) -> None:
        """Acquire a token unless a previously acquired one is still valid."""
        if not self._token_expiry or timezone.now() >= self._token_expiry:
            self._acquire_token()

    @classmethod
    def _persist_result(
        cls,
        payment_plan: PaymentPlan,
        entry: dict,
        vision_status: VisionStatus | None = None,
        *,
        initial_request_succeeded: bool = False,
    ) -> None:
        with transaction.atomic():
            locked_payment_plan = PaymentPlan.objects.select_for_update().get(pk=payment_plan.pk)
            vision_data = VisionService.vision_data(locked_payment_plan)
            vision_data.setdefault("log", []).append(entry)

            current_status = str(vision_data.get("status") or VisionStatus.NOT_SENT.value)
            plan_is_still_in_review = locked_payment_plan.status == PaymentPlan.Status.IN_REVIEW
            vision_attempt_has_not_been_reset = current_status != VisionStatus.NOT_SENT.value
            send_result_updates_status = vision_status is not None
            current_status_can_be_changed_by_send_result = current_status in cls.SEND_MUTABLE_STATUSES

            # Normally the attempt is WAITING_FOR_CALLBACK when the initial request succeeds. A fast callback may have
            # already changed it to an FC result; that is still the same active attempt and must be marked as sent.
            # NOT_SENT or a plan outside IN_REVIEW means that the attempt was reset or completed, so a late response
            # from the old request must not reactivate it.
            if (
                # The initial POST to Vision returned successfully.
                initial_request_succeeded
                # The plan has not been released, rejected, or aborted.
                and plan_is_still_in_review
                # The Vision attempt was not reset while the request was running.
                and vision_attempt_has_not_been_reset
            ):
                vision_data["sent"] = True

            if (
                # Initial sends and retries provide a local status to record; status notifications do not.
                send_result_updates_status
                # A late HTTP response must not change an aborted, rejected, or released plan.
                and plan_is_still_in_review
                # Preserve a newer callback status such as PP_CREATED, FC_NOT_FOUND, or CALLBACK_FAILED.
                and current_status_can_be_changed_by_send_result
            ):
                VisionService.set_status(locked_payment_plan, cast("VisionStatus", vision_status))

            PaymentPlan.objects.filter(pk=locked_payment_plan.pk).update(
                internal_data=locked_payment_plan.internal_data
            )

    def _post_payment_plan(
        self,
        payment_plan: PaymentPlan,
        payload: dict,
        log_entry_type: VisionLogEntryType,
        *,
        url: str | None = None,
    ) -> dict:
        is_initial_send = log_entry_type == VisionLogEntryType.API_CALL
        success_status = VisionStatus.WAITING_FOR_CALLBACK if is_initial_send else None
        failure_status = VisionStatus.SEND_FAILED if is_initial_send else None
        entry = {
            "timestamp": timezone.now().isoformat(),
            "type": log_entry_type.value,
            "payload": {key: str(value) for key, value in payload.items()},
            "response": {},
        }
        try:
            self._ensure_token()
            response, _ = self._post(url or self.payment_plan_creation_url, payload)
            entry["response"] = response
        except VisionAPIMissingCredentialsError:
            entry["response"] = {"error": "Vision API credentials are not configured"}
            self._persist_result(payment_plan, entry, failure_status)
            raise
        except (BaseAPI.APIError, VisionAPIError, requests.RequestException) as error:
            entry["response"] = {"error": str(error)}
            self._persist_result(payment_plan, entry, failure_status)
            raise VisionAPIError(str(error)) from error

        self._persist_result(
            payment_plan,
            entry,
            success_status,
            initial_request_succeeded=is_initial_send,
        )
        return response

    def send_payment_plan(self, payment_plan: PaymentPlan) -> dict:
        if getattr(payment_plan, "sent_to_vision", False) is True:
            raise VisionAPIError("Payment plan has already been sent to Vision")

        return self._post_payment_plan(
            payment_plan,
            dict(PaymentPlanPayloadSerializer(payment_plan).data),
            VisionLogEntryType.API_CALL,
        )

    def notify_payment_plan_status(self, payment_plan: PaymentPlan, vision_status: str) -> dict:
        payload = dict(PaymentPlanPayloadSerializer(payment_plan).data)
        payload["status"] = vision_status
        return self._post_payment_plan(payment_plan, payload, VisionLogEntryType.STATUS_NOTIFICATION)

    def notify_payment_plan_closure(
        self,
        payment_plan: PaymentPlan,
        *,
        total_amount_reconciled: Any,
        closure_date: Any,
    ) -> dict:
        """Post the closure reconciliation to Vision's PaymentPlanClosure endpoint.

        Send the Payment Plan code (``payplanSno``), the Vision Payment Plan code
        (``visionPayplanSno``), the total amount reconciled (``totalAmountReconciled``), and the
        closure date (``closureDate``). The attempt, including its response, is logged under the
        plan's Vision log in ``internal_data``; a failure raises and never changes Vision status.
        """
        vision_data = payment_plan.vision_data if hasattr(payment_plan, "vision_data") else {}
        vision_payment_plan_id = ""
        if isinstance(vision_data, dict):
            vision_payment_plan_id = str(vision_data.get("vision_id") or "")
        # Total delivered quantity is a Decimal, which is not JSON-serializable by the
        # underlying requests client; Vision expects it as a string, like authAmt.
        normalized_total_amount_reconciled = "" if total_amount_reconciled is None else str(total_amount_reconciled)
        payload = {
            "payplanSno": payment_plan.unicef_id,
            "visionPayplanSno": vision_payment_plan_id,
            "totalAmountReconciled": normalized_total_amount_reconciled,
            "closureDate": normalize_date(closure_date),
        }
        return self._post_payment_plan(
            payment_plan,
            payload,
            VisionLogEntryType.CLOSURE_NOTIFICATION,
            url=self.payment_plan_closure_url,
        )
