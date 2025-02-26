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
    queryset = PaymentPlan.objects.all()
    program_model_field = "program_cycle__program"
    serializer_class = TargetPopulationListSerializer
    PERMISSIONS = [Permissions.TARGETING_VIEW_LIST]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = PaymentPlanFilter

    @etag_decorator(TPKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=TPKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
