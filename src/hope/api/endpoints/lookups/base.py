from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from hope.api.endpoints.base import HOPEAPIView
from hope.api.endpoints.serializers import (
    CountrySerializer,
    FinancialInstitutionListSerializer,
)
from hope.api.filters import CountryFilter, FinancialInstitutionFilter
from hope.models.country import Country
from hope.models.household import (
    IDENTIFICATION_TYPE_CHOICE,
    MARITAL_STATUS_CHOICE,
    OBSERVED_DISABILITY_CHOICE,
    RELATIONSHIP_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    ROLE_CHOICE,
    SEX_CHOICE,
)
from hope.models.financial_institution import FinancialInstitution
from hope.models.program import Program


class DocumentType(HOPEAPIView):
    def get(self, request: "Request", **kwargs) -> Response:
        return Response(dict(IDENTIFICATION_TYPE_CHOICE))


class CountryAPIView(HOPEAPIView, ListAPIView):
    queryset = Country.objects.all().order_by("name")
    serializer_class = CountrySerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend, SearchFilter)
    filterset_class = CountryFilter
    search_fields = (
        "iso_code2",
        "iso_code3",
        "name",
        "short_name",
        "iso_num",
    )


class FinancialInstitutionAPIView(HOPEAPIView, ListAPIView):
    queryset = FinancialInstitution.objects.select_related("country").order_by("name")
    serializer_class = FinancialInstitutionListSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = FinancialInstitutionFilter


class ResidenceStatus(HOPEAPIView):
    def get(self, request: "Request", **kwargs) -> Response:
        return Response(dict(RESIDENCE_STATUS_CHOICE))


class MaritalStatus(HOPEAPIView):
    def get(self, request: "Request", **kwargs) -> Response:
        return Response(dict(MARITAL_STATUS_CHOICE))


class ObservedDisability(HOPEAPIView):
    def get(self, request: "Request", **kwargs) -> Response:
        return Response(dict(OBSERVED_DISABILITY_CHOICE))


class Relationship(HOPEAPIView):
    def get(self, request: "Request", **kwargs) -> Response:
        return Response(dict(RELATIONSHIP_CHOICE))


class Roles(HOPEAPIView):
    def get(self, request: "Request", **kwargs) -> Response:
        return Response(dict(ROLE_CHOICE))


class Sex(HOPEAPIView):
    def get(self, request: "Request", **kwargs) -> Response:
        return Response(dict(SEX_CHOICE))


class Sector(HOPEAPIView):
    def get(self, request: "Request", **kwargs) -> Response:
        return Response(dict(Program.SECTOR_CHOICE))


class FrequencyOfPayments(HOPEAPIView):
    def get(self, request: "Request", **kwargs) -> Response:
        return Response(dict(Program.FREQUENCY_OF_PAYMENTS_CHOICE))


class ProgramScope(HOPEAPIView):
    def get(self, request: "Request", **kwargs) -> Response:
        return Response(dict(Program.SCOPE_CHOICE))


class ProgramStatuses(HOPEAPIView):
    def get(self, request: "Request", **kwargs) -> Response:
        return Response(dict(Program.STATUS_CHOICE))
