import logging
import mimetypes
from typing import Any, Optional

from django.db import transaction
from django.db.models import QuerySet
from django.http import FileResponse
from django.utils import timezone

from constance import config
from django_filters import rest_framework as filters
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from hct_mis_api.api.caches import etag_decorator
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.core.api.mixins import (
    BaseViewSet,
    BusinessAreaProgramsAccessMixin,
    CountActionMixin,
    DecodeIdForDetailMixin,
    ProgramMixin,
    SerializerActionMixin,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import (
    check_concurrency_version_in_mutation,
    decode_id_string,
    decode_id_string_required,
)
from hct_mis_api.apps.payment.api.caches import PaymentPlanKeyConstructor
from hct_mis_api.apps.payment.api.filters import (
    PaymentPlanFilter,
    TargetPopulationFilter,
)
from hct_mis_api.apps.payment.api.serializers import (
    PaymentDetailSerializer,
    PaymentListSerializer,
    PaymentPlanBulkActionSerializer,
    PaymentPlanCreateUpdateSerializer,
    PaymentPlanDetailSerializer,
    PaymentPlanExcludeBeneficiariesSerializer,
    PaymentPlanListSerializer,
    PaymentPlanSerializer,
    PaymentPlanSupportingDocumentSerializer,
    TargetPopulationApplyEngineFormulaSerializer,
    TargetPopulationCopySerializer,
    TargetPopulationCreateSerializer,
    TargetPopulationDetailSerializer,
    TPHouseholdListSerializer,
)
from hct_mis_api.apps.payment.celery_tasks import (
    payment_plan_apply_steficon_hh_selection,
    payment_plan_exclude_beneficiaries,
    payment_plan_full_rebuild,
)
from hct_mis_api.apps.payment.models import (
    Payment,
    PaymentPlan,
    PaymentPlanSupportingDocument,
)
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.program.models import ProgramCycle
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.targeting.api.serializers import TargetPopulationListSerializer

logger = logging.getLogger(__name__)


class PaymentPlanMixin:
    serializer_class = PaymentPlanSerializer
    filter_backends = (
        filters.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    filterset_class = PaymentPlanFilter
    search_fields = (
        "unicef_id",
        "id",
        "^name",
    )


class PaymentPlanViewSet(
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
    PaymentPlanMixin,
    DecodeIdForDetailMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    BaseViewSet,
):
    program_model_field = "program_cycle__program"
    queryset = PaymentPlan.objects.exclude(status__in=PaymentPlan.PRE_PAYMENT_PLAN_STATUSES).order_by("unicef_id")
    http_method_names = ["get", "post", "patch", "delete"]
    PERMISSIONS = [Permissions.PM_VIEW_LIST]
    serializer_classes_by_action = {
        "list": PaymentPlanListSerializer,
        "retrieve": PaymentPlanDetailSerializer,
        "open": PaymentPlanCreateUpdateSerializer,
        "partial_update": PaymentPlanCreateUpdateSerializer,
        "exclude_beneficiaries": PaymentPlanExcludeBeneficiariesSerializer,
    }
    permissions_by_action = {
        "list": [
            Permissions.PM_VIEW_LIST,
        ],
        "retrieve": [
            Permissions.PM_VIEW_DETAILS,
        ],
        "open": [Permissions.PM_CREATE],
        "partial_update": [Permissions.PM_CREATE],
        "destroy": [Permissions.PM_CREATE],
        "exclude_beneficiaries": [Permissions.PM_EXCLUDE_BENEFICIARIES_FROM_FOLLOW_UP_PP],
    }

    def get_object(self) -> PaymentPlan:
        return get_object_or_404(PaymentPlan, id=decode_id_string(self.kwargs.get("pk")))

    @etag_decorator(PaymentPlanKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=PaymentPlanKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def open(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        serializer = self.get_serializer(data=request.data, context={"payment_plan": payment_plan})
        if serializer.is_valid():
            old_payment_plan = copy_model_object(payment_plan)

            payment_plan = PaymentPlanService(payment_plan=payment_plan).open(input_data=serializer.validated_data)
            log_create(
                mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
                business_area_field="business_area",
                user=request.user,
                programs=payment_plan.program,
                old_object=old_payment_plan,
                new_object=payment_plan,
            )
            response_serializer = PaymentPlanDetailSerializer(payment_plan, context={"request": request})
            return Response(
                data=response_serializer.data,
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)
        payment_plan = PaymentPlanService(payment_plan=payment_plan).delete()
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def exclude_beneficiaries(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()

        if payment_plan.status not in (PaymentPlan.Status.OPEN, PaymentPlan.Status.LOCKED):
            raise ValidationError("Beneficiary can be excluded only for 'Open' or 'Locked' status of Payment Plan")

        serializer = self.get_serializer(
            data=request.data,
        )
        if serializer.is_valid():
            payment_plan_exclude_beneficiaries.delay(
                str(payment_plan.id),
                serializer.validated_data["excluded_households_ids"],
                serializer.validated_data.get("exclusion_reason", ""),
            )

            payment_plan.background_action_status_excluding_beneficiaries()
            payment_plan.exclude_household_error = ""
            payment_plan.save(update_fields=["background_action_status", "exclude_household_error"])

            payment_plan.refresh_from_db()

            response_serializer = PaymentPlanDetailSerializer(payment_plan, context={"request": request})
            return Response(
                data=response_serializer.data,
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], PERMISSIONS=[Permissions.PM_LOCK_AND_UNLOCK])
    def lock(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)
        payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(
            input_data={"action": PaymentPlan.Action.LOCK}, user=request.user
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Payment Plan locked"})

    @action(detail=True, methods=["get"], PERMISSIONS=[Permissions.PM_LOCK_AND_UNLOCK])
    def unlock(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)
        payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(
            input_data={"action": PaymentPlan.Action.UNLOCK}, user=request.user
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Payment Plan unlocked"})


class TargetPopulationViewSet(
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
    PaymentPlanMixin,
    DecodeIdForDetailMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    BaseViewSet,
):
    program_model_field = "program_cycle__program"
    queryset = PaymentPlan.objects.all().order_by("created_at")
    http_method_names = ["get", "post", "patch", "delete"]
    serializer_classes_by_action = {
        "list": TargetPopulationListSerializer,
        "retrieve": TargetPopulationDetailSerializer,
        "create": TargetPopulationCreateSerializer,
        "partial_update": TargetPopulationCreateSerializer,
        "copy": TargetPopulationCopySerializer,
        "apply_engine_formula": TargetPopulationApplyEngineFormulaSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.TARGETING_VIEW_LIST],
        "retrieve": [Permissions.TARGETING_VIEW_DETAILS],
        "create": [Permissions.TARGETING_CREATE],
        "partial_update": [Permissions.TARGETING_UPDATE],
        "destroy": [Permissions.TARGETING_REMOVE],
        "copy": [Permissions.TARGETING_DUPLICATE],
        "apply_engine_formula": [Permissions.TARGETING_UPDATE],
    }
    filterset_class = TargetPopulationFilter

    def get_object(self) -> PaymentPlan:
        return get_object_or_404(PaymentPlan, id=decode_id_string(self.kwargs.get("pk")))

    @etag_decorator(PaymentPlanKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=PaymentPlanKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)
        payment_plan = PaymentPlanService(payment_plan=payment_plan).delete()
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], PERMISSIONS=[Permissions.TARGETING_LOCK])
    def lock(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        tp = self.get_object()
        old_tp = copy_model_object(tp)
        payment_plan = PaymentPlanService(tp).execute_update_status_action(
            input_data={"action": PaymentPlan.Action.TP_LOCK}, user=request.user
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_tp,
            new_object=tp,
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Target Population locked"})

    @action(detail=True, methods=["get"], PERMISSIONS=[Permissions.TARGETING_UNLOCK])
    def unlock(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        tp = self.get_object()
        old_tp = copy_model_object(tp)

        payment_plan = PaymentPlanService(tp).execute_update_status_action(
            input_data={"action": PaymentPlan.Action.TP_UNLOCK}, user=request.user
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_tp,
            new_object=tp,
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Target Population unlocked"})

    @action(detail=True, methods=["get"], PERMISSIONS=[Permissions.TARGETING_LOCK])
    def rebuild(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        tp = self.get_object()
        old_tp = copy_model_object(tp)

        payment_plan = PaymentPlanService(tp).execute_update_status_action(
            input_data={"action": PaymentPlan.Action.TP_REBUILD}, user=request.user
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_tp,
            new_object=tp,
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Target Population rebuilding"})

    @action(detail=True, methods=["get"], PERMISSIONS=[Permissions.TARGETING_CREATE, Permissions.TARGETING_SEND])
    def mark_ready(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        tp = self.get_object()
        old_tp = copy_model_object(tp)

        payment_plan = PaymentPlanService(tp).execute_update_status_action(
            input_data={"action": PaymentPlan.Action.TP_REBUILD}, user=request.user
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_tp,
            new_object=tp,
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Target Population ready for Payment Plan"})

    @action(detail=True, methods=["post"])
    def copy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        request.data["target_population_id"] = kwargs.get("pk")

        serializer = self.get_serializer(
            data=request.data,
        )
        if serializer.is_valid():
            name = serializer.validated_data["name"].strip()
            payment_plan_id = decode_id_string_required(serializer.validated_data["target_population_id"])
            program_cycle_id = decode_id_string_required(serializer.validated_data["program_cycle_id"])
            payment_plan = get_object_or_404(PaymentPlan, pk=payment_plan_id)
            program_cycle = get_object_or_404(ProgramCycle, pk=program_cycle_id)
            program = program_cycle.program

            if program_cycle.status == ProgramCycle.FINISHED:
                raise ValidationError("Not possible to assign Finished Program Cycle to Targeting.")
            if PaymentPlan.objects.filter(name=name, program_cycle=program_cycle, is_removed=False).exists():
                raise ValidationError(
                    f"Target Population with name: {name} and program cycle: {program_cycle.title} already exists."
                )

            payment_plan_copy = PaymentPlan(
                name=name,
                created_by=user,
                business_area=payment_plan.business_area,
                status=PaymentPlan.Status.TP_OPEN,
                status_date=timezone.now(),
                start_date=program_cycle.start_date,
                end_date=program_cycle.end_date,
                build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
                built_at=timezone.now(),
                male_children_count=payment_plan.male_children_count,
                female_children_count=payment_plan.female_children_count,
                male_adults_count=payment_plan.male_adults_count,
                female_adults_count=payment_plan.female_adults_count,
                total_households_count=payment_plan.total_households_count,
                total_individuals_count=payment_plan.total_individuals_count,
                steficon_rule_targeting=payment_plan.steficon_rule_targeting,
                steficon_targeting_applied_date=payment_plan.steficon_targeting_applied_date,
                program_cycle=program_cycle,
            )
            if payment_plan.targeting_criteria:
                payment_plan_copy.targeting_criteria = PaymentPlanService.copy_target_criteria(
                    payment_plan.targeting_criteria
                )
            payment_plan_copy.save()
            payment_plan_copy.refresh_from_db()

            transaction.on_commit(lambda: payment_plan_full_rebuild.delay(payment_plan_copy.id))
            log_create(
                PaymentPlan.ACTIVITY_LOG_MAPPING,
                "business_area",
                user,
                getattr(program, "pk", None),
                None,
                payment_plan_copy,
            )
            response_serializer = TargetPopulationDetailSerializer(payment_plan_copy, context={"request": request})
            return Response(
                data=response_serializer.data,
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def apply_engine_formula(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        tp = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
        )
        if serializer.is_valid():
            engine_formula_rule_id = decode_id_string_required(serializer.validated_data["engine_formula_rule_id"])
            if version := serializer.validated_data.get("version"):
                check_concurrency_version_in_mutation(version, tp)
            engine_rule = get_object_or_404(Rule, id=engine_formula_rule_id)
            # tp vulnerability_score
            if tp.status not in PaymentPlan.CAN_RUN_ENGINE_FORMULA_FOR_VULNERABILITY_SCORE:
                raise ValidationError(f"Not allowed to run engine formula within status {tp.status}.")
            if not engine_rule.enabled or engine_rule.deprecated:
                raise ValidationError("This engine rule is not enabled or is deprecated.")
            old_tp = copy_model_object(tp)
            rule_commit = engine_rule.latest
            tp.steficon_rule_targeting = rule_commit
            tp.status = PaymentPlan.Status.TP_STEFICON_WAIT
            tp.save()
            payment_plan_apply_steficon_hh_selection.delay(str(tp.pk), str(engine_rule.pk))
            log_create(
                mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
                business_area_field="business_area",
                user=request.user,
                programs=tp.program.pk,
                old_object=old_tp,
                new_object=tp,
            )
            response_serializer = TargetPopulationDetailSerializer(tp, context={"request": request})
            return Response(
                data=response_serializer.data,
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentPlanManagerialViewSet(
    BusinessAreaProgramsAccessMixin, PaymentPlanMixin, mixins.ListModelMixin, BaseViewSet
):
    queryset = PaymentPlan.objects.all()
    PERMISSIONS = [
        Permissions.PAYMENT_VIEW_LIST_MANAGERIAL,
    ]
    program_model_field = "program_cycle__program"

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(
                status__in=[
                    PaymentPlan.Status.IN_APPROVAL,
                    PaymentPlan.Status.IN_AUTHORIZATION,
                    PaymentPlan.Status.IN_REVIEW,
                    PaymentPlan.Status.ACCEPTED,
                ],
            )
        )

    # TODO: e2e failed probably because of cache here
    @etag_decorator(PaymentPlanKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=PaymentPlanKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @action(
        detail=False,
        methods=["post"],
        url_path="bulk-action",
        serializer_class=PaymentPlanBulkActionSerializer,
    )
    def bulk_action(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action_name = serializer.validated_data["action"]
        comment = serializer.validated_data.get("comment", "")
        input_data = {"action": action_name, "comment": comment}

        with transaction.atomic():
            for payment_plan_id_str in serializer.validated_data["ids"]:
                self._perform_payment_plan_status_action(
                    payment_plan_id_str,
                    input_data,
                    self.business_area,
                    request,
                )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _perform_payment_plan_status_action(
        self,
        payment_plan_id_str: str,
        input_data: dict,
        business_area: BusinessArea,
        request: Request,
    ) -> None:
        payment_plan_id = decode_id_string(payment_plan_id_str)
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)

        if not self.request.user.has_perm(
            self._get_action_permission(input_data["action"]),  # type: ignore
            payment_plan.program_cycle.program or business_area,
        ):
            raise PermissionDenied(
                f"You do not have permission to perform action {input_data['action']} "
                f"on payment plan with id {payment_plan.unicef_id}."
            )

        old_payment_plan = copy_model_object(payment_plan)
        if old_payment_plan.imported_file:
            old_payment_plan.imported_file = copy_model_object(payment_plan.imported_file)
        if old_payment_plan.export_file_entitlement:
            old_payment_plan.export_file_entitlement = copy_model_object(payment_plan.export_file_entitlement)
        if old_payment_plan.export_file_per_fsp:
            old_payment_plan.export_file_per_fsp = copy_model_object(payment_plan.export_file_per_fsp)

        payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(
            input_data=input_data, user=request.user
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program_cycle.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )

    def _get_action_permission(self, action_name: str) -> Optional[str]:
        action_to_permissions_map = {
            PaymentPlan.Action.APPROVE.name: Permissions.PM_ACCEPTANCE_PROCESS_APPROVE.name,
            PaymentPlan.Action.AUTHORIZE.name: Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE.name,
            PaymentPlan.Action.REVIEW.name: Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW.name,
        }
        return action_to_permissions_map.get(action_name)


class PaymentPlanSupportingDocumentViewSet(
    SerializerActionMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, BaseViewSet
):
    serializer_class = PaymentPlanSupportingDocumentSerializer
    lookup_field = "file_id"

    serializer_classes_by_action = {
        "create": PaymentPlanSupportingDocumentSerializer,
        "delete": PaymentPlanSupportingDocumentSerializer,
    }
    permissions_by_action = {
        "create": [Permissions.PM_UPLOAD_SUPPORTING_DOCUMENT],
        "delete": [Permissions.PM_DELETE_SUPPORTING_DOCUMENT],
        "destroy": [Permissions.PM_DELETE_SUPPORTING_DOCUMENT],
        "download": [Permissions.PM_DOWNLOAD_SUPPORTING_DOCUMENT],
    }

    def get_queryset(self) -> QuerySet:
        payment_plan_id = decode_id_string(self.kwargs.get("payment_plan_id"))
        return PaymentPlanSupportingDocument.objects.filter(payment_plan_id=payment_plan_id)

    def get_object(self) -> PaymentPlanSupportingDocument:
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(self.kwargs.get("payment_plan_id")))
        return get_object_or_404(
            PaymentPlanSupportingDocument, id=decode_id_string(self.kwargs.get("file_id")), payment_plan=payment_plan
        )

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        document = self.get_object()
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    def download(self, request: Request, *args: Any, **kwargs: Any) -> FileResponse:
        document = self.get_object()
        file = document.file
        file_mimetype, _ = mimetypes.guess_type(file.url)
        response = FileResponse(
            file.open(), as_attachment=True, content_type=file_mimetype or "application/octet-stream"
        )
        response["Content-Disposition"] = f"attachment; filename={file.name.split('/')[-1]}"
        return response


class PaymentViewSet(
    CountActionMixin,
    SerializerActionMixin,
    DecodeIdForDetailMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = Payment.objects.all()
    PERMISSIONS = [Permissions.PM_VIEW_DETAILS, Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS]
    serializer_classes_by_action = {
        "list": PaymentListSerializer,
        "retrieve": PaymentDetailSerializer,
    }
    permissions_by_action = {
        "list": [
            Permissions.PM_VIEW_DETAILS,
        ],
        "retrieve": [
            Permissions.PM_VIEW_DETAILS,
        ],
    }


class TPHouseholdViewSet(
    CountActionMixin,
    SerializerActionMixin,
    DecodeIdForDetailMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = Payment.objects.all()
    PERMISSIONS = [Permissions.TARGETING_VIEW_LIST]
    serializer_classes_by_action = {
        "list": TPHouseholdListSerializer,
        "retrieve": TPHouseholdListSerializer,
    }
    permissions_by_action = {
        "list": [
            Permissions.TARGETING_VIEW_LIST,
        ],
        "retrieve": [
            Permissions.TARGETING_VIEW_DETAILS,
        ],
    }
