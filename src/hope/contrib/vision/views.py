from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from hope.api.auth import HOPEAuthentication
from hope.api.endpoints.base import HOPEAPIView
from hope.contrib.api.serializers.vision import (
    PaymentPlanCallbackRequestSerializer,
    PaymentPlanCallbackResponseSerializer,
)
from hope.models import Grant, PaymentPlan

VISION_RESPONSE_OK = "OK"
VISION_RESPONSE_KO = "KO"
VISION_PAYMENT_PLAN_STATUS_SUCCESS = "SUCCESS"


class PaymentPlanCallbackView(HOPEAPIView, APIView):
    authentication_classes = [HOPEAuthentication]
    permission = Grant.API_VISION_PP_CREATE

    @staticmethod
    def _build_response(status_: str, message_id: str, payplan_sno: str) -> dict[str, str]:
        return dict(
            PaymentPlanCallbackResponseSerializer(
                {"status": status_, "message_id": message_id, "payplan_sno": payplan_sno}
            ).data
        )

    @staticmethod
    def _error_response(message_id: str, payplan_sno: str) -> Response:
        return Response(
            PaymentPlanCallbackView._build_response(VISION_RESPONSE_KO, message_id, payplan_sno),
            status=status.HTTP_400_BAD_REQUEST,
        )

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = PaymentPlanCallbackRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return self._error_response(serializer.initial_message_id, serializer.initial_payplan_sno)

        try:
            payment_plan = PaymentPlan.objects.get(unicef_id=serializer.validated_payplan_sno)
        except PaymentPlan.DoesNotExist:
            return self._error_response(serializer.validated_message_id, serializer.validated_payplan_sno)

        response_data = self._build_response(
            VISION_RESPONSE_OK,
            serializer.validated_message_id,
            serializer.validated_payplan_sno,
        )
        vision_data = payment_plan.internal_data.setdefault("vision", {})
        vision_data.setdefault("callback_log", []).append(
            {
                "payload": serializer.external_payload,
                "response": dict(response_data),
            }
        )

        if serializer.validated_data.get("status") == VISION_PAYMENT_PLAN_STATUS_SUCCESS:
            vision_data["vision_id"] = serializer.validated_vision_payplan_sno
            if fc_num := serializer.validated_data.get("fc_num"):
                vision_data["fc_num"] = fc_num

        payment_plan.save(update_fields=["internal_data"])

        return Response(response_data, status=status.HTTP_200_OK)
