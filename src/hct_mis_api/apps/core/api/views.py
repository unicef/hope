from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated

from hct_mis_api.apps.core.api.filters import BusinessAreaFilter
from hct_mis_api.apps.core.api.mixins import BaseViewSet
from hct_mis_api.apps.core.api.serializers import BusinessAreaSerializer
from hct_mis_api.apps.core.models import BusinessArea


class BusinessAreaViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    BaseViewSet,
):
    permission_classes = [IsAuthenticated]
    queryset = BusinessArea.objects.all()
    serializer_class = BusinessAreaSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = BusinessAreaFilter
    lookup_url_kwarg = "slug"
