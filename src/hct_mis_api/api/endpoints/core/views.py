from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from hct_mis_api.api.endpoints.base import HOPEAPIView
from hct_mis_api.api.endpoints.core.filters import BusinessAreaFilter
from hct_mis_api.api.endpoints.core.serializers import BusinessAreaSerializer
from hct_mis_api.apps.core.models import BusinessArea


class BusinessAreaListView(HOPEAPIView, ListAPIView):
    serializer_class = BusinessAreaSerializer
    queryset = BusinessArea.objects.all()
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = BusinessAreaFilter
