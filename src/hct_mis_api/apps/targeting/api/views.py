import logging
from typing import Any

from django.db.models import QuerySet

from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from hct_mis_api.api.caches import etag_decorator
from hct_mis_api.apps.account.api.permissions import HasOneOfPermissions
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.api.mixins import BaseViewSet, BusinessAreaProgramMixin
from hct_mis_api.apps.payment.api.filters import PaymentPlanFilter
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.targeting.api.caches import TPKeyConstructor
from hct_mis_api.apps.targeting.api.serializers import TargetPopulationListSerializer

logger = logging.getLogger(__name__)


class TargetPopulationViewSet(
    BusinessAreaProgramMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    serializer_class = TargetPopulationListSerializer
    PERMISSIONS = [Permissions.TARGETING_VIEW_LIST]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = PaymentPlanFilter

    def get_queryset(self) -> QuerySet:
        business_area = self.get_business_area()
        program = self.get_program()
        return PaymentPlan.objects.filter(business_area=business_area, program_cycle__program=program)

    @etag_decorator(TPKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=TPKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
