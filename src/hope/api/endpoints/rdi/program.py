from typing import Any

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response

from hope.api.endpoints.base import HOPEAPIBusinessAreaViewSet
from hope.models.grant import Grant
from hope.apps.core.api.filters import UpdatedAtFilter
from hope.models.program import Program


class ProgramAPISerializer(serializers.ModelSerializer):
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
            "data_collecting_type",
            "beneficiary_group",
        )


class ProgramViewSet(CreateModelMixin, ListModelMixin, HOPEAPIBusinessAreaViewSet, GenericAPIView):
    serializer_class = ProgramAPISerializer
    permission = Grant.API_READ_ONLY
    queryset = Program.objects.all()
    pagination_class = None
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = UpdatedAtFilter

    def get_queryset(self) -> QuerySet:
        return self.queryset.filter(business_area=self.selected_business_area)

    def perform_create(self, serializer_class: "BaseSerializer") -> None:
        serializer_class.save(business_area=self.selected_business_area)

    @extend_schema(request=ProgramAPISerializer)
    def create(self, request: "Request", *args: Any, **kwargs: Any) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if Grant.API_PROGRAM_CREATE.name not in request.auth.grants:
            raise PermissionDenied()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
