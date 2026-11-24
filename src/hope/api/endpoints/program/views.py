from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from hope.api.endpoints.base import HOPEAPIView
from hope.api.endpoints.program.filters import ProgramFilter
from hope.api.endpoints.program.serializers import ProgramGlobalSerializer
from hope.models import Program


class ProgramGlobalListView(HOPEAPIView, ListAPIView):
    serializer_class = ProgramGlobalSerializer
    queryset = Program.objects.select_related("data_collecting_type__payee_type", "business_area")
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = ProgramFilter
