from dataclasses import asdict
from typing import Any, TYPE_CHECKING

from django.db.transaction import atomic
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from hct_mis_api.api.endpoints.base import HOPEAPIBusinessAreaView
from hct_mis_api.api.endpoints.rdi.mixin import HouseholdUploadMixin
from hct_mis_api.api.endpoints.rdi.serializers import HouseholdSerializer
from hct_mis_api.api.models import Grant
from hct_mis_api.api.utils import humanize_errors
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


if TYPE_CHECKING:
    from rest_framework.request import Request
    from hct_mis_api.apps.core.models import BusinessArea


class RDINestedSerializer(HouseholdUploadMixin, serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    households = HouseholdSerializer(many=True, required=True)
    program = serializers.SlugRelatedField(
        slug_field="id", required=True, queryset=Program.objects.all(), write_only=True
    )

    class Meta:
        model = RegistrationDataImport
        fields = ("name", "households", "program")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.business_area = kwargs.pop("business_area", None)
        super().__init__(*args, **kwargs)

    def validate_households(self, value: Any) -> Any:
        if not value:
            raise ValidationError("This field is required.")
        return value

    @atomic()
    def create(self, validated_data: dict) -> dict:
        created_by = validated_data.pop("user")
        households = validated_data.pop("households")
        program = validated_data.pop("program")

        rdi = RegistrationDataImport.objects.create(
            **validated_data,
            imported_by=created_by,
            data_source=RegistrationDataImport.API,
            number_of_individuals=0,
            number_of_households=0,
            business_area=self.business_area,
            program=program,
        )
        if program.biometric_deduplication_enabled:
            rdi.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_PENDING

        info = self.save_households(rdi, households)
        rdi.number_of_households = info.households
        rdi.number_of_individuals = info.individuals
        rdi.save()

        return dict(id=rdi.pk, name=rdi.name, **asdict(info))


class UploadRDIView(HOPEAPIBusinessAreaView):
    permission = Grant.API_RDI_UPLOAD

    @extend_schema(request=RDINestedSerializer)
    @atomic()
    def post(self, request: "Request", business_area: "BusinessArea") -> Response:
        serializer = RDINestedSerializer(data=request.data, business_area=self.selected_business_area)
        if serializer.is_valid():
            info = serializer.save(user=request.user)
            return Response(info, status=status.HTTP_201_CREATED)
        errors = humanize_errors(serializer.errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
