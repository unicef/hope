from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from hope.api.auth import HOPEAuthentication
from hope.api.endpoints.base import HOPEAPIView
from hope.models import Grant, PaymentPlan

VISION_PAYMENT_PLAN_STATUS_SUCCESS = "SUCCESS"


class PaymentPlanCallbackView(HOPEAPIView, APIView):
    authentication_classes = [HOPEAuthentication]
    permission = Grant.API_VISION_PP_CREATE

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            message_id = request.data.get("messageId", "")

            if not (payplan_sno := request.data.get("payplanSno")):
                return Response(
                    {"status": "KO", "messageId": message_id, "payplanSno": ""},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            payment_plan = PaymentPlan.objects.get(unicef_id=payplan_sno)

            if not (vision_payplan_sno := request.data.get("vision_payplanSno")):
                return Response(
                    {
                        "status": "KO",
                        "messageId": message_id,
                        "payplanSno": payplan_sno,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response_data = {
                "status": "OK",
                "messageId": message_id,
                "payplanSno": payplan_sno,
            }

            vision_log = payment_plan.internal_data.setdefault("vision", [])
            vision_log.append({"payload": dict(request.data), "response": dict(response_data)})

            if request.data.get("status") == VISION_PAYMENT_PLAN_STATUS_SUCCESS:
                payment_plan.internal_data["vision_id"] = vision_payplan_sno
                if fc_num := request.data.get("fc_num"):
                    payment_plan.internal_data["fc_num"] = fc_num

            payment_plan.save(update_fields=["internal_data"])

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception:  # noqa: BLE001
            return Response(
                {
                    "status": "KO",
                    "messageId": request.data.get("messageId", ""),
                    "payplanSno": request.data.get("payplanSno", ""),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
