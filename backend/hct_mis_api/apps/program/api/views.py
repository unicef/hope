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
from hct_mis_api.apps.account.api.permissions import ProgramCycleViewListPermission
from hct_mis_api.apps.core.api.mixins import BusinessAreaProgramMixin
from hct_mis_api.apps.program.api.caches import ProgramCycleKeyConstructor
from hct_mis_api.apps.program.api.filters import ProgramCycleFilter
from hct_mis_api.apps.program.api.serializers import ProgramCycleListSerializer
from hct_mis_api.apps.program.models import ProgramCycle

logger = logging.getLogger(__name__)


class ProgramCycleViewSet(
    BusinessAreaProgramMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = ProgramCycleListSerializer
    permission_classes = [ProgramCycleViewListPermission]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = ProgramCycleFilter

    def get_queryset(self) -> QuerySet:
        business_area = self.get_business_area()
        program = self.get_program()
        return ProgramCycle.objects.filter(program__business_area=business_area, program=program)

    @etag_decorator(ProgramCycleKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=ProgramCycleKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        serializer = ProgramCycleListSerializer(instance)
        return Response(serializer.data)
