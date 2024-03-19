from typing import Any, Dict
from uuid import UUID

from django.db.transaction import atomic

from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from hct_mis_api.api.endpoints.base import HOPEAPIBusinessAreaView, HOPEAPIView
from hct_mis_api.api.models import Grant
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.registration_datahub.models import (
    ImportedIndividualRoleInHousehold,
)


class DelegateSerializer(serializers.Serializer):
    delegate_id = serializers.UUIDField(required=True)
    delegated_for = serializers.ListField(child=serializers.UUIDField(required=True), allow_empty=False, required=True)


class DelegatePeopleSerializer(serializers.Serializer):
    delegates = DelegateSerializer(many=True, required=True)

    def validate_delegates(self, value: Any) -> Any:
        if not value:
            raise ValidationError("This field is required.")
        return value

    def create(self, validated_data: Dict) -> Dict:
        delegates = validated_data.pop("delegates")
        updated = 0
        for delegate in delegates:
            delegate_id = delegate["delegate_id"]
            delegated_for = delegate["delegated_for"]
            for delegated_for_id in delegated_for:
                updated += ImportedIndividualRoleInHousehold.objects.filter(
                    household__individuals__in=[delegated_for_id],
                    individual_id=delegated_for_id,
                    role=ROLE_PRIMARY,
                ).update(individual_id=delegate_id)
        return {"updated": updated}


class DelegatePeopleRDIView(HOPEAPIBusinessAreaView, HOPEAPIView):
    permission = Grant.API_RDI_UPLOAD

    @atomic(using="registration_datahub")
    def post(self, request: "Request", business_area: str, rdi: UUID) -> Response:
        serializer = DelegatePeopleSerializer(data=request.data)
        if serializer.is_valid():
            response = serializer.save()
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
