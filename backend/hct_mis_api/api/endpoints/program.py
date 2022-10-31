from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response

from hct_mis_api.api.endpoints.base import HOPEAPIBusinessAreaViewSet
from hct_mis_api.api.models import Grant
from hct_mis_api.apps.program.models import Program


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
        )


class ProgramViewSet(CreateModelMixin, HOPEAPIBusinessAreaViewSet):
    serializer = ProgramSerializer
    model = Program
    permission = Grant.API_PROGRAM_CREATE

    def perform_create(self, serializer) -> None:
        serializer.save(business_area=self.selected_business_area)

    @swagger_auto_schema(request_body=ProgramSerializer)
    def create(self, request, *args, **kwargs) -> Response:
        self.selected_business_area
        serializer = ProgramSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST, headers=headers)
