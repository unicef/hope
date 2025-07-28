from typing import TYPE_CHECKING, Any

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from hct_mis_api.api.endpoints.base import HOPEAPIView
from hct_mis_api.api.endpoints.serializers import (
    CountrySerializer,
    FinancialInstitutionListSerializer,
)
from hct_mis_api.api.filters import CountryFilter, FinancialInstitutionFilter
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_CHOICE,
    MARITAL_STATUS_CHOICE,
    OBSERVED_DISABILITY_CHOICE,
    RELATIONSHIP_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    ROLE_CHOICE,
    SEX_CHOICE,
)
from hct_mis_api.apps.payment.models import FinancialInstitution
from hct_mis_api.apps.program.models import Program

if TYPE_CHECKING:
    from rest_framework.request import Request


class DocumentType(HOPEAPIView):
    def get(self, request: "Request", format: Any | None = None) -> Response:
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
    def get(self, request: "Request", format: Any | None = None) -> Response:
        return Response(dict(RESIDENCE_STATUS_CHOICE))


class MaritalStatus(HOPEAPIView):
    def get(self, request: "Request", format: Any | None = None) -> Response:
        return Response(dict(MARITAL_STATUS_CHOICE))


class ObservedDisability(HOPEAPIView):
    def get(self, request: "Request", format: Any | None = None) -> Response:
        return Response(dict(OBSERVED_DISABILITY_CHOICE))


class Relationship(HOPEAPIView):
    def get(self, request: "Request", format: Any | None = None) -> Response:
        return Response(dict(RELATIONSHIP_CHOICE))


class Roles(HOPEAPIView):
    def get(self, request: "Request", format: Any | None = None) -> Response:
        return Response(dict(ROLE_CHOICE))


class Sex(HOPEAPIView):
    def get(self, request: "Request", format: Any | None = None) -> Response:
        return Response(dict(SEX_CHOICE))


class Sector(HOPEAPIView):
    def get(self, request: "Request", format: Any | None = None) -> Response:
        return Response(dict(Program.SECTOR_CHOICE))


class FrequencyOfPayments(HOPEAPIView):
    def get(self, request: "Request", format: Any | None = None) -> Response:
        return Response(dict(Program.FREQUENCY_OF_PAYMENTS_CHOICE))


class ProgramScope(HOPEAPIView):
    def get(self, request: "Request", format: Any | None = None) -> Response:
        return Response(dict(Program.SCOPE_CHOICE))


class ProgramStatuses(HOPEAPIView):
    def get(self, request: "Request", format: Any | None = None) -> Response:
        return Response(dict(Program.STATUS_CHOICE))
