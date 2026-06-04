from typing import Any

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from hope.api.endpoints.base import HOPEAPIView
from hope.contrib.api.serializers.vision import PaymentPlanCallbackSerializer
from hope.models.grant import Grant


class PaymentPlanCallbackView(HOPEAPIView, CreateAPIView):
    permission = Grant.API_VISION_PAYMENTPLAN
    serializer_class = PaymentPlanCallbackSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"status": "ok"}, status=status.HTTP_200_OK)
