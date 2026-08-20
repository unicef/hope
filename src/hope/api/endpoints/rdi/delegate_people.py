from typing import TYPE_CHECKING
from uuid import UUID

from django.http.response import Http404
from django.utils.functional import cached_property
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.response import Response

from hope.api.endpoints.base import HOPEAPIBusinessAreaView, HOPEAPIView
from hope.apps.household.const import ROLE_PRIMARY
from hope.models import Grant, PendingIndividual, PendingIndividualRoleInHousehold, RegistrationDataImport

if TYPE_CHECKING:
    from rest_framework.request import Request


class DelegateSerializer(serializers.Serializer):
    delegate_id = serializers.UUIDField(required=True)
    delegated_for = serializers.ListField(child=serializers.UUIDField(required=True), allow_empty=False, required=True)


class DelegatePeopleSerializer(serializers.Serializer):
    delegates = DelegateSerializer(many=True, required=True, allow_empty=False, allow_null=False)

    def create(self, validated_data: dict) -> dict:
        rdi = self.context["registration_data_import"]
        delegates = validated_data.pop("delegates")
        updated = 0
        for delegate in delegates:
            delegate_id = delegate["delegate_id"]
            delegated_for = delegate["delegated_for"]
            if not PendingIndividual.objects.filter(id=delegate_id, registration_data_import=rdi).exists():
                raise serializers.ValidationError(f"Delegate {delegate_id} does not belong to this import.")
            for delegated_for_id in delegated_for:
                updated += PendingIndividualRoleInHousehold.objects.filter(
                    household__registration_data_import=rdi,
                    household__individuals__in=[delegated_for_id],
                    individual_id=delegated_for_id,
                    role=ROLE_PRIMARY,
                ).update(individual_id=delegate_id)
        return {"updated": updated}


class DelegatePeopleRDIView(HOPEAPIBusinessAreaView, HOPEAPIView):
    permission = Grant.API_RDI_UPLOAD

    @cached_property
    def selected_rdi(self) -> RegistrationDataImport:
        try:
            return RegistrationDataImport.objects.get(
                id=self.kwargs["rdi"],
                business_area__slug=self.kwargs["business_area"],
            )
        except RegistrationDataImport.DoesNotExist:
            raise Http404

    @extend_schema(request=DelegatePeopleSerializer)
    def post(self, request: "Request", business_area: str, rdi: UUID) -> Response:
        serializer = DelegatePeopleSerializer(
            data=request.data, context={"registration_data_import": self.selected_rdi}
        )
        if serializer.is_valid():
            response = serializer.save()
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
