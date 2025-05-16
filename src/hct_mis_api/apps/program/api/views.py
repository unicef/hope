import logging
from typing import Any

from django.db.models import Case, IntegerField, Prefetch, QuerySet, Value, When

from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_extensions.cache.decorators import cache_response

from hct_mis_api.api.caches import etag_decorator
from hct_mis_api.apps.account.permissions import (
    ALL_GRIEVANCES_CREATE_MODIFY,
    Permissions,
)
from hct_mis_api.apps.core.api.mixins import (
    BaseViewSet,
    BusinessAreaMixin,
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
)
from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.payment.api.serializers import PaymentListSerializer
from hct_mis_api.apps.payment.models import Payment, PaymentPlan
from hct_mis_api.apps.program.api.caches import (
    BeneficiaryGroupKeyConstructor,
    ProgramCycleKeyConstructor,
    ProgramListKeyConstructor,
)
from hct_mis_api.apps.program.api.filters import ProgramCycleFilter, ProgramFilter
from hct_mis_api.apps.program.api.serializers import (
    BeneficiaryGroupSerializer,
    ProgramCycleCreateSerializer,
    ProgramCycleDeleteSerializer,
    ProgramCycleListSerializer,
    ProgramCycleUpdateSerializer,
    ProgramDetailSerializer,
    ProgramListSerializer,
)
from hct_mis_api.apps.program.models import BeneficiaryGroup, Program, ProgramCycle
from hct_mis_api.apps.program.validators import ProgramDeletionValidator

logger = logging.getLogger(__name__)


class ProgramViewSet(
    SerializerActionMixin,
    BusinessAreaMixin,
    ProgramDeletionValidator,
    CountActionMixin,
    RetrieveModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    BaseViewSet,
):
    permissions_by_action = {
        "retrieve": [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        "list": [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS, *ALL_GRIEVANCES_CREATE_MODIFY],
        "destroy": [Permissions.PROGRAMME_REMOVE],
        "payments": [Permissions.PM_VIEW_PAYMENT_LIST],
    }
    queryset = Program.objects.all()
    serializer_classes_by_action = {
        "list": ProgramListSerializer,
        "retrieve": ProgramDetailSerializer,
        "payments": PaymentListSerializer,
    }
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = ProgramFilter
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[Program]:
        queryset = super().get_queryset()
        user = self.request.user
        allowed_programs = queryset.filter(id__in=user.get_program_ids_for_business_area(self.business_area.id))
        return (
            queryset.filter(
                data_collecting_type__deprecated=False,
                id__in=allowed_programs.values_list("id", flat=True),
            )
            .exclude(data_collecting_type__code="unknown")
            .annotate(
                custom_order=Case(
                    When(status=Program.DRAFT, then=Value(1)),
                    When(status=Program.ACTIVE, then=Value(2)),
                    When(status=Program.FINISHED, then=Value(3)),
                    output_field=IntegerField(),
                )
            )
            .prefetch_related(Prefetch("pdu_fields", queryset=FlexibleAttribute.objects.order_by("created_at")))
            .select_related("beneficiary_group", "data_collecting_type")
            .order_by("custom_order", "start_date")
        )

    @etag_decorator(ProgramListKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=ProgramListKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    def perform_destroy(self, instance: Program) -> None:
        self.validate(program=instance)
        super().perform_destroy(instance)

    @extend_schema(
        responses={
            200: PaymentListSerializer(many=True),
        },
    )
    @action(detail=True, methods=["get"])
    def payments(self) -> Response:
        program = self.get_object()
        payments = Payment.objects.filter(parent__program_cycle__program=program)
        page = self.paginate_queryset(payments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)


class ProgramCycleViewSet(
    SerializerActionMixin,
    CountActionMixin,
    ProgramMixin,
    ModelViewSet,
    BaseViewSet,
):
    queryset = ProgramCycle.objects.all()
    serializer_classes_by_action = {
        "list": ProgramCycleListSerializer,
        "retrieve": ProgramCycleListSerializer,
        "create": ProgramCycleCreateSerializer,
        "update": ProgramCycleUpdateSerializer,
        "partial_update": ProgramCycleUpdateSerializer,
        "destroy": ProgramCycleDeleteSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS],
        "retrieve": [Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS],
        "create": [Permissions.PM_PROGRAMME_CYCLE_CREATE],
        "update": [Permissions.PM_PROGRAMME_CYCLE_UPDATE],
        "partial_update": [Permissions.PM_PROGRAMME_CYCLE_UPDATE],
        "destroy": [Permissions.PM_PROGRAMME_CYCLE_DELETE],
    }

    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = ProgramCycleFilter

    @etag_decorator(ProgramCycleKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=ProgramCycleKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    def perform_update(self, serializer: BaseSerializer[Any]) -> None:
        cycle = self.get_object()
        previous_start_date = cycle.start_date
        previous_end_date = cycle.end_date

        updated_cycle = serializer.save()
        # update PaymentPlan start and end dates
        if previous_start_date != updated_cycle.start_date:
            PaymentPlan.objects.filter(program_cycle=cycle).update(start_date=updated_cycle.start_date)
        if previous_end_date != updated_cycle.end_date:
            PaymentPlan.objects.filter(program_cycle=cycle).update(end_date=updated_cycle.end_date)

    def perform_destroy(self, program_cycle: ProgramCycle) -> None:
        if program_cycle.program.status != Program.ACTIVE:
            raise ValidationError("Only Programme Cycle for Active Programme can be deleted.")

        if program_cycle.status != ProgramCycle.DRAFT:
            raise ValidationError("Only Draft Programme Cycle can be deleted.")

        if program_cycle.program.cycles.count() == 1:
            raise ValidationError("Don’t allow to delete last Cycle.")

        if program_cycle.payment_plans.exists():
            raise ValidationError("Don’t allow to delete Cycle with assigned Target Population")

        program_cycle.delete()

    @action(detail=True, methods=["post"], PERMISSIONS=[Permissions.PM_PROGRAMME_CYCLE_UPDATE])
    def finish(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        program_cycle = self.get_object()
        program_cycle.set_finish()
        return Response(status=status.HTTP_200_OK, data={"message": "Programme Cycle Finished"})

    @action(detail=True, methods=["post"], PERMISSIONS=[Permissions.PM_PROGRAMME_CYCLE_UPDATE])
    def reactivate(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        program_cycle = self.get_object()
        program_cycle.set_active()
        return Response(status=status.HTTP_200_OK, data={"message": "Programme Cycle Reactivated"})


class BeneficiaryGroupViewSet(
    mixins.ListModelMixin,
    GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    queryset = BeneficiaryGroup.objects.all()
    serializer_class = BeneficiaryGroupSerializer

    @etag_decorator(BeneficiaryGroupKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=BeneficiaryGroupKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
