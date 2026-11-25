from typing import Any

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from hope.api.auth import HOPEAuthentication
from hope.api.endpoints.base import HOPEAPIView
from hope.apps.account.actor_snapshot import ActorSnapshot, build_actor_snapshot
from hope.contrib.api.serializers.vision import (
    PaymentPlanCallbackAckSerializer,
    PaymentPlanCallbackRequestSerializer,
)
from hope.contrib.vision.choices import VISION_SUCCESSFUL_CALLBACK_RESULTS, VisionLogEntryType, VisionStatus
from hope.contrib.vision.services import VisionService
from hope.models import Grant, PaymentPlan

VISION_RESPONSE_OK = "OK"
VISION_RESPONSE_KO = "KO"
VISION_CALLBACK_RECEIVED_MESSAGE = "Callback received"
VISION_INVALID_CALLBACK_MESSAGE = "Invalid callback payload"
VISION_PAYMENT_PLAN_NOT_FOUND_MESSAGE = "Payment plan not found"
VISION_PAYPLAN_ID_MISSING_MESSAGE = "vision_payplanSno is required"


class PaymentPlanCallbackView(HOPEAPIView, APIView):
    authentication_classes = [HOPEAuthentication]
    permission = Grant.API_VISION_PP_CREATE

    @staticmethod
    def _build_response(
        vision_status: str,
        serializer: PaymentPlanCallbackRequestSerializer,
        *,
        message: str,
    ) -> dict[str, str]:
        return dict(PaymentPlanCallbackAckSerializer(serializer.ack_payload(vision_status, message=message)).data)

    @staticmethod
    def _error_response(
        serializer: PaymentPlanCallbackRequestSerializer,
        *,
        message: str,
        http_status: int = status.HTTP_400_BAD_REQUEST,
    ) -> Response:
        return Response(
            PaymentPlanCallbackView._build_response(VISION_RESPONSE_KO, serializer, message=message),
            status=http_status,
        )

    @staticmethod
    def _get_payment_plan(payplan_sno: str) -> PaymentPlan:
        return (
            PaymentPlan.objects.select_for_update()
            .select_related("business_area", "created_by")
            .get(unicef_id=payplan_sno)
        )

    @staticmethod
    def _release_actor_snapshot(serializer: PaymentPlanCallbackRequestSerializer) -> ActorSnapshot | None:
        """Return the name and AD job title of the plan creator for the release this callback will trigger.

        A successful callback with FC numbers releases the plan and records a FINANCE_RELEASE Approval for its
        creator. The AD lookup for that record is done here, before `post` locks the Payment Plan row.
        Any other callback, an unknown plan, or a plan the callback cannot release returns None.
        """
        if (
            serializer.validated_data.get("status") not in VISION_SUCCESSFUL_CALLBACK_RESULTS
            or not serializer.validated_data.get("fc_numbers")
            or not serializer.validated_vision_payplan_sno
        ):
            return None
        payment_plan = (
            PaymentPlan.objects.select_related("business_area", "created_by")
            .filter(unicef_id=serializer.validated_payplan_sno)
            .first()
        )
        if payment_plan is None or not VisionService.can_recover_with_funds_commitment_headers(payment_plan):
            return None
        return build_actor_snapshot(payment_plan.created_by)

    @staticmethod
    def _append_log(payment_plan: Any, payload: dict, response_data: dict) -> None:
        vision_data = payment_plan.internal_data.setdefault("vision", {})
        vision_data.setdefault("log", []).append(
            {
                "timestamp": timezone.now().isoformat(),
                "type": VisionLogEntryType.PUSH_NOTIFICATION.value,
                "payload": payload,
                "response": dict(response_data),
            }
        )

    @transaction.atomic
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = PaymentPlanCallbackRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return self._error_response(serializer, message=VISION_INVALID_CALLBACK_MESSAGE)

        actor_snapshot = self._release_actor_snapshot(serializer)
        try:
            payment_plan = self._get_payment_plan(serializer.validated_payplan_sno)
        except PaymentPlan.DoesNotExist:
            return self._error_response(
                serializer,
                message=VISION_PAYMENT_PLAN_NOT_FOUND_MESSAGE,
                http_status=status.HTTP_404_NOT_FOUND,
            )

        if not serializer.validated_vision_payplan_sno:
            response_data = self._build_response(
                VISION_RESPONSE_KO,
                serializer,
                message=VISION_PAYPLAN_ID_MISSING_MESSAGE,
            )
            self._append_log(payment_plan, serializer.external_payload, response_data)
            missing_id_failure_statuses = {
                VisionStatus.WAITING_FOR_CALLBACK.value,
                VisionStatus.PP_CREATED.value,
            }
            if (
                payment_plan.status == PaymentPlan.Status.IN_REVIEW
                and payment_plan.vision_integration_enabled
                and payment_plan.vision_status in missing_id_failure_statuses
            ):
                VisionService.set_status(payment_plan, VisionStatus.CALLBACK_FAILED)
            payment_plan.save(update_fields=["internal_data"])
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        VisionService.process_callback(
            payment_plan,
            vision_payment_plan_id=serializer.validated_vision_payplan_sno,
            vision_result=serializer.validated_data.get("status", ""),
            fc_numbers=serializer.validated_data.get("fc_numbers", []),
            actor_snapshot=actor_snapshot,
        )
        response_data = self._build_response(
            VISION_RESPONSE_OK,
            serializer,
            message=VISION_CALLBACK_RECEIVED_MESSAGE,
        )

        self._append_log(payment_plan, serializer.external_payload, response_data)

        payment_plan.save(update_fields=["internal_data"])

        return Response(response_data, status=status.HTTP_200_OK)
