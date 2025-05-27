from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from hct_mis_api.api.endpoints.base import HOPEAPIView
from hct_mis_api.api.endpoints.program.filters import ProgramFilter
from hct_mis_api.api.endpoints.program.serializers import \
    ProgramGlobalSerializer
from hct_mis_api.apps.program.models import Program


class ProgramGlobalListView(HOPEAPIView, ListAPIView):
    serializer_class = ProgramGlobalSerializer
    queryset = Program.objects.all()
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = ProgramFilter
