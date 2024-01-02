from typing import TYPE_CHECKING

from django.db.transaction import atomic

import requests
from constance import config
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from hct_mis_api.api.endpoints.base import HOPEAPIView
from hct_mis_api.api.utils import humanize_errors
from hct_mis_api.payment.serializers import PaymentInstructionSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


class GatewayAPIView(APIView):
    authentication_classes = []
    permission_classes = []


class CreatePaymentInstruction(GatewayAPIView):
    @atomic()
    def post(self, request: "Request") -> Response:
        data = request.data
        serializer = PaymentInstructionSerializer(data=data)
        if serializer.is_valid():
            endpoint = "api/rest/payment_instructions"
            url = f"{config.GATEWAY_SERVER}{endpoint}"
            headers = {"Authorization": f"Token {config.GATEWAY_TOKEN}"}
            response = requests.post(url=url, data=data, headers=headers)
            if 200 <= response.status_code < 300:
                return Response(response, status=status.HTTP_201_CREATED)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        errors = humanize_errors(serializer.errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeStatusPaymentInstruction(HOPEAPIView):
    pass


class SendRecordsToChangeStatusPaymentInstruction(HOPEAPIView):
    pass
