from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from hope.api.endpoints.base import HOPEAPIView
from hope.api.endpoints.core.filters import BusinessAreaFilter
from hope.api.endpoints.core.serializers import BusinessAreaSerializer
from hope.apps.core.models import BusinessArea


class BusinessAreaListView(HOPEAPIView, ListAPIView):
    serializer_class = BusinessAreaSerializer
    queryset = BusinessArea.objects.all()
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = BusinessAreaFilter
