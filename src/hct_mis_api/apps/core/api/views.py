from typing import Any

from django.db.models import Q, QuerySet
from django.utils import timezone

from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from hct_mis_api.api.caches import etag_decorator
from hct_mis_api.apps.account.models import RoleAssignment
from hct_mis_api.apps.core.api.caches import BusinessAreaKeyConstructor
from hct_mis_api.apps.core.api.filters import BusinessAreaFilter
from hct_mis_api.apps.core.api.mixins import BaseViewSet, CountActionMixin
from hct_mis_api.apps.core.api.serializers import BusinessAreaSerializer
from hct_mis_api.apps.core.models import BusinessArea


class BusinessAreaViewSet(
    CountActionMixin,
    RetrieveModelMixin,
    ListModelMixin,
    BaseViewSet,
):
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessAreaSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = BusinessAreaFilter
    lookup_url_kwarg = "slug"

    def get_queryset(self) -> QuerySet[BusinessArea]:
        user = self.request.user
        role_assignments = RoleAssignment.objects.filter(Q(user=user) | Q(partner__user=user)).exclude(
            expiry_date__lt=timezone.now()
        )
        return BusinessArea.objects.filter(role_assignments__in=role_assignments).order_by("id").distinct()

    @etag_decorator(BusinessAreaKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=BusinessAreaKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
