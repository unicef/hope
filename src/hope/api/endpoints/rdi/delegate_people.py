from functools import reduce
from operator import or_
from typing import TYPE_CHECKING
from uuid import UUID

from django.db import transaction
from django.db.models import Q
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

    def validate_delegates(self, delegates: list[dict]) -> list[dict]:
        """Reject a delegate from outside this import before any role is reassigned."""
        rdi = self.context["registration_data_import"]
        delegate_ids = {delegate["delegate_id"] for delegate in delegates}
        ids_in_import = set(
            PendingIndividual.objects.filter(id__in=delegate_ids, registration_data_import=rdi).values_list(
                "id", flat=True
            )
        )
        for delegate_id in delegate_ids - ids_in_import:
            raise serializers.ValidationError(f"Delegate {delegate_id} does not belong to this import.")
        return delegates

    @transaction.atomic
    def create(self, validated_data: dict) -> dict:
        rdi = self.context["registration_data_import"]
        delegates = validated_data.pop("delegates")
        updated = 0
        for delegate in delegates:
            # one update per delegate: a role qualifies when its holder is delegated for and lives in the household
            in_own_household = reduce(
                or_, (Q(individual_id=i, household__individuals=i) for i in delegate["delegated_for"])
            )
            updated += PendingIndividualRoleInHousehold.objects.filter(
                in_own_household,
                household__registration_data_import=rdi,
                role=ROLE_PRIMARY,
            ).update(individual_id=delegate["delegate_id"])
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
