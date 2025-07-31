import copy
import logging
from typing import Any

from django.db import transaction
from django.db.models import Case, IntegerField, Prefetch, QuerySet, Value, When

from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
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
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.api.filters import UpdatedAtFilter
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
from hct_mis_api.apps.periodic_data_update.service.flexible_attribute_service import (
    FlexibleAttributeForPDUService,
)
from hct_mis_api.apps.program.api.caches import (
    BeneficiaryGroupKeyConstructor,
    ProgramCycleKeyConstructor,
    ProgramListKeyConstructor,
)
from hct_mis_api.apps.program.api.filters import ProgramCycleFilter, ProgramFilter
from hct_mis_api.apps.program.api.serializers import (
    BeneficiaryGroupSerializer,
    ProgramChoicesSerializer,
    ProgramCopySerializer,
    ProgramCreateSerializer,
    ProgramCycleCreateSerializer,
    ProgramCycleListSerializer,
    ProgramCycleUpdateSerializer,
    ProgramDetailSerializer,
    ProgramListSerializer,
    ProgramUpdatePartnerAccessSerializer,
    ProgramUpdateSerializer,
)
from hct_mis_api.apps.program.celery_tasks import (
    copy_program_task,
    populate_pdu_new_rounds_with_null_values_task,
)
from hct_mis_api.apps.program.models import BeneficiaryGroup, Program, ProgramCycle
from hct_mis_api.apps.program.utils import (
    copy_program_object,
    create_program_partner_access,
    remove_program_partner_access,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.services.biometric_deduplication import (
    BiometricDeduplicationService,
)

logger = logging.getLogger(__name__)


class ProgramViewSet(
    SerializerActionMixin,
    BusinessAreaMixin,
    CountActionMixin,
    RetrieveModelMixin,
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    BaseViewSet,
):
    permissions_by_action = {
        "retrieve": [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        "list": [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS, *ALL_GRIEVANCES_CREATE_MODIFY],
        "create": [Permissions.PROGRAMME_CREATE],
        "update": [Permissions.PROGRAMME_UPDATE],
        "activate": [Permissions.PROGRAMME_ACTIVATE],
        "finish": [Permissions.PROGRAMME_FINISH],
        "update_partner_access": [Permissions.PROGRAMME_UPDATE],
        "copy": [Permissions.PROGRAMME_DUPLICATE],
        "destroy": [Permissions.PROGRAMME_REMOVE],
        "choices": [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        "deduplication_flags": [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        "payments": [Permissions.PM_VIEW_PAYMENT_LIST],
    }
    queryset = Program.objects.all()
    serializer_classes_by_action = {
        "list": ProgramListSerializer,
        "retrieve": ProgramDetailSerializer,
        "create": ProgramCreateSerializer,
        "update": ProgramUpdateSerializer,
        "update_partner_access": ProgramUpdatePartnerAccessSerializer,
        "copy": ProgramCopySerializer,
        "choices": ProgramChoicesSerializer,
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

    @action(detail=True, methods=["post"])
    def activate(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        program = self.get_object()
        old_program = copy.deepcopy(program)

        if program.status == Program.ACTIVE:
            raise ValidationError("Program is already active.")

        program.status = Program.ACTIVE
        program.save(update_fields=["status"])

        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", self.request.user, program.pk, old_program, program)

        return Response(status=status.HTTP_200_OK, data={"message": "Program Activated."})

    @action(detail=True, methods=["post"])
    def finish(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        program = self.get_object()
        old_program = copy.deepcopy(program)

        if program.status != Program.ACTIVE:
            raise ValidationError("Only active Program can be finished.")
        # check payment plans
        if (
            PaymentPlan.objects.filter(program_cycle__in=program.cycles.all())
            .exclude(
                status__in=PaymentPlan.PRE_PAYMENT_PLAN_STATUSES
                + (PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED),
            )
            .exists()
        ):
            raise ValidationError("All Payment Plans and Follow-Up Payment Plans have to be Reconciled.")

        # check for active cycles
        if program.cycles.filter(status=ProgramCycle.ACTIVE).exists():
            raise ValidationError("Cannot finish Program with active cycles.")

        if program.end_date is None:
            raise ValidationError("Cannot finish programme without end date.")

        program.status = Program.FINISHED
        program.save(update_fields=["status"])

        if program.biometric_deduplication_enabled:
            BiometricDeduplicationService().delete_deduplication_set(program)

        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", self.request.user, program.pk, old_program, program)

        return Response(status=status.HTTP_200_OK, data={"message": "Program Finished."})

    @transaction.atomic
    def perform_create(self, serializer: BaseSerializer[Any]) -> None:
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        partners_data = data.pop("partners", [])
        pdu_fields = data.pop("pdu_fields", [])

        program = Program(
            **data,
            status=Program.DRAFT,
            business_area=self.business_area,
        )
        if not program.programme_code:
            program.programme_code = program.generate_programme_code()
        program.slug = program.generate_slug()

        program.full_clean()
        program.save()

        ProgramCycle.objects.create(
            program=program,
            start_date=program.start_date,
            end_date=None,
            status=ProgramCycle.DRAFT,
            created_by=self.request.user,
        )
        # create partner access only for SELECTED_PARTNERS_ACCESS type, since NONE and ALL are handled through signal
        if program.partner_access == Program.SELECTED_PARTNERS_ACCESS:
            create_program_partner_access(partners_data, program, program.partner_access)

        if pdu_fields:
            FlexibleAttributeForPDUService(program, pdu_fields).create_pdu_flex_attributes()

        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", self.request.user, program.pk, None, program)

        serializer.instance = program

    @transaction.atomic
    def perform_update(self, serializer: BaseSerializer[Any]) -> None:
        program = self.get_object()
        old_program = copy.deepcopy(program)

        if program.status == Program.FINISHED:
            raise ValidationError("Cannot update a finished Program.")

        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        pdu_fields = data.pop("pdu_fields", [])

        for attrib, value in data.items():
            if hasattr(program, attrib):
                setattr(program, attrib, value)
        program.full_clean()
        program.save()

        if pdu_fields:
            FlexibleAttributeForPDUService(program, pdu_fields).update_pdu_flex_attributes_in_program_update()
            populate_pdu_new_rounds_with_null_values_task.delay(str(program.id))

        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", self.request.user, program.pk, old_program, program)

        serializer.instance = program

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def update_partner_access(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        program = self.get_object()
        old_program = copy.deepcopy(program)
        old_partner_access = old_program.partner_access

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance=program, data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        partners_data = data.pop("partners", [])
        partner_access = data.pop("partner_access", None)

        program.partner_access = partner_access
        # update partner access for ALL_PARTNERS_ACCESS type if it was not changed but the partners need to be refetched
        if partner_access == old_partner_access and partner_access == Program.ALL_PARTNERS_ACCESS:
            create_program_partner_access([], program, partner_access)
        # update partner access only for SELECTED_PARTNERS_ACCESS type, since update to NONE and ALL are handled through signal
        if partner_access == Program.SELECTED_PARTNERS_ACCESS:
            partners_data = create_program_partner_access(partners_data, program, partner_access)
            remove_program_partner_access(partners_data, program)
        program.save()

        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", self.request.user, program.pk, old_program, program)

        return Response(status=status.HTTP_200_OK, data={"message": "Partner access updated."})

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def copy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        program = self.get_object()
        old_program = copy.deepcopy(program)

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance=program, data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        partners_data = data.pop("partners", [])
        partner_access = data.get("partner_access", None)
        pdu_fields = data.pop("pdu_fields", [])

        program = copy_program_object(str(program.id), data, self.request.user)  # type: ignore

        # create partner access only for SELECTED_PARTNERS_ACCESS type, since NONE and ALL are handled through signal
        if partner_access == Program.SELECTED_PARTNERS_ACCESS:
            create_program_partner_access(partners_data, program, partner_access)

        transaction.on_commit(
            lambda: copy_program_task.delay(
                copy_from_program_id=str(old_program.id),
                new_program_id=str(program.id),
                user_id=str(self.request.user.id),
            )
        )

        if pdu_fields:
            FlexibleAttributeForPDUService(program, pdu_fields).create_pdu_flex_attributes()

        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", self.request.user, program.pk, None, program)

        return Response(
            status=status.HTTP_201_CREATED,
            data={"message": f"Program copied successfully. New Program slug: {program.slug}"},
        )

    def perform_destroy(self, instance: Program) -> None:
        old_program = copy.deepcopy(instance)
        if instance.status != Program.DRAFT:
            raise ValidationError("Only Draft Program can be deleted.")

        instance.delete()
        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", self.request.user, instance.pk, old_program, instance)

    @action(detail=False, methods=["get"])
    def choices(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        return Response(data=self.get_serializer(instance={}).data)

    @action(detail=True, methods=["get"])
    def deduplication_flags(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        program = self.get_object()

        # deduplication engine in progress
        is_still_processing = RegistrationDataImport.objects.filter(
            program=program,
            deduplication_engine_status__in=[
                RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS,
            ],
        ).exists()
        # all RDIs are deduplicated
        all_rdis_deduplicated = (
            RegistrationDataImport.objects.filter(program=program).all().count()
            == RegistrationDataImport.objects.filter(
                deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
                program=program,
            ).count()
        )
        # RDI merge in progress
        rdi_merging = RegistrationDataImport.objects.filter(
            program=program,
            status__in=[
                RegistrationDataImport.MERGE_SCHEDULED,
                RegistrationDataImport.MERGING,
                RegistrationDataImport.MERGE_ERROR,
            ],
        ).exists()
        is_deduplication_disabled = is_still_processing or all_rdis_deduplicated or rdi_merging

        return Response(
            {
                "can_run_deduplication": program.biometric_deduplication_enabled,
                "is_deduplication_disabled": is_deduplication_disabled,
            }
        )

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
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = UpdatedAtFilter

    @etag_decorator(BeneficiaryGroupKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=BeneficiaryGroupKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
