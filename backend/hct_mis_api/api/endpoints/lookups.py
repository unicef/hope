from django_countries import Countries
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from hct_mis_api.api.endpoints.base import HOPEAPIView
from hct_mis_api.apps.household.models import (
    COLLECT_TYPES,
    IDENTIFICATION_TYPE_CHOICE,
    MARITAL_STATUS_CHOICE,
    OBSERVED_DISABILITY_CHOICE,
    RELATIONSHIP_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    ROLE_CHOICE,
)


class DocumentType(HOPEAPIView):
    def get(self, request, format=None):
        return Response(dict(IDENTIFICATION_TYPE_CHOICE))


class Country(HOPEAPIView):
    def get(self, request, format=None):
        return Response(dict(Countries()))


class ResidenceStatus(HOPEAPIView):
    def get(self, request, format=None):
        return Response(dict(RESIDENCE_STATUS_CHOICE))


class MaritalStatus(HOPEAPIView):
    def get(self, request, format=None):
        return Response(dict(MARITAL_STATUS_CHOICE))


class ObservedDisability(HOPEAPIView):
    def get(self, request, format=None):
        return Response(dict(OBSERVED_DISABILITY_CHOICE))


class Relationship(HOPEAPIView):
    def get(self, request, format=None):
        return Response(dict(RELATIONSHIP_CHOICE))


class DataCollectingPolicy(HOPEAPIView):
    def get(self, request, format=None):
        return Response(dict(COLLECT_TYPES))


class Roles(HOPEAPIView):
    def get(self, request, format=None):
        return Response(dict(ROLE_CHOICE))
