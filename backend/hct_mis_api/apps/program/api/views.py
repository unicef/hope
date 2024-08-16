import logging
from typing import Any

from django.db.models import QuerySet

from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_extensions.cache.decorators import cache_response

from hct_mis_api.api.caches import etag_decorator
from hct_mis_api.apps.account.api.permissions import (
    ProgramCycleCreatePermission,
    ProgramCycleDeletePermission,
    ProgramCycleUpdatePermission,
    ProgramCycleViewDetailsPermission,
    ProgramCycleViewListPermission,
)
from hct_mis_api.apps.core.api.mixins import ActionMixin, BusinessAreaProgramMixin
from hct_mis_api.apps.program.api.caches import ProgramCycleKeyConstructor
from hct_mis_api.apps.program.api.filters import ProgramCycleFilter
from hct_mis_api.apps.program.api.serializers import (
    ProgramCycleCreateSerializer,
    ProgramCycleDeleteSerializer,
    ProgramCycleListSerializer,
    ProgramCycleUpdateSerializer,
)
from hct_mis_api.apps.program.models import Program, ProgramCycle

logger = logging.getLogger(__name__)


class ProgramCycleViewSet(
    ActionMixin,
    BusinessAreaProgramMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_classes_by_action = {
        "list": ProgramCycleListSerializer,
        "retrieve": ProgramCycleListSerializer,
        "create": ProgramCycleCreateSerializer,
        "update": ProgramCycleUpdateSerializer,
        "partial_update": ProgramCycleUpdateSerializer,
        "delete": ProgramCycleDeleteSerializer,
    }
    permission_classes_by_action = {
        "list": [ProgramCycleViewListPermission],
        "retrieve": [ProgramCycleViewDetailsPermission],
        "create": [ProgramCycleCreatePermission],
        "update": [ProgramCycleUpdatePermission],
        "partial_update": [ProgramCycleUpdatePermission],
        "delete": [ProgramCycleDeletePermission],
    }

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

    # def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
    #     serializer_class = self.get_serializer_class()
    #     serializer = serializer_class(self.get_object())
    #     return Response(serializer.data)

    def perform_destroy(self, program_cycle: ProgramCycle) -> None:
        if program_cycle.program.status != Program.ACTIVE:
            raise ValidationError("Only Programme Cycle for Active Programme can be deleted.")

        if program_cycle.status != ProgramCycle.DRAFT:
            raise ValidationError("Only Draft Programme Cycle can be deleted.")

        if program_cycle.program.cycles.count() == 1:
            raise ValidationError("Don’t allow to delete last Cycle.")

        program_cycle.delete()

    @action(detail=True, methods=["post"], permission_classes=[ProgramCycleUpdatePermission])
    def finish(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        program_cycle = self.get_object()
        program_cycle.set_finish()
        return Response(status=status.HTTP_200_OK, data={"message": "Programme Cycle Finished"})

    @action(detail=True, methods=["post"], permission_classes=[ProgramCycleUpdatePermission])
    def reactivate(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        program_cycle = self.get_object()
        program_cycle.set_active()
        return Response(status=status.HTTP_200_OK, data={"message": "Programme Cycle Reactivated"})
