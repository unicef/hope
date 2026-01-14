from typing import Any

from django.db import transaction
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from hope.api.endpoints.base import HOPEAPIBusinessAreaView
from hope.api.endpoints.beneficiary_ticket.serializers import (
    BeneficiaryTicketCreateSerializer,
    BeneficiaryTicketResponseSerializer,
)
from hope.apps.grievance.constants import PRIORITY_NOT_SET, URGENCY_NOT_SET
from hope.apps.grievance.models import GrievanceTicket
from hope.models.grant import Grant


class CreateBeneficiaryTicketView(HOPEAPIBusinessAreaView, CreateAPIView):
    permission = Grant.API_BENEFICIARY_TICKET_CREATE
    serializer_class = BeneficiaryTicketCreateSerializer

    @transaction.atomic()
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        ticket = GrievanceTicket.objects.create(
            business_area=self.selected_business_area,
            category=GrievanceTicket.CATEGORY_BENEFICIARY,
            description=validated_data["description"],
            priority=validated_data.get("priority", PRIORITY_NOT_SET),
            urgency=validated_data.get("urgency", URGENCY_NOT_SET),
            assigned_to=validated_data.get("assigned_to"),
            consent=True,
            status=GrievanceTicket.STATUS_NEW,
        )

        program = validated_data.get("program")
        if program:
            ticket.programs.add(program)

        response_serializer = BeneficiaryTicketResponseSerializer(ticket)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
