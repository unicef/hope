from typing import TYPE_CHECKING, Any, Dict, List

from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, serializers, status
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response

from hct_mis_api.api.endpoints.base import HOPEAPIBusinessAreaViewSet
from hct_mis_api.api.models import Grant
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.models import Program

if TYPE_CHECKING:
    from rest_framework.request import Request


class DataCollectingTypeSerializer(serializers.ModelSerializer):
    limit_to = serializers.SerializerMethodField()

    class Meta:
        model = DataCollectingType
        fields = (
            "id",
            "label",
            "code",
            "description",
            "active",
            "individual_filters_available",
            "household_filters_available",
            "recalculate_composition",
            "compatible_types",
            "limit_to",
        )

    def get_limit_to(self, obj: DataCollectingType) -> List[str]:
        return list(obj.limit_to.all().values_list("slug", flat=True))


class DataCollectingTypeViewSet(mixins.ListModelMixin, HOPEAPIBusinessAreaViewSet):
    queryset = DataCollectingType.objects.all().order_by("code")
    serializer_class = DataCollectingTypeSerializer


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = (
            "id",
            "name",
            "start_date",
            "end_date",
            "budget",
            "frequency_of_payments",
            "sector",
            "cash_plus",
            "population_goal",
            "business_area",
            "data_collecting_type",
        )

    def validate_data_collecting_type(self, data_collecting_type: DataCollectingType) -> DataCollectingType:
        if data_collecting_type.code == "unknown":
            raise serializers.ValidationError("DataCollectingType does not exists or equals to unknown.")
        return data_collecting_type

    def to_representation(self, instance: Program) -> Dict:
        representation = super().to_representation(instance)
        representation["data_collecting_type"] = DataCollectingTypeSerializer(instance.data_collecting_type).data
        return representation


class ProgramViewSet(CreateModelMixin, ListModelMixin, HOPEAPIBusinessAreaViewSet):
    serializer_class = ProgramSerializer
    model = Program
    queryset = Program.objects.all()
    permission = Grant.API_PROGRAM_CREATE

    @swagger_auto_schema(request_body=ProgramSerializer)
    def create(self, request: "Request", *args: Any, **kwargs: Any) -> Response:
        business_area_slug = self.kwargs.get("business_area")  # we can get it from path variable
        business_area = get_object_or_404(BusinessArea, slug=business_area_slug)

        serializer = ProgramSerializer(data={**request.data, "business_area": str(business_area.id)})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
