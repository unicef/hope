from typing import Any

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from hope.api.auth import HOPEAuthentication
from hope.api.endpoints.base import HOPEAPIView
from hope.contrib.api.serializers.vision import (
    PaymentPlanCallbackAckSerializer,
    PaymentPlanCallbackRequestSerializer,
)
from hope.contrib.vision.choices import VisionLogEntryType, VisionStatus
from hope.contrib.vision.services import VisionService
from hope.models import Grant, PaymentPlan

VISION_RESPONSE_OK = "OK"
VISION_RESPONSE_KO = "KO"


class PaymentPlanCallbackView(HOPEAPIView, APIView):
    authentication_classes = [HOPEAuthentication]
    permission = Grant.API_VISION_PP_CREATE

    @staticmethod
    def _build_response(vision_status: str, serializer: PaymentPlanCallbackRequestSerializer) -> dict[str, str]:
        return dict(PaymentPlanCallbackAckSerializer(serializer.ack_payload(vision_status)).data)

    @staticmethod
    def _error_response(serializer: PaymentPlanCallbackRequestSerializer) -> Response:
        return Response(
            PaymentPlanCallbackView._build_response(VISION_RESPONSE_KO, serializer),
            status=status.HTTP_400_BAD_REQUEST,
        )

    @staticmethod
    def _get_payment_plan(payplan_sno: str) -> PaymentPlan:
        return (
            PaymentPlan.objects.select_for_update()
            .select_related("business_area", "created_by")
            .get(unicef_id=payplan_sno)
        )

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
            return self._error_response(serializer)

        try:
            payment_plan = self._get_payment_plan(serializer.validated_payplan_sno)
        except PaymentPlan.DoesNotExist:
            return self._error_response(serializer)

        if not serializer.validated_vision_payplan_sno:
            response_data = self._build_response(VISION_RESPONSE_KO, serializer)
            self._append_log(payment_plan, serializer.external_payload, response_data)
            if (
                payment_plan.vision_integration_enabled
                and payment_plan.vision_status == VisionStatus.WAITING_FOR_CALLBACK.value
            ):
                VisionService.set_status(payment_plan, VisionStatus.CALLBACK_FAILED)
            payment_plan.save(update_fields=["internal_data"])
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        response_data = self._build_response(VISION_RESPONSE_OK, serializer)
        self._append_log(payment_plan, serializer.external_payload, response_data)
        # TODO(Vision decision): Keep returning OK for a transport-valid callback even when FC assignment fails until
        # the business confirms whether missing, unknown, ambiguous, or conflicting FC data should return KO to Vision.
        VisionService.process_callback(
            payment_plan,
            vision_payment_plan_id=serializer.validated_vision_payplan_sno,
            vision_result=serializer.validated_data.get("status", ""),
            fc_num=serializer.validated_data.get("fc_num", ""),
        )

        payment_plan.save(update_fields=["internal_data"])

        return Response(response_data, status=status.HTTP_200_OK)
