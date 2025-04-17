import logging
from typing import Any

from django.db.models import QuerySet

from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_extensions.cache.decorators import cache_response

from hct_mis_api.api.caches import etag_decorator
from hct_mis_api.apps.account.api.permissions import GeoViewListPermission
from hct_mis_api.apps.core.api.mixins import BusinessAreaMixin, PermissionsMixin
from hct_mis_api.apps.geo.api.caches import AreaKeyConstructor
from hct_mis_api.apps.geo.api.filters import AreaFilter
from hct_mis_api.apps.geo.api.serializers import AreaListSerializer
from hct_mis_api.apps.geo.models import Area

logger = logging.getLogger(__name__)


class AreaViewSet(
    BusinessAreaMixin,
    PermissionsMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_class = AreaListSerializer
    permission_classes = [GeoViewListPermission]  # type: ignore
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = AreaFilter

    def get_queryset(self) -> QuerySet:
        business_area = self.get_business_area()
        return Area.objects.filter(area_type__country__business_areas=business_area)

    @etag_decorator(AreaKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=AreaKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
