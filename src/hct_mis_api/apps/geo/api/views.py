import logging
from typing import Any

from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from hct_mis_api.api.caches import etag_decorator
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.api.mixins import (
    BaseViewSet,
    BusinessAreaMixin,
    PermissionsMixin,
)
from hct_mis_api.apps.geo.api.caches import AreaKeyConstructor
from hct_mis_api.apps.geo.api.filters import AreaFilter
from hct_mis_api.apps.geo.api.serializers import AreaListSerializer
from hct_mis_api.apps.geo.models import Area

logger = logging.getLogger(__name__)


class AreaViewSet(
    BusinessAreaMixin,
    PermissionsMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = Area.objects.all()
    business_area_model_field = "area_type__country__business_areas"
    serializer_class = AreaListSerializer
    PERMISSIONS = [Permissions.GEO_VIEW_LIST]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = AreaFilter

    @etag_decorator(AreaKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=AreaKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
