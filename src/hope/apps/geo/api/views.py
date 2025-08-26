import logging
from typing import Any

from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from hope.api.caches import etag_decorator
from hope.apps.account.permissions import Permissions
from hope.apps.core.api.mixins import BaseViewSet, BusinessAreaMixin, PermissionsMixin
from hope.apps.geo.api.caches import AreaKeyConstructor
from hope.apps.geo.api.filters import AreaFilter
from hope.apps.geo.api.serializers import AreaListSerializer, AreaTreeSerializer
from hope.models.geo import Area

logger = logging.getLogger(__name__)


class AreaViewSet(
    BusinessAreaMixin,
    PermissionsMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = Area.objects.all().order_by("area_type__area_level", "name")
    business_area_model_field = "area_type__country__business_areas"
    serializer_class = AreaListSerializer
    PERMISSIONS = [Permissions.GEO_VIEW_LIST]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = AreaFilter

    @etag_decorator(AreaKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=AreaKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: AreaTreeSerializer(many=True),
        },
    )
    @action(detail=False, methods=["get"], url_path="all-areas-tree")
    def all_areas_tree(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # get Area max level 3
        queryset = (
            Area.objects.filter(
                area_type__country__business_areas=self.business_area,
                area_type__area_level__lte=3,
            )
            .select_related("area_type", "area_type__country")
            .prefetch_related("area_type__country__business_areas")
        )
        return Response(AreaTreeSerializer(queryset.get_cached_trees(), many=True).data, status=200)
