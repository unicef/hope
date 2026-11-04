from collections.abc import Callable
from decimal import Decimal
from functools import cached_property
from io import BytesIO
import logging
import mimetypes
from typing import TYPE_CHECKING, Any, cast
from zipfile import BadZipFile

from django.contrib.admin.options import get_content_type_for_model
from django.db import DatabaseError, transaction
from django.db.models import Count, Exists, F, OuterRef, Prefetch, Q, QuerySet, Sum
from django.db.models.functions import Coalesce
from django.http import FileResponse, Http404, HttpResponse
from django.utils import timezone
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import mixins, serializers, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from hope.api.caches import cached_response, etag_decorator
from hope.apps.account.permissions import Permissions
from hope.apps.activity_log.utils import copy_model_object, create_diff
from hope.apps.core.api.mixins import (
    BaseViewSet,
    BusinessAreaMixin,
    BusinessAreaProgramsAccessMixin,
    CountActionMixin,
    ProgramMixin,
    ProgramVisibilityMixin,
    SerializerActionMixin,
)
from hope.apps.core.api.parsers import DictDrfNestedParser
from hope.apps.core.utils import check_concurrency_version_in_mutation
from hope.apps.household.api.serializers.individual import AccountSerializer
from hope.apps.payment.api.caches import (
    PaymentListListKeyConstructor,
    PaymentPlanKeyConstructor,
    PaymentPlanListKeyConstructor,
    PaymentPlanPurposeListKeyConstructor,
    PaymentVerificationListKeyConstructor,
    TargetPopulationListKeyConstructor,
)
from hope.apps.payment.api.filters import (
    NotEligiblePaymentSearchFilter,
    PaymentListFilter,
    PaymentListListFilter,
    PaymentListOfficeSearchFilter,
    PaymentOfficeSearchFilter,
    PaymentPlanFilter,
    PaymentSearchFilter,
    PaymentVerificationRecordFilter,
    PendingPaymentFilter,
    TargetPopulationFilter,
)
from hope.apps.payment.api.querysets import with_payment_related_data
from hope.apps.payment.api.serializers import (
    AcceptanceProcessSerializer,
    AccountAttachmentUploadSerializer,
    ApplyCustomExchangeRateSerializer,
    ApplyEngineFormulaSerializer,
    ApplyFlatAmountEntitlementSerializer,
    AssignFundsCommitmentsSerializer,
    FinancialInstitutionChoiceSerializer,
    FollowUpInstructionCreateSerializer,
    FollowUpInstructionDetailSerializer,
    FollowUpInstructionListSerializer,
    FspChoicesSerializer,
    FSPXlsxTemplateSerializer,
    NotEligiblePaymentRowSerializer,
    PaymentDetailSerializer,
    PaymentListCreateUpdateSerializer,
    PaymentListDetailSerializer,
    PaymentListExcludeBeneficiariesSerializer,
    PaymentListListSerializer,
    PaymentListSerializer,
    PaymentPlanAbortSerializer,
    PaymentPlanBulkActionSerializer,
    PaymentPlanCloseSerializer,
    PaymentPlanCreateFollowUpSerializer,
    PaymentPlanCreateSerializer,
    PaymentPlanCreateTopUpSerializer,
    PaymentPlanDeliveryExportSerializer,
    PaymentPlanDetailSerializer,
    PaymentPlanImportFileSerializer,
    PaymentPlanListSerializer,
    PaymentPlanManagerialSerializer,
    PaymentPlanReconciliationImportSerializer,
    PaymentPlanSupportingDocumentSerializer,
    PaymentPlanUpdateSerializer,
    PaymentRowSerializer,
    PaymentVerificationPlanActivateSerializer,
    PaymentVerificationPlanCreateSerializer,
    PaymentVerificationPlanDetailsSerializer,
    PaymentVerificationPlanImportSerializer,
    PaymentVerificationPlanListSerializer,
    PaymentVerificationSampleSizeSerializer,
    PaymentVerificationUpdateSerializer,
    PendingPaymentSerializer,
    RevertMarkPaymentAsFailedSerializer,
    SplitPaymentPlanSerializer,
    TargetPopulationCopySerializer,
    TargetPopulationCreateSerializer,
    TargetPopulationDetailSerializer,
    XlsxErrorSerializer,
)
from hope.apps.payment.celery_tasks import (
    export_payment_plan_delivery_xlsx_async_task,
    export_pdf_follow_up_instruction_summary_async_task,
    export_pdf_payment_plan_summary_async_task,
    import_payment_list_from_xlsx_async_task,
    import_payment_plan_delivery_from_xlsx_async_task,
    import_payment_plan_fsp_extra_fields_from_xlsx_async_task,
    payment_list_apply_engine_rule_async_task,
    payment_list_apply_steficon_hh_selection_async_task,
    payment_list_exclude_beneficiaries_async_task,
    payment_list_full_rebuild_async_task,
    payment_list_set_entitlement_flat_amount_async_task,
    recalculate_owner_exchange_rate_async_task,
    send_payment_plan_delivery_xlsx_password_async_task,
)
from hope.apps.payment.flows import PaymentListFlow
from hope.apps.payment.notifications import PaymentPlanReconciliationImportNotification
from hope.apps.payment.services.follow_up_instruction_service import FollowUpInstructionService
from hope.apps.payment.services.mark_as_failed import (
    mark_as_failed,
    revert_mark_as_failed,
)
from hope.apps.payment.services.payment_list_services import PaymentListService
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.apps.payment.services.sampling import Sampling
from hope.apps.payment.services.top_up_amount_service import TopUpAmountTemplateService
from hope.apps.payment.services.verification_plan_crud_services import (
    VerificationPlanCrudServices,
    get_payment_records,
)
from hope.apps.payment.services.verification_plan_status_change_services import (
    VerificationPlanStatusChangeServices,
)
from hope.apps.payment.services.verifiers import PaymentVerificationArgumentVerifier
from hope.apps.payment.utils import (
    calculate_counts,
    from_received_to_status,
    log_follow_up_instruction_change,
    log_payment_plan_change,
    log_payment_plan_supporting_document,
)
from hope.apps.payment.xlsx.xlsx_follow_up_instruction_reconciliation_import_service import (
    XlsxFollowUpInstructionReconciliationImportService,
)
from hope.apps.payment.xlsx.xlsx_payment_list_delivery_import_service import (
    NULL_DELIVERY_POLICY_OPTION,
    OVERRIDE_OPTION,
)
from hope.apps.payment.xlsx.xlsx_payment_list_import_service import (
    XlsxPaymentListImportService,
)
from hope.apps.payment.xlsx.xlsx_payment_plan_delivery_export_service import (
    XlsxPaymentPlanDeliveryExportService,
)
from hope.apps.payment.xlsx.xlsx_payment_plan_delivery_import_service import (
    XlsxPaymentPlanDeliveryImportService,
)
from hope.apps.payment.xlsx.xlsx_payment_plan_fsp_extra_fields_export_service import (
    XlsxPaymentPlanFspExtraFieldsExportService,
)
from hope.apps.payment.xlsx.xlsx_payment_plan_fsp_extra_fields_import_service import (
    XlsxPaymentPlanFspExtraFieldsImportService,
)
from hope.apps.payment.xlsx.xlsx_verification_import_service import (
    XlsxVerificationImportService,
)
from hope.apps.program.api.serializers import PaymentPlanPurposeSerializer
from hope.apps.targeting.api.serializers import TargetPopulationListSerializer
from hope.contrib.vision.models import FundsCommitmentHeader
from hope.contrib.vision.services import FundsCommitmentAssignmentError, VisionService
from hope.models import (
    Account,
    AccountAttachment,
    Approval,
    ApprovalProcess,
    DeliveryMechanism,
    FileTemp,
    FinancialInstitution,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    FollowUpInstruction,
    Payment,
    PaymentList,
    PaymentPlan,
    PaymentPlanSupportingDocument,
    PaymentVerification,
    PaymentVerificationPlan,
    ProgramCycle,
    Rule,
    log_create,
)
from hope.models.payment_plan_purpose import PaymentPlanPurpose

if TYPE_CHECKING:
    from hope.models import User

logger = logging.getLogger(__name__)

XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

REJECT_PERMISSION_BY_STATUS: dict[str | None, Permissions] = {
    PaymentPlan.Status.IN_APPROVAL: Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
    PaymentPlan.Status.IN_AUTHORIZATION: Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
    PaymentPlan.Status.IN_REVIEW: Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
}


class ScopedPaymentListMixin:
    payment_list_url_kwarg = "payment_list_pk"

    def scoped_payment_list(self, pk: Any) -> PaymentList:
        return get_object_or_404(PaymentList, pk=pk, program_cycle__program=self.program)

    @cached_property
    def payment_list(self) -> PaymentList:
        return self.scoped_payment_list(self.kwargs.get(self.payment_list_url_kwarg))


class PaymentListMixin:
    serializer_class = PaymentListSerializer
    filter_backends = (
        filters.DjangoFilterBackend,
        OrderingFilter,
    )
    filterset_class = PaymentListFilter


class PaymentVerificationViewSet(
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
    PaymentListMixin,
    ScopedPaymentListMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    program_model_field = "program_cycle__program"
    payment_list_url_kwarg = "pk"
    queryset = (
        PaymentList.objects.filter(status__in=(PaymentList.Status.ACCEPTED, PaymentList.Status.FINISHED))
        .select_related("payment_plan__currency", "follow_up_instruction__currency")
        .order_by("-created_at")
    )
    PERMISSIONS = [Permissions.PAYMENT_VERIFICATION_VIEW_LIST]
    serializer_classes_by_action = {
        "list": PaymentVerificationPlanListSerializer,
        "retrieve": PaymentVerificationPlanDetailsSerializer,
        "create_payment_verification_plan": PaymentVerificationPlanCreateSerializer,
        "update_payment_verification_plan": PaymentVerificationPlanCreateSerializer,
        "activate_payment_verification_plan": PaymentVerificationPlanActivateSerializer,
        "finish_payment_verification_plan": PaymentVerificationPlanActivateSerializer,
        "discard_payment_verification_plan": PaymentVerificationPlanActivateSerializer,
        "invalid_payment_verification_plan": PaymentVerificationPlanActivateSerializer,
        "delete_payment_verification_plan": PaymentVerificationPlanActivateSerializer,
        "export_xlsx_payment_verification_plan": PaymentVerificationPlanActivateSerializer,
        "import_xlsx_payment_verification_plan": PaymentVerificationPlanImportSerializer,
        "sample_size": PaymentVerificationPlanCreateSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.PAYMENT_VERIFICATION_VIEW_LIST],
        "retrieve": [Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS],
        "create_payment_verification_plan": [Permissions.PAYMENT_VERIFICATION_CREATE],
        "update_payment_verification_plan": [Permissions.PAYMENT_VERIFICATION_UPDATE],
        "activate_payment_verification_plan": [Permissions.PAYMENT_VERIFICATION_ACTIVATE],
        "finish_payment_verification_plan": [Permissions.PAYMENT_VERIFICATION_FINISH],
        "discard_payment_verification_plan": [Permissions.PAYMENT_VERIFICATION_DISCARD],
        "invalid_payment_verification_plan": [Permissions.PAYMENT_VERIFICATION_INVALID],
        "delete_payment_verification_plan": [Permissions.PAYMENT_VERIFICATION_DELETE],
        "export_xlsx_payment_verification_plan": [Permissions.PAYMENT_VERIFICATION_EXPORT],
        "import_xlsx_payment_verification_plan": [Permissions.PAYMENT_VERIFICATION_IMPORT],
        "sample_size": [Permissions.PAYMENT_VERIFICATION_CREATE],
    }

    def get_object(self) -> PaymentList:
        return self.payment_list

    def get_verification_plan_object(self) -> PaymentVerificationPlan:
        return get_object_or_404(
            PaymentVerificationPlan,
            id=self.kwargs.get("verification_plan_id"),
            payment_list=self.payment_list,
        )

    @etag_decorator(PaymentVerificationListKeyConstructor)
    @cached_response(key_func=PaymentVerificationListKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=PaymentVerificationPlanCreateSerializer,
        responses=PaymentVerificationSampleSizeSerializer,
    )
    @action(detail=True, methods=["post"], url_path="sample-size")
    def sample_size(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        input_data = serializer.validated_data

        verifier = PaymentVerificationArgumentVerifier(input_data)
        verifier.verify("sampling")
        verifier.verify("verification_channel")

        payment_records = get_payment_records(payment_list, input_data.get("verification_channel"))
        sampling = Sampling(input_data, payment_list, payment_records)
        number_of_recipients, sample_size = sampling.generate_sampling()

        return Response(
            PaymentVerificationSampleSizeSerializer(
                {
                    "number_of_recipients": number_of_recipients,
                    "sample_size": sample_size,
                }
            ).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentVerificationPlanCreateSerializer,
        responses={201: PaymentVerificationPlanDetailsSerializer},
    )
    @action(detail=True, methods=["post"], url_path="create-verification-plan")
    @transaction.atomic
    def create_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create Payment Verification Plan."""
        payment_list = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        verification_plan = VerificationPlanCrudServices.create(payment_list, serializer.validated_data)
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            payment_list.program,
            old_object=None,
            new_object=verification_plan,
        )
        payment_list.refresh_from_db()
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_list).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        request=PaymentVerificationPlanCreateSerializer,
        responses={200: PaymentVerificationPlanDetailsSerializer},
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-verification-plan/(?P<verification_plan_id>[^/.]+)",
    )
    @transaction.atomic
    def update_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        pvp = self.get_verification_plan_object()
        serializer = self.get_serializer(pvp, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        old_payment_verification_plan = copy_model_object(pvp)
        pvp.verification_channel = serializer.validated_data.get("verification_channel")
        pvp.payment_record_verifications.all().delete()

        payment_verification_plan = VerificationPlanCrudServices.update(pvp, serializer.validated_data)

        payment_list.refresh_from_db()
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            getattr(payment_verification_plan.get_program, "pk", None),
            old_object=old_payment_verification_plan,
            new_object=payment_verification_plan,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_verification_plan.payment_list).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentVerificationPlanActivateSerializer,
        responses={200: PaymentVerificationPlanDetailsSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="activate-verification-plan/(?P<verification_plan_id>[^/.]+)",
    )
    @transaction.atomic
    def activate_payment_verification_plan(
        self, request: Request, verification_plan_id: str, *args: Any, **kwargs: Any
    ) -> Response:
        payment_list = self.get_object()
        try:
            payment_verification_plan = PaymentVerificationPlan.objects.select_for_update(nowait=True).get(
                pk=verification_plan_id, payment_list=payment_list
            )
        except PaymentVerificationPlan.DoesNotExist:
            raise Http404
        except DatabaseError:
            raise ValidationError("Payment verification plan is locked by another request.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        check_concurrency_version_in_mutation(serializer.validated_data.get("version"), payment_verification_plan)
        old_payment_verification_plan = copy_model_object(payment_verification_plan)

        payment_verification_plan = VerificationPlanStatusChangeServices(payment_verification_plan).activate()
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            getattr(payment_verification_plan.get_program, "pk", None),
            old_object=old_payment_verification_plan,
            new_object=payment_verification_plan,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_list).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentVerificationPlanActivateSerializer,
        responses={200: PaymentVerificationPlanDetailsSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="finish-verification-plan/(?P<verification_plan_id>[^/.]+)",
    )
    @transaction.atomic
    def finish_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        payment_verification_plan = self.get_verification_plan_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        check_concurrency_version_in_mutation(serializer.validated_data.get("version"), payment_verification_plan)
        old_payment_verification_plan = copy_model_object(payment_verification_plan)

        if payment_verification_plan.status != PaymentVerificationPlan.STATUS_ACTIVE:
            raise ValidationError("You can finish only ACTIVE verification")
        VerificationPlanStatusChangeServices(payment_verification_plan).finish()
        payment_verification_plan.refresh_from_db()
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            getattr(payment_verification_plan.get_program, "pk", None),
            old_object=old_payment_verification_plan,
            new_object=payment_verification_plan,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_list).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentVerificationPlanActivateSerializer,
        responses={200: PaymentVerificationPlanDetailsSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="discard-verification-plan/(?P<verification_plan_id>[^/.]+)",
    )
    @transaction.atomic
    def discard_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        payment_verification_plan = self.get_verification_plan_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        check_concurrency_version_in_mutation(serializer.validated_data.get("version"), payment_verification_plan)

        old_payment_verification_plan = copy_model_object(payment_verification_plan)

        payment_verification_plan = VerificationPlanStatusChangeServices(payment_verification_plan).discard()
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            getattr(payment_verification_plan.get_program, "pk", None),
            old_object=old_payment_verification_plan,
            new_object=payment_verification_plan,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_list).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentVerificationPlanActivateSerializer,
        responses={200: PaymentVerificationPlanDetailsSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="invalid-verification-plan/(?P<verification_plan_id>[^/.]+)",
    )
    @transaction.atomic
    def invalid_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        payment_verification_plan = self.get_verification_plan_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        check_concurrency_version_in_mutation(serializer.validated_data.get("version"), payment_verification_plan)
        old_payment_verification_plan = copy_model_object(payment_verification_plan)

        payment_verification_plan = VerificationPlanStatusChangeServices(payment_verification_plan).mark_invalid()
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            getattr(payment_verification_plan.get_program, "pk", None),
            old_object=old_payment_verification_plan,
            new_object=payment_verification_plan,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_list).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentVerificationPlanActivateSerializer,
        responses={200: PaymentVerificationPlanDetailsSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="delete-verification-plan/(?P<verification_plan_id>[^/.]+)",
    )
    @transaction.atomic
    def delete_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        payment_verification_plan = self.get_verification_plan_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        check_concurrency_version_in_mutation(serializer.validated_data.get("version"), payment_verification_plan)
        program_id = getattr(payment_verification_plan.get_program, "pk", None)
        old_payment_verification_plan = copy_model_object(payment_verification_plan)

        VerificationPlanCrudServices.delete(payment_verification_plan)
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            program_id,
            old_object=old_payment_verification_plan,
            new_object=None,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_list).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentVerificationPlanActivateSerializer,
        responses={200: PaymentVerificationPlanDetailsSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="export-xlsx/(?P<verification_plan_id>[^/.]+)",
    )
    @transaction.atomic
    def export_xlsx_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        payment_verification_plan = self.get_verification_plan_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        check_concurrency_version_in_mutation(serializer.validated_data.get("version"), payment_verification_plan)
        program_id = getattr(payment_verification_plan.get_program, "pk", None)
        old_payment_verification_plan = copy_model_object(payment_verification_plan)

        payment_verification_plan = VerificationPlanStatusChangeServices(payment_verification_plan).export_xlsx(
            str(request.user.pk)
        )
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            program_id,
            old_object=old_payment_verification_plan,
            new_object=payment_verification_plan,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_list).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentVerificationPlanImportSerializer,
        responses={
            200: PaymentVerificationPlanDetailsSerializer,
            400: XlsxErrorSerializer,
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="import-xlsx/(?P<verification_plan_id>[^/.]+)",
        parser_classes=[DictDrfNestedParser],
    )
    @transaction.atomic
    def import_xlsx_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        payment_verification_plan = self.get_verification_plan_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]
        check_concurrency_version_in_mutation(serializer.validated_data.get("version"), payment_verification_plan)
        program_id = getattr(payment_verification_plan.get_program, "pk", None)
        old_payment_verification_plan = copy_model_object(payment_verification_plan)

        import_service = XlsxVerificationImportService(payment_verification_plan, file)
        import_service.open_workbook()
        import_service.validate()
        if len(import_service.errors):
            return Response(
                data=XlsxErrorSerializer(import_service.errors, many=True, context={"request": request}).data,
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment_verification_plan = VerificationPlanStatusChangeServices(payment_verification_plan).import_xlsx(file)

        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            program_id,
            old_object=old_payment_verification_plan,
            new_object=payment_verification_plan,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_list).data,
            status=status.HTTP_200_OK,
        )


class PaymentVerificationRecordViewSet(
    CountActionMixin, ProgramMixin, SerializerActionMixin, ScopedPaymentListMixin, BaseViewSet
):
    queryset = Payment.objects.all()
    program_model_field = "program_cycle__program"
    payment_list_url_kwarg = "payment_verification_pk"
    PERMISSIONS = [Permissions.PAYMENT_VERIFICATION_VIEW_LIST]
    serializer_classes_by_action = {
        "list": PaymentRowSerializer,
        "retrieve": PaymentDetailSerializer,
        "partial_update": PaymentVerificationUpdateSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS],
        "retrieve": [Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS],
        "partial_update": [Permissions.PAYMENT_VERIFICATION_VERIFY],
    }
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PaymentVerificationRecordFilter

    def get_object(self) -> PaymentList:
        return self.payment_list

    def get_verification_record(self) -> Payment:
        return get_object_or_404(
            with_payment_related_data(Payment.objects.all()),
            id=self.kwargs.get("pk"),
            parent=self.payment_list,
        )

    def get_queryset(self) -> QuerySet:
        has_verification = Exists(PaymentVerification.objects.filter(payment=OuterRef("pk")))
        return with_payment_related_data(self.payment_list.eligible_payments.filter(has_verification))

    @extend_schema(
        responses={
            200: PaymentRowSerializer(many=True),
        },
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return list of verification records."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment = self.get_verification_record()
        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=PaymentVerificationUpdateSerializer,
        responses={200: PaymentDetailSerializer},
    )
    @transaction.atomic
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Update verification amount."""
        payment = self.get_verification_record()
        payment_verification = payment.payment_verifications.first()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        check_concurrency_version_in_mutation(serializer.validated_data.get("version"), payment_verification)
        received_amount = serializer.validated_data["received_amount"]
        received = serializer.validated_data["received"]
        old_payment_verification = copy_model_object(payment_verification)
        if (
            payment_verification.payment_verification_plan.verification_channel
            != PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL
        ):
            raise ValidationError("You can only update status of payment verification for MANUAL verification method")
        if payment_verification.payment_verification_plan.status != PaymentVerificationPlan.STATUS_ACTIVE:
            raise ValidationError(
                f"You can only update status of payment verification for "
                f"{PaymentVerificationPlan.STATUS_ACTIVE} cash plan verification"
            )
        if not payment_verification.is_manually_editable:
            raise ValidationError("You can only edit payment verification in first 10 minutes")
        delivered_amount = payment_verification.payment.delivered_quantity

        if received is None and received_amount is not None and received_amount == 0:
            raise ValidationError("You can't set received_amount {received_amount} and not set received to NO")
        if received is None and received_amount is not None:
            raise ValidationError("You can't set received_amount {received_amount} and not set received to YES")
        if received_amount == 0 and received:
            raise ValidationError("If 'Amount Received' equals to 0, please set status as 'Not Received'")
        if received_amount is not None and received_amount != 0 and not received:
            raise ValidationError(f"If received_amount({received_amount}) is not 0, you should set received to YES")

        payment_verification.status = from_received_to_status(received, received_amount, delivered_amount)  # type: ignore[arg-type]
        payment_verification.status_date = timezone.now()
        payment_verification.received_amount = received_amount
        payment_verification.save()
        payment_verification_plan = payment_verification.payment_verification_plan
        calculate_counts(payment_verification_plan)
        payment_verification_plan.save()
        log_create(
            PaymentVerification.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            getattr(payment_verification_plan.get_program, "pk", None),
            old_object=old_payment_verification,
            new_object=payment_verification,
        )
        payment.refresh_from_db()

        return Response(
            PaymentDetailSerializer(payment, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class PaymentListViewSet(
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
    PaymentListMixin,
    ScopedPaymentListMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    BaseViewSet,
):
    BLOCKED_ACTIONS_FOR_INSTRUCTION_MANAGED = {
        "destroy",
        "lock",
        "unlock",
    }
    program_model_field = "program_cycle__program"
    queryset = (
        PaymentList.objects.select_related(
            "program_cycle__program", "payment_plan__currency", "follow_up_instruction__currency"
        )
        .prefetch_related(
            Prefetch(
                "child_plans",
                queryset=PaymentList.objects.select_related("payment_plan", "follow_up_instruction"),
            )
        )
        # The tables group rows under their payment plan; `ordering_fields = "__all__"` sorts by model
        # fields and annotations only.
        .annotate(payment_plan_name=F("payment_plan__name"))
        .order_by("-created_at")
    )
    filterset_class = PaymentListListFilter
    http_method_names = ["get", "post", "delete"]
    PERMISSIONS = [Permissions.PM_VIEW_LIST]
    serializer_classes_by_action = {
        "list": PaymentListListSerializer,
        "retrieve": PaymentListDetailSerializer,
        "create": PaymentListCreateUpdateSerializer,
        "exclude_beneficiaries": PaymentListExcludeBeneficiariesSerializer,
        "apply_engine_formula": ApplyEngineFormulaSerializer,
        "entitlement_flat_amount": ApplyFlatAmountEntitlementSerializer,
        "entitlement_import_xlsx": PaymentPlanImportFileSerializer,
        "fsp_xlsx_template_list": FSPXlsxTemplateSerializer,
    }
    permissions_by_action = {
        "list": [
            Permissions.PM_VIEW_LIST,
        ],
        "retrieve": [
            Permissions.PM_VIEW_DETAILS,
        ],
        "create": [Permissions.PM_CREATE],
        "destroy": [Permissions.PM_CREATE],
        "exclude_beneficiaries": [Permissions.PM_EXCLUDE_BENEFICIARIES_FROM_FOLLOW_UP_PP],
        "apply_engine_formula": [Permissions.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS],
        "lock": [Permissions.PM_LOCK_AND_UNLOCK],
        "unlock": [Permissions.PM_LOCK_AND_UNLOCK],
        "entitlement_export_xlsx": [Permissions.PM_VIEW_LIST],
        "entitlement_import_xlsx": [Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS],
        "entitlement_flat_amount": [
            Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS,
            Permissions.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS,
        ],
        "fsp_xlsx_template_list": [Permissions.PM_EXPORT_XLSX_FOR_FSP],
    }

    def get_object(self) -> PaymentList:
        payment_list = self.scoped_payment_list(self.kwargs.get("pk"))
        if payment_list.is_instruction_managed and self.action in self.BLOCKED_ACTIONS_FOR_INSTRUCTION_MANAGED:
            raise ValidationError("This Payment List is managed by a Follow Up Instruction.")
        return payment_list

    @etag_decorator(PaymentListListKeyConstructor)
    @cached_response(key_func=PaymentListListKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if "target_population_id" not in request.data:
            raise ValidationError("target_population_id is required")
        payment_list = self.scoped_payment_list(request.data.get("target_population_id"))
        # Despite the name this updates an existing plan, so the serializer gets the instance:
        # that is what lets the currency field keep a plan on its deprecated row when the client
        # echoes back the code a GET handed out. The view still saves via PaymentListService.
        serializer = self.get_serializer(payment_list, data=request.data, context={"payment_list": payment_list})
        serializer.is_valid(raise_exception=True)
        old_payment_list = copy_model_object(payment_list)

        payment_list = PaymentListService(payment_list=payment_list).open()
        log_create(
            mapping=PaymentList.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_list.program,
            old_object=old_payment_list,
            new_object=payment_list,
        )
        response_serializer = PaymentListDetailSerializer(payment_list, context={"request": request})
        return Response(
            data=response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        old_payment_list = copy_model_object(payment_list)
        payment_list = PaymentListService(payment_list=payment_list).delete()
        log_create(
            mapping=PaymentList.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_list.program.pk,
            old_object=old_payment_list,
            new_object=payment_list,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=PaymentListExcludeBeneficiariesSerializer,
        responses={200: PaymentListDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="exclude-beneficiaries")
    @transaction.atomic
    def exclude_beneficiaries(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()

        if payment_list.status not in (
            PaymentList.Status.OPEN,
            PaymentList.Status.LOCKED,
        ):
            raise ValidationError("Beneficiary can be excluded only for 'Open' or 'Locked' status of Payment List")

        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        payment_list_exclude_beneficiaries_async_task(
            payment_list,
            serializer.validated_data["excluded_households_ids"],
            serializer.validated_data.get("exclusion_reason", ""),
            str(request.user.pk),
        )

        flow = PaymentListFlow(payment_list)
        flow.background_action_status_excluding_beneficiaries()
        payment_list.exclude_household_error = ""
        payment_list.save(update_fields=["background_action_status", "exclude_household_error"])

        payment_list.refresh_from_db()

        response_serializer = PaymentListDetailSerializer(payment_list, context={"request": request})
        return Response(
            data=response_serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"])
    @transaction.atomic
    def lock(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        old_payment_list = copy_model_object(payment_list)
        payment_list = PaymentListService(payment_list).execute_update_status_action(
            input_data={"action": PaymentList.Action.LOCK}, user=request.user
        )
        log_create(
            mapping=PaymentList.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_list.program.pk,
            old_object=old_payment_list,
            new_object=payment_list,
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Payment List locked"})

    @action(detail=True, methods=["get"])
    @transaction.atomic
    def unlock(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        old_payment_list = copy_model_object(payment_list)
        payment_list = PaymentListService(payment_list).execute_update_status_action(
            input_data={"action": PaymentList.Action.UNLOCK}, user=request.user
        )
        log_create(
            mapping=PaymentList.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_list.program.pk,
            old_object=old_payment_list,
            new_object=payment_list,
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Payment List unlocked"})

    @extend_schema(
        request=ApplyEngineFormulaSerializer,
        responses={200: PaymentListDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="apply-engine-formula")
    @transaction.atomic
    def apply_engine_formula(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        if payment_list.plan_type == PaymentList.PlanType.FOLLOW_UP:
            raise ValidationError("Entitlement actions are not available for Follow Up Payment Lists.")
        serializer = self.get_serializer(
            data=request.data,
        )
        if serializer.is_valid():
            engine_formula_rule_id = serializer.validated_data["engine_formula_rule_id"]
            if version := serializer.validated_data.get("version"):
                check_concurrency_version_in_mutation(version, payment_list)
            engine_rule = get_object_or_404(Rule, id=engine_formula_rule_id, allowed_business_areas=self.business_area)
            if payment_list.status not in PaymentList.CAN_RUN_ENGINE_FORMULA_FOR_ENTITLEMENT:
                raise ValidationError(f"Not allowed to run engine formula within status {payment_list.status}.")
            if not engine_rule.enabled or engine_rule.deprecated:
                raise ValidationError("This engine rule is not enabled or is deprecated.")
            # PaymentList entitlement
            old_payment_list = copy_model_object(payment_list)
            if payment_list.background_action_status == PaymentList.BackgroundActionStatus.RULE_ENGINE_RUN:
                raise ValidationError("Rule Engine run in progress")
            flow = PaymentListFlow(payment_list)
            flow.background_action_status_steficon_run()
            payment_list.save()
            user_id = str(request.user.pk)
            transaction.on_commit(lambda: payment_list_apply_engine_rule_async_task(payment_list, engine_rule, user_id))

            log_create(
                mapping=PaymentList.ACTIVITY_LOG_MAPPING,
                business_area_field="business_area",
                user=request.user,
                programs=payment_list.program.pk,
                old_object=old_payment_list,
                new_object=payment_list,
            )
            payment_list.refresh_from_db(fields=["background_action_status"])
            response_serializer = PaymentListDetailSerializer(payment_list, context={"request": request})
            return Response(
                data=response_serializer.data,
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["get"],
        url_path="entitlement-export-xlsx",
    )
    @transaction.atomic
    def entitlement_export_xlsx(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        if payment_list.plan_type == PaymentList.PlanType.FOLLOW_UP:
            raise ValidationError("Entitlement actions are not available for Follow Up Payment Lists.")
        old_payment_list = copy_model_object(payment_list)

        if payment_list.status != PaymentList.Status.LOCKED:
            raise ValidationError("You can only export Payment List for LOCKED Payment List")

        payment_list = PaymentListService(payment_list=payment_list).export_xlsx(user_id=str(request.user.pk))
        log_create(
            mapping=PaymentList.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_list.program.pk,
            old_object=old_payment_list,
            new_object=payment_list,
        )
        return Response(
            data=PaymentListDetailSerializer(payment_list, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentPlanImportFileSerializer,
        responses={200: PaymentListDetailSerializer, 400: XlsxErrorSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="entitlement-import-xlsx",
        parser_classes=[DictDrfNestedParser],
    )
    @transaction.atomic
    def entitlement_import_xlsx(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        if payment_list.plan_type == PaymentList.PlanType.FOLLOW_UP:
            raise ValidationError("Entitlement actions are not available for Follow Up Payment Lists.")
        if payment_list.status != PaymentList.Status.LOCKED:
            raise ValidationError("User can only import for LOCKED Payment List")
        if payment_list.background_action_status == PaymentList.BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS:
            raise ValidationError("Import in progress")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]
        with transaction.atomic():
            import_service = XlsxPaymentListImportService(payment_list, file)
            import_service.open_workbook()
            import_service.validate()
            if import_service.errors:
                return Response(
                    data=XlsxErrorSerializer(import_service.errors, many=True, context={"request": request}).data,
                    status=status.HTTP_400_BAD_REQUEST,
                )
            old_payment_list = copy_model_object(payment_list)
            if old_payment_list.imported_file:
                old_payment_list.imported_file = copy_model_object(payment_list.imported_file)
            flow = PaymentListFlow(payment_list)
            flow.background_action_status_xlsx_importing_entitlements()
            payment_list.save()
            payment_list = import_service.create_import_xlsx_file(request.user)

            user_id = str(request.user.pk)
            transaction.on_commit(lambda: import_payment_list_from_xlsx_async_task(payment_list, user_id))
            log_create(
                mapping=PaymentList.ACTIVITY_LOG_MAPPING,
                business_area_field="business_area",
                user=request.user,
                programs=payment_list.program.pk,
                old_object=old_payment_list,
                new_object=payment_list,
            )
        return Response(
            data=PaymentListDetailSerializer(payment_list, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=ApplyFlatAmountEntitlementSerializer,
        responses={200: PaymentListDetailSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="entitlement-flat-amount",
    )
    @transaction.atomic
    def entitlement_flat_amount(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        if payment_list.plan_type == PaymentList.PlanType.FOLLOW_UP:
            raise ValidationError("Entitlement actions are not available for Follow Up Payment Lists.")
        serializer = self.get_serializer(
            data=request.data,
        )
        if payment_list.status != PaymentList.Status.LOCKED:
            raise ValidationError("User can only set entitlements for LOCKED Payment List")
        if payment_list.background_action_status is not None:
            raise ValidationError("Import in progress")

        if serializer.is_valid():
            flat_amount_value = serializer.validated_data["flat_amount_value"]
            if version := serializer.validated_data.get("version"):
                check_concurrency_version_in_mutation(version, payment_list)
            # PaymentList entitlement
            flow = PaymentListFlow(payment_list)
            flow.background_action_status_importing_entitlements()
            payment_list.flat_amount_value = flat_amount_value
            payment_list.save()
            payment_list.refresh_from_db(fields=["background_action_status", "flat_amount_value"])
            flat_amount_user_id = str(request.user.pk)
            transaction.on_commit(
                lambda: payment_list_set_entitlement_flat_amount_async_task(payment_list, flat_amount_user_id)
            )
            response_serializer = PaymentListDetailSerializer(payment_list, context={"request": request})
            return Response(
                data=response_serializer.data,
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={200: FSPXlsxTemplateSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="fsp-xlsx-template-list")
    @transaction.atomic
    def fsp_xlsx_template_list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        qs = FinancialServiceProviderXlsxTemplate.objects.filter(
            financial_service_providers__allowed_business_areas__slug=self.business_area_slug
        ).order_by("name")

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = FSPXlsxTemplateSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(
            data=FSPXlsxTemplateSerializer(qs, many=True).data,
            status=status.HTTP_200_OK,
        )


class PaymentListGlobalViewSet(
    BusinessAreaProgramsAccessMixin,
    SerializerActionMixin,
    CountActionMixin,
    PaymentListMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = (
        PaymentList.objects.exclude(status__in=PaymentList.PRE_PAYMENT_LIST_STATUSES)
        .select_related("payment_plan__currency", "follow_up_instruction__currency")
        .prefetch_related(
            Prefetch(
                "child_plans",
                queryset=PaymentList.objects.select_related("payment_plan", "follow_up_instruction"),
            )
        )
        .order_by("-created_at")
    )
    serializer_classes_by_action = {
        "list": PaymentListListSerializer,
    }
    PERMISSIONS = [Permissions.PM_VIEW_LIST]
    program_model_field = "program_cycle__program"
    filterset_class = PaymentListOfficeSearchFilter


class FollowUpInstructionViewSet(
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    program_model_field = "program"
    queryset = (
        FollowUpInstruction.objects.select_related("business_area", "program", "created_by", "currency")
        .prefetch_related("payment_lists__source_payment_list")
        .order_by("-created_at")
    )
    PERMISSIONS = [Permissions.PM_VIEW_LIST]
    serializer_classes_by_action = {
        "list": FollowUpInstructionListSerializer,
        "retrieve": FollowUpInstructionDetailSerializer,
        "create": FollowUpInstructionCreateSerializer,
        "delivery_import_xlsx": PaymentPlanImportFileSerializer,
        "reject": AcceptanceProcessSerializer,
        "approve": AcceptanceProcessSerializer,
        "authorize": AcceptanceProcessSerializer,
        "mark_as_released": AcceptanceProcessSerializer,
        "abort": PaymentPlanAbortSerializer,
        "close": PaymentPlanCloseSerializer,
        "custom_exchange_rate": ApplyCustomExchangeRateSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.PM_VIEW_LIST],
        "retrieve": [Permissions.PM_VIEW_DETAILS],
        "create": [Permissions.PM_CREATE],
        "lock": [Permissions.PM_LOCK_AND_UNLOCK],
        "unlock": [Permissions.PM_LOCK_AND_UNLOCK],
        "lock_fsp": [Permissions.PM_LOCK_AND_UNLOCK_FSP],
        "unlock_fsp": [Permissions.PM_LOCK_AND_UNLOCK_FSP],
        "send_for_approval": [Permissions.PM_SEND_FOR_APPROVAL],
        "approve": [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        "authorize": [Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE],
        "mark_as_released": [Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW],
        "delivery_export_xlsx": [Permissions.PM_PAYMENT_PLAN_EXPORT_XLSX],
        "delivery_import_xlsx": [Permissions.PM_IMPORT_XLSX_WITH_RECONCILIATION],
        "ready_for_closure": [Permissions.PM_MARK_READY_FOR_CLOSURE],
        "send_back_to_finished": [Permissions.PM_MARK_READY_FOR_CLOSURE],
        "close": [Permissions.PM_CLOSE_FINISHED],
        "abort": [Permissions.PM_ABORT],
        "reactivate_abort": [Permissions.PM_REACTIVATE_ABORT],
        "export_pdf_payment_plan_summary": [Permissions.PM_EXPORT_PDF_SUMMARY],
        "custom_exchange_rate": [Permissions.PM_CUSTOM_EXCHANGE_RATE],
    }

    def get_object(self) -> FollowUpInstruction:
        return get_object_or_404(self.get_queryset(), id=self.kwargs.get("pk"))

    def _detail_response(self, instruction: FollowUpInstruction, status_code: int = status.HTTP_200_OK) -> Response:
        return Response(
            data=FollowUpInstructionDetailSerializer(instruction, context={"request": self.request}).data,
            status=status_code,
        )

    @staticmethod
    def _request_user(request: Request) -> "User":
        return cast("User", request.user)

    @extend_schema(request=ApplyCustomExchangeRateSerializer, responses={200: FollowUpInstructionDetailSerializer})
    @action(detail=True, methods=["post"], url_path="custom-exchange-rate")
    @transaction.atomic
    def custom_exchange_rate(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        instruction = FollowUpInstruction.objects.select_for_update().get(pk=self.get_object().pk)
        if instruction.status not in (FollowUpInstruction.Status.OPEN, FollowUpInstruction.Status.IN_REVIEW):
            raise ValidationError("Exchange rate can be changed only while the instruction is OPEN or IN_REVIEW")
        check_concurrency_version_in_mutation(data.get("version"), instruction)
        if instruction.background_action_status not in (None, *FollowUpInstruction.BACKGROUND_ACTION_ERROR_STATES):
            raise ValidationError("Wait for the current instruction action to finish before changing the rate")

        user = self._request_user(request)
        old_instruction = cast("FollowUpInstruction", copy_model_object(instruction))
        custom_rate = data.get("custom_exchange_rate")
        instruction.exchange_rate = custom_rate if custom_rate is not None else data["unore_exchange_rate"]
        instruction.custom_exchange_rate = custom_rate is not None
        instruction.custom_exchange_rate_set_by = user if custom_rate is not None else None
        instruction.save(
            update_fields=[
                "exchange_rate",
                "custom_exchange_rate",
                "custom_exchange_rate_set_by",
                "version",
                "updated_at",
            ]
        )
        log_follow_up_instruction_change(instruction, old_instruction, str(user.pk))
        instruction = cast(
            "FollowUpInstruction",
            recalculate_owner_exchange_rate_async_task(instruction, str(user.pk), fetch_unore_rate=False),
        )
        return self._detail_response(instruction)

    @transaction.atomic
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self._request_user(request)
        instruction = FollowUpInstructionService(self.program).create(
            user=user,
            payment_plan_ids=[
                str(payment_plan_id) for payment_plan_id in serializer.validated_data["payment_plan_ids"]
            ],
            dispersion_start_date=serializer.validated_data["dispersion_start_date"],
            dispersion_end_date=serializer.validated_data["dispersion_end_date"],
        )
        return self._detail_response(instruction, status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    @transaction.atomic
    def lock(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = self.get_object()
        user = self._request_user(request)
        instruction = FollowUpInstructionService(instruction=instruction).execute_payment_list_action(
            PaymentList.Action.LOCK,
            user,
        )
        return self._detail_response(instruction)

    @action(detail=True, methods=["get"])
    @transaction.atomic
    def unlock(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = self.get_object()
        user = self._request_user(request)
        instruction = FollowUpInstructionService(instruction=instruction).execute_payment_list_action(
            PaymentList.Action.UNLOCK,
            user,
        )
        return self._detail_response(instruction)

    @action(detail=True, methods=["get"], url_path="lock-fsp")
    @transaction.atomic
    def lock_fsp(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = self.get_object()
        user = self._request_user(request)
        instruction = FollowUpInstructionService(instruction=instruction).execute_payment_list_action(
            PaymentList.Action.LOCK_FSP,
            user,
        )
        return self._detail_response(instruction)

    @action(detail=True, methods=["get"], url_path="unlock-fsp")
    @transaction.atomic
    def unlock_fsp(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = self.get_object()
        user = self._request_user(request)
        instruction = FollowUpInstructionService(instruction=instruction).execute_payment_list_action(
            PaymentList.Action.UNLOCK_FSP,
            user,
        )
        return self._detail_response(instruction)

    @action(detail=True, methods=["get"], url_path="send-for-approval")
    @transaction.atomic
    def send_for_approval(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = self.get_object()
        user = self._request_user(request)
        instruction = FollowUpInstructionService(instruction=instruction).send_for_approval(user)
        return self._detail_response(instruction)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def reject(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # The stage permission must match the status the reject is recorded on, so read it from the locked row.
        instruction = FollowUpInstruction.objects.select_for_update().get(pk=self.get_object().pk)
        reject_permission = REJECT_PERMISSION_BY_STATUS.get(instruction.status)
        if reject_permission and not request.user.has_perm(reject_permission.value, instruction.program):
            raise PermissionDenied(detail={"required_permissions": [reject_permission.value]})
        user = self._request_user(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instruction = FollowUpInstructionService(instruction=instruction).acceptance_process(
            PaymentList.Action.REJECT.value,
            user,
            serializer.validated_data.get("comment"),
        )
        return self._detail_response(instruction)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def approve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = self.get_object()
        user = self._request_user(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instruction = FollowUpInstructionService(instruction=instruction).acceptance_process(
            PaymentList.Action.APPROVE.value,
            user,
            serializer.validated_data.get("comment"),
        )
        return self._detail_response(instruction)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def authorize(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = self.get_object()
        user = self._request_user(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instruction = FollowUpInstructionService(instruction=instruction).acceptance_process(
            PaymentList.Action.AUTHORIZE.value,
            user,
            serializer.validated_data.get("comment"),
        )
        return self._detail_response(instruction)

    @action(detail=True, methods=["post"], url_path="mark-as-released")
    @transaction.atomic
    def mark_as_released(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = self.get_object()
        user = self._request_user(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instruction = FollowUpInstructionService(instruction=instruction).acceptance_process(
            PaymentList.Action.REVIEW.value,
            user,
            serializer.validated_data.get("comment"),
        )
        return self._detail_response(instruction)

    @action(detail=True, methods=["get"], url_path="delivery-export-xlsx")
    @transaction.atomic
    def delivery_export_xlsx(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = self.get_object()
        instruction = FollowUpInstructionService(instruction=instruction).delivery_export_xlsx(
            self._request_user(request)
        )
        return self._detail_response(instruction)

    @extend_schema(
        request=PaymentPlanImportFileSerializer,
        responses={200: FollowUpInstructionDetailSerializer, 400: XlsxErrorSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="delivery-import-xlsx",
        parser_classes=[DictDrfNestedParser],
    )
    @transaction.atomic
    def delivery_import_xlsx(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        file = serializer.validated_data["file"]

        import_service = XlsxFollowUpInstructionReconciliationImportService(instruction, file)
        try:
            import_service.open_workbook()
        except BadZipFile:
            raise ValidationError(
                "Wrong file type or password protected .zip file. Upload another file, or remove the password."
            )
        import_service.validate()
        if import_service.errors:
            return Response(
                data=XlsxErrorSerializer(import_service.errors, many=True, context={"request": request}).data,
                status=status.HTTP_400_BAD_REQUEST,
            )

        file.seek(0)
        instruction = FollowUpInstructionService(instruction=instruction).import_delivery_xlsx(
            self._request_user(request), file
        )
        return self._detail_response(instruction)

    @extend_schema(request=None, responses={200: FollowUpInstructionDetailSerializer})
    @action(detail=True, methods=["post"], url_path="ready-for-closure")
    def ready_for_closure(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = FollowUpInstructionService(instruction=self.get_object()).ready_for_closure(
            self._request_user(request)
        )
        return self._detail_response(instruction)

    @extend_schema(request=None, responses={200: FollowUpInstructionDetailSerializer})
    @action(detail=True, methods=["post"], url_path="send-back-to-finished")
    def send_back_to_finished(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = FollowUpInstructionService(instruction=self.get_object()).send_back_to_finished(
            self._request_user(request)
        )
        return self._detail_response(instruction)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def close(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instruction = FollowUpInstructionService(instruction=instruction).close(
            self._request_user(request), serializer.validated_data.get("closure_comment")
        )
        return self._detail_response(instruction)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def abort(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = self.get_object()
        user = self._request_user(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instruction = FollowUpInstructionService(instruction=instruction).abort(
            user, serializer.validated_data.get("abort_comment")
        )
        return self._detail_response(instruction)

    @action(detail=True, methods=["get"], url_path="reactivate-abort")
    @transaction.atomic
    def reactivate_abort(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = self.get_object()
        instruction = FollowUpInstructionService(instruction=instruction).reactivate_abort(self._request_user(request))
        return self._detail_response(instruction)

    @extend_schema(request=None, responses={200: FollowUpInstructionDetailSerializer})
    @action(detail=True, methods=["get"], url_path="export-pdf-payment-plan-summary")
    def export_pdf_payment_plan_summary(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instruction = self.get_object()
        if instruction.status not in FollowUpInstruction.SUMMARY_PDF_STATUSES:
            raise ValidationError(
                f"Export PDF is possible only within Status IN_REVIEW, ACCEPTED or FINISHED, got {instruction.status}"
            )
        export_pdf_follow_up_instruction_summary_async_task(instruction, str(request.user.pk))
        return self._detail_response(instruction)


class TargetPopulationViewSet(
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
    PaymentListMixin,
    ScopedPaymentListMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    BaseViewSet,
):
    program_model_field = "program_cycle__program"
    queryset = (
        PaymentList.objects.select_related("payment_plan__currency", "created_by")
        .annotate(payment_plan_name=F("payment_plan__name"))
        .order_by("-created_at")
    )
    http_method_names = ["get", "post", "patch", "delete"]
    serializer_classes_by_action = {
        "list": TargetPopulationListSerializer,
        "retrieve": TargetPopulationDetailSerializer,
        "create": TargetPopulationCreateSerializer,
        "partial_update": TargetPopulationCreateSerializer,
        "copy": TargetPopulationCopySerializer,
        "apply_engine_formula": ApplyEngineFormulaSerializer,
        "pending_payments": PendingPaymentSerializer,  # to show list of households in target population
    }
    permissions_by_action = {
        "list": [Permissions.TARGETING_VIEW_LIST],
        "retrieve": [Permissions.TARGETING_VIEW_DETAILS],
        "create": [Permissions.TARGETING_CREATE],
        "partial_update": [Permissions.TARGETING_UPDATE],
        "destroy": [Permissions.TARGETING_REMOVE],
        "copy": [Permissions.TARGETING_DUPLICATE],
        "apply_engine_formula": [Permissions.TARGETING_UPDATE],
        "pending_payments": [Permissions.TARGETING_VIEW_DETAILS],
        "pending_payments_count": [Permissions.TARGETING_VIEW_DETAILS],
        "lock": [Permissions.TARGETING_LOCK],
        "unlock": [Permissions.TARGETING_UNLOCK],
        "rebuild": [Permissions.TARGETING_LOCK],
        "mark_ready": [Permissions.TARGETING_CREATE, Permissions.TARGETING_SEND],
    }
    filterset_class = TargetPopulationFilter

    def get_object(self) -> PaymentList:
        return self.scoped_payment_list(self.kwargs.get("pk"))

    @etag_decorator(TargetPopulationListKeyConstructor)
    @cached_response(key_func=TargetPopulationListKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_list = self.get_object()
        old_payment_list = copy_model_object(payment_list)
        payment_list = PaymentListService(payment_list=payment_list).delete()
        log_create(
            mapping=PaymentList.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_list.program.pk,
            old_object=old_payment_list,
            new_object=payment_list,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    @transaction.atomic
    def lock(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        tp = self.get_object()
        old_tp = copy_model_object(tp)
        payment_list = PaymentListService(tp).execute_update_status_action(
            input_data={"action": PaymentList.Action.TP_LOCK}, user=request.user
        )
        log_create(
            mapping=PaymentList.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_list.program.pk,
            old_object=old_tp,
            new_object=tp,
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Target Population locked"})

    @action(detail=True, methods=["get"])
    @transaction.atomic
    def unlock(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        tp = self.get_object()
        old_tp = copy_model_object(tp)

        payment_list = PaymentListService(tp).execute_update_status_action(
            input_data={"action": PaymentList.Action.TP_UNLOCK}, user=request.user
        )
        log_create(
            mapping=PaymentList.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_list.program.pk,
            old_object=old_tp,
            new_object=tp,
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Target Population unlocked"})

    @action(detail=True, methods=["get"])
    @transaction.atomic
    def rebuild(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        tp = self.get_object()
        old_tp = copy_model_object(tp)

        payment_list = PaymentListService(tp).execute_update_status_action(
            input_data={"action": PaymentList.Action.TP_REBUILD}, user=request.user
        )
        log_create(
            mapping=PaymentList.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_list.program.pk,
            old_object=old_tp,
            new_object=tp,
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Target Population rebuilding"})

    @extend_schema(
        responses={200: PendingPaymentSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="ordering",
            ),
        ],
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="pending-payments",
        filter_backends=[],
    )
    @transaction.atomic
    def pending_payments(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        tp = self.get_object()
        queryset = tp.payment_items.select_related("household", "head_of_household", "household__admin2").all()

        filterset = PendingPaymentFilter(request.GET, queryset=queryset)
        queryset = filterset.qs

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        responses={
            status.HTTP_200_OK: inline_serializer("CountResponse", fields={"count": serializers.IntegerField()})
        },
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="pending-payments/count",
        filter_backends=[],
    )
    def pending_payments_count(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        tp = self.get_object()
        pending_payments_count = tp.payment_items.count()
        return Response({"count": pending_payments_count}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["get"],
        url_path="mark-ready",
    )
    @transaction.atomic
    def mark_ready(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        tp = self.get_object()
        old_tp = copy_model_object(tp)

        payment_list = PaymentListService(tp).execute_update_status_action(
            input_data={"action": PaymentList.Action.DRAFT}, user=request.user
        )
        log_create(
            mapping=PaymentList.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_list.program.pk,
            old_object=old_tp,
            new_object=tp,
        )
        return Response(
            status=status.HTTP_200_OK,
            data={"message": "Target Population ready for Payment List"},
        )

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def copy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        data = dict(request.data)
        data["target_population_id"] = kwargs.get("pk")

        serializer = self.get_serializer(
            data=data,
        )
        if serializer.is_valid():
            name = serializer.validated_data["name"].strip()
            payment_list_id = serializer.validated_data["target_population_id"]
            program_cycle_id = serializer.validated_data["program_cycle_id"]
            payment_plan_id = serializer.validated_data["payment_plan_id"]
            purposes = serializer.validated_data["payment_plan_purposes"]
            payment_list = self.scoped_payment_list(payment_list_id)
            program_cycle = get_object_or_404(ProgramCycle, pk=program_cycle_id, program=self.program)
            program = program_cycle.program

            if program_cycle.status == ProgramCycle.FINISHED:
                raise ValidationError("Not possible to assign Finished Program Cycle to Targeting.")
            if PaymentList.objects.filter(name=name, program_cycle=program_cycle, is_removed=False).exists():
                raise ValidationError(
                    f"Target Population with name: {name} and program cycle: {program_cycle.title} already exists."
                )
            if not (payment_plan := PaymentPlan.objects.filter(pk=payment_plan_id, cycle=program_cycle).first()):
                raise ValidationError("Payment Plan does not exist in the given Programme Cycle.")

            payment_list_copy = PaymentList(
                name=name,
                created_by=user,
                business_area=payment_list.business_area,
                status=PaymentList.Status.TP_OPEN,
                status_date=timezone.now(),
                start_date=program_cycle.start_date,
                end_date=program_cycle.end_date,
                build_status=PaymentList.BuildStatus.BUILD_STATUS_PENDING,
                built_at=timezone.now(),
                male_children_count=payment_list.male_children_count,
                female_children_count=payment_list.female_children_count,
                male_adults_count=payment_list.male_adults_count,
                female_adults_count=payment_list.female_adults_count,
                total_households_count=payment_list.total_households_count,
                total_individuals_count=payment_list.total_individuals_count,
                steficon_rule_targeting=payment_list.steficon_rule_targeting,
                steficon_targeting_applied_date=payment_list.steficon_targeting_applied_date,
                program_cycle=program_cycle,
                payment_plan=payment_plan,
                delivery_mechanism=payment_list.delivery_mechanism,
            )
            PaymentListService.copy_target_criteria(payment_list, payment_list_copy)
            payment_list_copy.save()
            payment_list_copy.payment_plan_purposes.set(purposes)
            payment_list_copy.refresh_from_db()

            transaction.on_commit(lambda: payment_list_full_rebuild_async_task(payment_list_copy))
            log_create(
                PaymentList.ACTIVITY_LOG_MAPPING,
                "business_area",
                user,
                getattr(program, "pk", None),
                old_object=None,
                new_object=payment_list_copy,
            )
            response_serializer = TargetPopulationDetailSerializer(payment_list_copy, context={"request": request})
            return Response(
                data=response_serializer.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="apply-engine-formula")
    @transaction.atomic
    def apply_engine_formula(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        tp = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        engine_formula_rule_id = serializer.validated_data["engine_formula_rule_id"]
        if version := serializer.validated_data.get("version"):
            check_concurrency_version_in_mutation(version, tp)
        engine_rule = get_object_or_404(Rule, id=engine_formula_rule_id, allowed_business_areas=self.business_area)
        # tp vulnerability_score
        if tp.status not in PaymentList.CAN_RUN_ENGINE_FORMULA_FOR_VULNERABILITY_SCORE:
            raise ValidationError(f"Not allowed to run engine formula within status {tp.status}.")
        if not engine_rule.enabled or engine_rule.deprecated:
            raise ValidationError("This engine rule is not enabled or is deprecated.")
        old_tp = copy_model_object(tp)
        tp.steficon_rule_targeting = engine_rule.latest
        tp.status = PaymentList.Status.TP_STEFICON_WAIT
        tp.save()
        payment_list_apply_steficon_hh_selection_async_task(tp, str(engine_rule.id), str(request.user.pk))
        log_create(
            mapping=PaymentList.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=tp.program.pk,
            old_object=old_tp,
            new_object=tp,
        )
        tp.refresh_from_db(fields=["background_action_status"])
        response_serializer = TargetPopulationDetailSerializer(tp, context={"request": request})
        return Response(
            data=response_serializer.data,
            status=status.HTTP_200_OK,
        )


class PaymentPlanManagerialViewSet(
    BusinessAreaProgramsAccessMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    """Managerial console: the payment plans awaiting approval, authorization or release, and bulk actions on them."""

    MANAGERIAL_STATUSES = (
        PaymentPlan.Status.IN_APPROVAL,
        PaymentPlan.Status.IN_AUTHORIZATION,
        PaymentPlan.Status.IN_REVIEW,
        PaymentPlan.Status.ACCEPTED,
    )
    ACTION_PERMISSIONS = {
        PaymentList.Action.APPROVE.value: Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
        PaymentList.Action.AUTHORIZE.value: Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
        PaymentList.Action.REVIEW.value: Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
    }

    queryset = PaymentPlan.objects.all()
    serializer_class = PaymentPlanManagerialSerializer
    PERMISSIONS = [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL]
    business_area_model_field = "cycle__program__business_area"
    program_model_field = "cycle__program"
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = PaymentPlanFilter
    search_fields = ("unicef_id", "id", "^name")

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(status__in=self.MANAGERIAL_STATUSES)
            .select_related("cycle__program", "financial_service_provider", "currency")
            .prefetch_related(
                Prefetch(
                    "approval_process",
                    queryset=ApprovalProcess.objects.select_related("sent_for_approval_by").prefetch_related(
                        Prefetch("approvals", queryset=Approval.objects.select_related("created_by"))
                    ),
                )
            )
            .annotate(
                payment_lists_count=Count("payment_lists"),
                households_total=Coalesce(Sum("payment_lists__total_households_count"), 0),
                entitled_usd_total=Coalesce(Sum("payment_lists__total_entitled_quantity_usd"), Decimal(0)),
            )
            .order_by("-created_at")
        )

    @etag_decorator(PaymentPlanKeyConstructor)
    @cached_response(key_func=PaymentPlanKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @action(
        detail=False,
        methods=["post"],
        url_path="bulk-action",
        serializer_class=PaymentPlanBulkActionSerializer,
    )
    @transaction.atomic
    def bulk_action(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action_name = serializer.validated_data["action"]
        comment = serializer.validated_data.get("comment", "")
        payment_plans = PaymentPlan.objects.filter(
            id__in=serializer.validated_data["ids"], cycle__program__business_area=self.business_area
        ).select_related("cycle__program")
        for payment_plan in payment_plans:
            self._perform_payment_plan_action(payment_plan, action_name, comment, request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _perform_payment_plan_action(
        self, payment_plan: PaymentPlan, action_name: str, comment: str, request: Request
    ) -> None:
        if action_name == PaymentList.Action.REVIEW.value and payment_plan.vision_managed:
            return
        permission = self.ACTION_PERMISSIONS[action_name]
        if not request.user.has_perm(permission.value, payment_plan.cycle.program):
            raise PermissionDenied(detail={"required_permissions": [permission.value]})

        old_payment_plan = copy_model_object(payment_plan)
        payment_plan = PaymentPlanService(payment_plan).acceptance_process(
            action_name, cast("User", request.user), comment
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="cycle.program.business_area",
            user=request.user,
            programs=payment_plan.cycle.program_id,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )


class AccountViewSet(
    ProgramVisibilityMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = Account.all_objects.select_related("account_type").prefetch_related("attachments")
    serializer_class = AccountSerializer
    program_model_field = "individual__program"
    admin_area_model_fields = [
        "individual__household__admin1",
        "individual__household__admin2",
        "individual__household__admin3",
    ]
    PERMISSIONS = [Permissions.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION]

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(individual_id=self.kwargs["individual_pk"], individual__is_removed=False)


class AccountAttachmentViewSet(ProgramVisibilityMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, BaseViewSet):
    queryset = AccountAttachment.objects.all()
    serializer_class = AccountAttachmentUploadSerializer
    lookup_field = "file_id"
    program_model_field = "account__individual__program"
    admin_area_model_fields = [
        "account__individual__household__admin1",
        "account__individual__household__admin2",
        "account__individual__household__admin3",
    ]

    PERMISSIONS = [Permissions.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION]

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(
                account_id=self.kwargs["account_pk"],
                account__individual_id=self.kwargs["individual_pk"],
                account__individual__is_removed=False,
            )
        )

    def get_object(self) -> AccountAttachment:
        return get_object_or_404(self.get_queryset(), id=self.kwargs["file_id"])

    def get_serializer_context(self) -> dict[str, Any]:
        # The account is resolved here, not in the serializer: CreateModelMixin.create() never calls
        # get_queryset(), so without this the upload would skip the program and area-limit filtering
        # that destroy and download get from ProgramVisibilityMixin.
        context = super().get_serializer_context()
        context["account"] = get_object_or_404(self._visible_accounts(), id=self.kwargs["account_pk"])
        return context

    def _visible_accounts(self) -> QuerySet:
        accounts = Account.all_objects.filter(
            individual__program=self.program,
            individual_id=self.kwargs["individual_pk"],
            individual__is_removed=False,
        )
        if area_limits := self.request.user.partner.get_area_limits_for_program(self.program.id):
            areas_null = Q(
                individual__household__admin1__isnull=True,
                individual__household__admin2__isnull=True,
                individual__household__admin3__isnull=True,
            )
            areas_query = (
                Q(individual__household__admin1__in=area_limits)
                | Q(individual__household__admin2__in=area_limits)
                | Q(individual__household__admin3__in=area_limits)
            )
            accounts = accounts.filter(areas_null | areas_query)
        return accounts

    @action(detail=True, methods=["get"])
    def download(self, request: Request, *args: Any, **kwargs: Any) -> FileResponse:
        attachment = self.get_object()
        file = attachment.file
        file_mimetype, _ = mimetypes.guess_type(file.url)
        return FileResponse(
            file.open(),
            as_attachment=True,
            content_type=file_mimetype or "application/octet-stream",
        )


class SupportingDocumentViewSet(ProgramMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, BaseViewSet):
    """Upload, delete and download the supporting documents of a payment plan or a Follow-Up Instruction."""

    serializer_class = PaymentPlanSupportingDocumentSerializer
    lookup_field = "file_id"
    owner_field: str

    permissions_by_action = {
        "create": [Permissions.PM_UPLOAD_SUPPORTING_DOCUMENT],
        "delete": [Permissions.PM_DELETE_SUPPORTING_DOCUMENT],
        "destroy": [Permissions.PM_DELETE_SUPPORTING_DOCUMENT],
        "download": [Permissions.PM_DOWNLOAD_SUPPORTING_DOCUMENT],
    }

    @cached_property
    def owner(self) -> PaymentPlan | FollowUpInstruction:
        raise NotImplementedError

    def get_queryset(self) -> QuerySet:
        return PaymentPlanSupportingDocument.objects.filter(**{self.owner_field: self.owner})

    def get_object(self) -> PaymentPlanSupportingDocument:
        return get_object_or_404(self.get_queryset(), id=self.kwargs.get("file_id"))

    def get_serializer_context(self) -> dict:
        context = super().get_serializer_context()
        context["owner"] = {self.owner_field: self.owner}
        return context

    @transaction.atomic
    def perform_create(self, serializer: Any) -> None:
        document = serializer.save()
        log_payment_plan_supporting_document(self.owner, self.request.user, document.title, created=True)

    @transaction.atomic
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        document = self.get_object()
        title = document.title
        document.delete()
        log_payment_plan_supporting_document(self.owner, request.user, title, created=False)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    def download(self, request: Request, *args: Any, **kwargs: Any) -> FileResponse:
        document = self.get_object()
        file = document.file
        file_mimetype, _ = mimetypes.guess_type(file.url)
        return FileResponse(
            file.open(),
            as_attachment=True,
            content_type=file_mimetype or "application/octet-stream",
        )


class PaymentPlanSupportingDocumentViewSet(SupportingDocumentViewSet):
    owner_field = "payment_plan"

    @cached_property
    def owner(self) -> PaymentPlan:
        return get_object_or_404(PaymentPlan, pk=self.kwargs.get("payment_plan_pk"), cycle__program=self.program)


class FollowUpInstructionSupportingDocumentViewSet(SupportingDocumentViewSet):
    owner_field = "follow_up_instruction"

    @cached_property
    def owner(self) -> FollowUpInstruction:
        return get_object_or_404(
            FollowUpInstruction, pk=self.kwargs.get("follow_up_instruction_pk"), program=self.program
        )


class PaymentViewSet(
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
    ScopedPaymentListMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = Payment.objects.all()
    lookup_field = "payment_id"
    serializer_classes_by_action = {
        "list": PaymentRowSerializer,
        "not_eligible": NotEligiblePaymentRowSerializer,
        "retrieve": PaymentDetailSerializer,
        "revert_mark_as_failed": RevertMarkPaymentAsFailedSerializer,
    }
    permissions_by_action = {
        "list": [
            Permissions.PM_VIEW_DETAILS,
            Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS,
        ],
        "retrieve": [
            Permissions.PM_VIEW_DETAILS,
            Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS,
        ],
        # Both actions need a functional permission for BaseRestPermission; get_queryset adds the superuser-only gate.
        "not_eligible": [
            Permissions.PM_VIEW_DETAILS,
            Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS,
        ],
        "not_eligible_count": [
            Permissions.PM_VIEW_DETAILS,
            Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS,
        ],
        "mark_as_failed": [Permissions.PM_MARK_PAYMENT_AS_FAILED],
        "revert_mark_as_failed": [Permissions.PM_MARK_PAYMENT_AS_FAILED],
    }
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PaymentSearchFilter

    def get_object(self) -> Payment:
        # the details page is reached by a plain link with no plan id, so scope to the program instead
        queryset = Payment.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.exclude(status=Payment.STATUS_NOT_ELIGIBLE)
        return get_object_or_404(
            with_payment_related_data(queryset),
            id=self.kwargs["payment_id"],
            parent__program_cycle__program=self.program,
        )

    def get_queryset(self) -> QuerySet:
        parent = self.payment_list
        if self.action in ("not_eligible", "not_eligible_count"):
            if not self.request.user.is_superuser:
                raise PermissionDenied("Only superusers can view Not Eligible payments.")
            return with_payment_related_data(parent.payment_items.filter(status=Payment.STATUS_NOT_ELIGIBLE))
        if parent.status == PaymentList.Status.OPEN:
            queryset = parent.eligible_payments_with_conflicts
        else:
            queryset = parent.eligible_payments
        return with_payment_related_data(queryset)

    @extend_schema(responses={200: NotEligiblePaymentRowSerializer(many=True)})
    @action(
        detail=False,
        methods=["get"],
        url_path="not-eligible",
        filterset_class=NotEligiblePaymentSearchFilter,
    )
    def not_eligible(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self.list(request, *args, **kwargs)

    @extend_schema(
        responses={status.HTTP_200_OK: inline_serializer("CountResponse", fields={"count": serializers.IntegerField()})}
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="not-eligible/count",
        filterset_class=NotEligiblePaymentSearchFilter,
    )
    def not_eligible_count(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = self.filter_queryset(self.get_queryset()).order_by()
        return Response({"count": queryset.count()})

    @action(
        detail=True,
        methods=["get"],
        url_path="mark-as-failed",
    )
    @transaction.atomic
    def mark_as_failed(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment = self.get_object()
        mark_as_failed(payment, str(request.user.pk))
        return Response(
            data=PaymentDetailSerializer(payment, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        serializer_class=PaymentDetailSerializer,
        url_path="revert-mark-as-failed",
    )
    @transaction.atomic
    def revert_mark_as_failed(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        delivered_quantity = serializer.validated_data.get("delivered_quantity")
        delivery_date = serializer.validated_data.get("delivery_date")
        revert_mark_as_failed(payment, Decimal(delivered_quantity), delivery_date, str(request.user.pk))
        return Response(
            data=PaymentDetailSerializer(payment, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class PaymentGlobalViewSet(
    BusinessAreaProgramsAccessMixin,
    SerializerActionMixin,
    CountActionMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = Payment.objects.exclude(parent__status__in=PaymentList.PRE_PAYMENT_LIST_STATUSES).all()
    serializer_classes_by_action = {
        "list": PaymentRowSerializer,
    }
    PERMISSIONS = [Permissions.PM_VIEW_DETAILS]
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = PaymentOfficeSearchFilter
    program_model_field = "program"

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset().eligible()
        return with_payment_related_data(queryset).order_by("-created_at")


@extend_schema(responses={200: FspChoicesSerializer(many=True)})
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def available_fsps_for_delivery_mechanisms(
    request: Request, business_area_slug: str, *args: Any, **kwargs: Any
) -> Response:
    delivery_mechanisms = DeliveryMechanism.objects.filter(is_active=True)

    fsps = (
        FinancialServiceProvider.objects.filter(
            allowed_business_areas__slug=business_area_slug,
        )
        .prefetch_related(
            "delivery_mechanisms",
            "fsp_xlsx_template_per_delivery_mechanisms__delivery_mechanism",
        )
        .distinct()
    )

    def get_fsps(dm: DeliveryMechanism) -> list[dict[str, Any]]:
        result = []
        for fsp in fsps:
            dm_names = {d.name for d in fsp.delivery_mechanisms.all()}
            if dm.name not in dm_names:
                continue

            templates = list(fsp.fsp_xlsx_template_per_delivery_mechanisms.all())
            has_templates = bool(templates)
            template_dm_names = {t.delivery_mechanism.name for t in templates if t.delivery_mechanism}

            if dm.name in template_dm_names or not has_templates:
                result.append({"id": fsp.id, "name": fsp.name})
        return result

    list_resp = [
        {
            "delivery_mechanism": delivery_mechanism,
            "fsps": get_fsps(delivery_mechanism),
        }
        for delivery_mechanism in delivery_mechanisms
    ]

    serializer = FspChoicesSerializer(list_resp, many=True)
    return Response(serializer.data)


class PaymentPlanViewSet(
    CountActionMixin,
    SerializerActionMixin,
    ProgramMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    BaseViewSet,
):
    queryset = PaymentPlan.objects.select_related(
        "cycle", "financial_service_provider", "currency", "source_payment_plan"
    ).order_by("cycle__title", "created_at")
    program_model_field = "cycle__program"
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PaymentPlanFilter

    serializer_classes_by_action = {
        "list": PaymentPlanListSerializer,
        "retrieve": PaymentPlanDetailSerializer,
        "create": PaymentPlanCreateSerializer,
        "update": PaymentPlanUpdateSerializer,
        "delivery_export_xlsx": PaymentPlanDeliveryExportSerializer,
        "delivery_import_xlsx": PaymentPlanReconciliationImportSerializer,
        "fsp_extra_fields_import_xlsx": PaymentPlanImportFileSerializer,
        "approve": AcceptanceProcessSerializer,
        "authorize": AcceptanceProcessSerializer,
        "reject": AcceptanceProcessSerializer,
        "mark_as_released": AcceptanceProcessSerializer,
        "close": PaymentPlanCloseSerializer,
        "abort": PaymentPlanAbortSerializer,
        "create_follow_up": PaymentPlanCreateFollowUpSerializer,
        "create_top_up": PaymentPlanCreateTopUpSerializer,
        "create_top_up_amendment": PaymentPlanCreateTopUpSerializer,
        "split": SplitPaymentPlanSerializer,
        "assign_funds_commitments": AssignFundsCommitmentsSerializer,
        "custom_exchange_rate": ApplyCustomExchangeRateSerializer,
    }

    permissions_by_action = {
        "list": [Permissions.PM_PAYMENT_PLAN_VIEW_LIST],
        "retrieve": [Permissions.PM_PAYMENT_PLAN_VIEW_DETAIL],
        "create": [Permissions.PM_PAYMENT_PLAN_CREATE],
        "update": [Permissions.PM_PAYMENT_PLAN_UPDATE],
        "destroy": [Permissions.PM_PAYMENT_PLAN_DELETE],
        "lock": [Permissions.PM_LOCK_AND_UNLOCK_FSP],
        "unlock": [Permissions.PM_LOCK_AND_UNLOCK_FSP],
        "send_for_approval": [Permissions.PM_SEND_FOR_APPROVAL],
        "approve": [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        "authorize": [Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE],
        "mark_as_released": [Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW],
        "reject": [
            Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
            Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
            Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
        ],
        "ready_for_closure": [Permissions.PM_MARK_READY_FOR_CLOSURE],
        "send_back_to_finished": [Permissions.PM_MARK_READY_FOR_CLOSURE],
        "close": [Permissions.PM_CLOSE_FINISHED],
        "abort": [Permissions.PM_ABORT],
        "reactivate_abort": [Permissions.PM_REACTIVATE_ABORT],
        "send_to_payment_gateway": [Permissions.PM_PAYMENT_PLAN_SEND_TO_PAYMENT_GATEWAY],
        "delivery_export_xlsx": [Permissions.PM_PAYMENT_PLAN_EXPORT_XLSX],
        "send_xlsx_password": [Permissions.PM_SEND_XLSX_PASSWORD],
        "delivery_import_xlsx": [Permissions.PM_PAYMENT_PLAN_IMPORT_XLSX],
        "fsp_extra_fields_template": [Permissions.PM_VIEW_LIST],
        "fsp_extra_fields_import_xlsx": [Permissions.PM_IMPORT_XLSX_WITH_RECONCILIATION],
        "create_follow_up": [Permissions.PM_CREATE],
        "create_top_up": [Permissions.PM_CREATE],
        "top_up_amount_template": [Permissions.PM_CREATE],
        "create_top_up_amendment": [Permissions.PM_CREATE],
        "split": [Permissions.PM_SPLIT],
        "assign_funds_commitments": [Permissions.PM_ASSIGN_FUNDS_COMMITMENTS],
        "export_pdf_payment_plan_summary": [Permissions.PM_EXPORT_PDF_SUMMARY],
        "custom_exchange_rate": [Permissions.PM_CUSTOM_EXCHANGE_RATE],
    }

    @etag_decorator(PaymentPlanListKeyConstructor)
    @cached_response(key_func=PaymentPlanListKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(request=ApplyCustomExchangeRateSerializer, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="custom-exchange-rate")
    @transaction.atomic
    def custom_exchange_rate(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        payment_plan = PaymentPlan.objects.select_for_update().get(pk=self.get_object().pk)
        if payment_plan.status not in (PaymentPlan.Status.OPEN, PaymentPlan.Status.IN_REVIEW):
            raise ValidationError("Exchange rate can be changed only while the payment plan is OPEN or IN_REVIEW")
        check_concurrency_version_in_mutation(data.get("version"), payment_plan)
        if payment_plan.background_action_status not in (None, *PaymentPlan.BACKGROUND_ACTION_ERROR_STATES):
            raise ValidationError("Wait for the current payment plan action to finish before changing the rate")

        user = cast("User", request.user)
        old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
        custom_rate = data.get("custom_exchange_rate")
        payment_plan.exchange_rate = custom_rate if custom_rate is not None else data["unore_exchange_rate"]
        payment_plan.custom_exchange_rate = custom_rate is not None
        payment_plan.custom_exchange_rate_set_by = user if custom_rate is not None else None
        payment_plan.save(
            update_fields=[
                "exchange_rate",
                "custom_exchange_rate",
                "custom_exchange_rate_set_by",
                "version",
                "updated_at",
            ]
        )
        log_payment_plan_change(payment_plan, old_payment_plan, str(user.pk))
        payment_plan = cast(
            "PaymentPlan",
            recalculate_owner_exchange_rate_async_task(payment_plan, str(user.pk), fetch_unore_rate=False),
        )
        return Response(PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data)

    @extend_schema(request=AssignFundsCommitmentsSerializer, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="assign-funds-commitments")
    @transaction.atomic
    def assign_funds_commitments(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        requested_numbers = set(serializer.validated_data["funds_commitment_numbers"])
        payment_plan = PaymentPlan.objects.select_for_update().get(pk=self.get_object().pk)
        if not payment_plan.can_assign_funds_commitments:
            raise ValidationError("Payment Plan must be in review, not managed by Vision, and not a Follow-Up")
        headers = list(FundsCommitmentHeader.objects.filter(funds_commitment_number__in=requested_numbers))
        if len(headers) != len(requested_numbers):
            raise ValidationError("One or more Funds Commitment Headers were not found")
        try:
            VisionService.assign_selected_funds_commitment_headers(payment_plan, headers)
        except FundsCommitmentAssignmentError as error:
            message = "One or more Funds Commitment Headers are not available for this Business Area"
            raise ValidationError(message) from error
        return Response(
            PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @transaction.atomic
    def perform_create(self, serializer: Any) -> None:
        payment_plan = serializer.save(created_by=self.request.user)
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="cycle.program.business_area",
            user=self.request.user,
            programs=payment_plan.cycle.program.pk,
            old_object=None,
            new_object=payment_plan,
        )

    @staticmethod
    def _validate_delivery_status(payment_plan: PaymentPlan, action_label: str) -> None:
        if payment_plan.status not in PaymentPlan.DELIVERY_STATUSES:
            raise ValidationError(
                f"{action_label} is possible only within Status ACCEPTED or FINISHED, got {payment_plan.status}"
            )

    def _create_linked_payment_plan_response(self, request: Request, plan_type: "PaymentList.PlanType") -> Response:
        """Shared body for the create-follow-up / create-top-up / create-top-up-amendment actions."""
        payment_plan = self.get_object()
        serializer = self.get_serializer(
            data=request.data, context={"payment_plan": payment_plan, "plan_type": plan_type}
        )
        serializer.is_valid(raise_exception=True)
        linked_payment_plan = PaymentPlanService(payment_plan).create_linked_payment_plan(
            plan_type=plan_type,
            user=cast("User", request.user),
            dispersion_start_date=serializer.validated_data["dispersion_start_date"],
            dispersion_end_date=serializer.validated_data["dispersion_end_date"],
            top_up_amount=serializer.validated_data.get("amounts") or serializer.validated_data.get("fixed_amount"),
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="cycle.program.business_area",
            user=request.user,
            programs=linked_payment_plan.cycle.program.pk,
            old_object=None,
            new_object=linked_payment_plan,
        )
        return Response(
            data=PaymentPlanDetailSerializer(linked_payment_plan, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=PaymentPlanCreateFollowUpSerializer, responses={201: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="create-follow-up")
    @transaction.atomic
    def create_follow_up(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._create_linked_payment_plan_response(request, PaymentList.PlanType.FOLLOW_UP)

    @extend_schema(request=PaymentPlanCreateTopUpSerializer, responses={201: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="create-top-up", parser_classes=[MultiPartParser, JSONParser])
    @transaction.atomic
    def create_top_up(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._create_linked_payment_plan_response(request, PaymentList.PlanType.TOP_UP)

    @extend_schema(request=PaymentPlanCreateTopUpSerializer, responses={201: PaymentPlanDetailSerializer})
    @action(
        detail=True,
        methods=["post"],
        url_path="create-top-up-amendment",
        parser_classes=[MultiPartParser, JSONParser],
    )
    @transaction.atomic
    def create_top_up_amendment(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._create_linked_payment_plan_response(request, PaymentList.PlanType.TOP_UP_AMENDMENT)

    @extend_schema(request=None, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["get"], url_path="export-pdf-payment-plan-summary")
    def export_pdf_payment_plan_summary(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        if payment_plan.status not in PaymentPlan.SUMMARY_PDF_STATUSES:
            raise ValidationError(
                f"Export PDF is possible only within Status IN_REVIEW, ACCEPTED or FINISHED, got {payment_plan.status}"
            )
        export_pdf_payment_plan_summary_async_task(payment_plan, str(request.user.pk))
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=SplitPaymentPlanSerializer, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"])
    def split(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._run_status_action(
            request,
            lambda service: service.split(
                serializer.validated_data["split_type"], serializer.validated_data.get("payments_no")
            ),
        )

    @extend_schema(responses={(200, XLSX_CONTENT_TYPE): OpenApiTypes.BINARY})
    @action(detail=True, methods=["get"], url_path="top-up-amount-template")
    def top_up_amount_template(self, request: Request, *args: Any, **kwargs: Any) -> HttpResponse:
        """Blank per-beneficiary amount template for the Top-Up or Amendment this payment plan can create.

        A Standard payment plan gets the Top-Up template, a Top-Up payment plan gets the Amendment one. Built
        synchronously: the sheet only lists existing payments.
        """
        payment_plan = self.get_object()
        plan_type = (
            PaymentList.PlanType.TOP_UP_AMENDMENT
            if payment_plan.plan_type == PaymentList.PlanType.TOP_UP
            else PaymentList.PlanType.TOP_UP
        )
        source_payment_lists = payment_plan.payment_lists_qualifying_for_linked_payment_plan(plan_type)
        if not source_payment_lists:
            raise ValidationError(f"No Payment List in this payment plan qualifies for a {plan_type.label}.")

        workbook = TopUpAmountTemplateService(source_payment_lists).generate_workbook()
        buffer = BytesIO()
        workbook.save(buffer)
        filename = f"top_up_amount_template_{payment_plan.unicef_id or payment_plan.id}.xlsx"
        response = HttpResponse(buffer.getvalue(), content_type=XLSX_CONTENT_TYPE)
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    @transaction.atomic
    def perform_update(self, serializer: Any) -> None:
        old_payment_plan = copy_model_object(serializer.instance)
        payment_plan = serializer.save()
        if not create_diff(old_payment_plan, payment_plan, PaymentPlan.ACTIVITY_LOG_MAPPING):
            return
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="cycle.program.business_area",
            user=self.request.user,
            programs=payment_plan.cycle.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )

    @transaction.atomic
    def perform_destroy(self, instance: PaymentPlan) -> None:
        if instance.payment_lists.exists():
            raise ValidationError("Cannot delete a payment plan that has payment lists.")
        if instance.cycle.payment_plans.count() == 1:
            raise ValidationError("Cannot delete the last payment plan in a cycle.")
        deleted_payment_plan = copy_model_object(instance)
        program_id = instance.cycle.program.pk
        instance.delete()
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="cycle.program.business_area",
            user=self.request.user,
            programs=program_id,
            old_object=deleted_payment_plan,
            new_object=None,
        )

    @extend_schema(
        request=PaymentPlanDeliveryExportSerializer,
        responses={200: PaymentPlanDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="delivery-export-xlsx")
    @transaction.atomic
    def delivery_export_xlsx(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = PaymentPlan.objects.select_for_update().get(pk=self.get_object().pk)
        self._validate_delivery_status(payment_plan, "Export")
        if not payment_plan.can_start_background_action:
            raise ValidationError("Another background action is already in progress.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fsp_xlsx_template_id = serializer.validated_data["fsp_xlsx_template_id"]

        if fsp_xlsx_template_id is not None:
            template = get_object_or_404(FinancialServiceProviderXlsxTemplate, pk=fsp_xlsx_template_id)
            if "fsp_auth_code" in template.columns and not request.user.has_perm(
                Permissions.PM_DOWNLOAD_FSP_AUTH_CODE.value,
                payment_plan.cycle.program,
            ):
                raise PermissionDenied(detail={"required_permissions": [Permissions.PM_DOWNLOAD_FSP_AUTH_CODE.value]})

        if not payment_plan.payment_lists.exists():
            raise ValidationError("Export requires at least one payment list in the payment plan.")
        if not Payment.objects.filter(parent__payment_plan=payment_plan).eligible().exists():
            raise ValidationError("Export failed: there are no eligible payments to export.")

        # The file goes to the FSP as one list, so a plan that cannot be exported blocks the whole
        # payment plan; the user gets the reason on click instead of a failing background task.
        unexportable_reasons = XlsxPaymentPlanDeliveryExportService(
            payment_plan, fsp_xlsx_template_id=fsp_xlsx_template_id
        ).unexportable_reasons()
        if unexportable_reasons:
            raise ValidationError(unexportable_reasons)

        old_payment_plan = copy_model_object(payment_plan)
        payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING
        payment_plan.save(update_fields=["background_action_status"])
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="cycle.program.business_area",
            user=request.user,
            programs=payment_plan.cycle.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        transaction.on_commit(
            lambda: export_payment_plan_delivery_xlsx_async_task(
                payment_plan, str(request.user.pk), fsp_xlsx_template_id
            )
        )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=None, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="send-xlsx-password")
    def send_xlsx_password(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        if payment_plan.export_file_delivery_id is None:
            raise ValidationError("No exported payment list file found for this payment plan.")

        transaction.on_commit(
            lambda: send_payment_plan_delivery_xlsx_password_async_task(payment_plan, str(request.user.pk))
        )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentPlanReconciliationImportSerializer,
        responses={200: PaymentPlanDetailSerializer, 400: XlsxErrorSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="delivery-import-xlsx",
        parser_classes=[DictDrfNestedParser],
    )
    @transaction.atomic
    def delivery_import_xlsx(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = PaymentPlan.objects.select_for_update().get(pk=self.get_object().pk)
        self._validate_delivery_status(payment_plan, "Import")
        if not payment_plan.can_start_background_action:
            raise ValidationError("Another background action is already in progress.")

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        file = serializer.validated_data["file"]
        override = serializer.validated_data[OVERRIDE_OPTION]
        null_delivery_policy = serializer.validated_data[NULL_DELIVERY_POLICY_OPTION]

        override_permission = Permissions.PM_IMPORT_XLSX_WITH_RECONCILIATION_OVERRIDE
        if override and not request.user.has_perm(override_permission.value, payment_plan.cycle.program):
            raise PermissionDenied(detail={"required_permissions": [override_permission.value]})

        import_service = XlsxPaymentPlanDeliveryImportService(
            payment_plan,
            file,
            override=override,
            null_delivery_policy=null_delivery_policy,
        )
        try:
            import_service.open_workbook()
        except BadZipFile:
            raise ValidationError(
                "Wrong file type or password protected .zip file. Upload another file, or remove the password."
            )
        import_service.validate()
        if import_service.errors:
            if import_service.conflict_errors:
                PaymentPlanReconciliationImportNotification(
                    payment_plan,
                    cast("User", request.user),
                    file.name,
                ).send_conflict(import_service.errors, len(import_service.conflict_errors))
            return Response(
                data=XlsxErrorSerializer(import_service.errors, many=True, context={"request": request}).data,
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_temp = FileTemp.objects.create(
            object_id=payment_plan.pk,
            content_type=get_content_type_for_model(payment_plan),
            created_by=request.user,
            file=file,
            extras={
                OVERRIDE_OPTION: override,
                NULL_DELIVERY_POLICY_OPTION: null_delivery_policy,
            },
        )
        old_payment_plan = copy_model_object(payment_plan)
        payment_plan.delivery_import_file = file_temp
        payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION
        payment_plan.save(update_fields=["delivery_import_file", "background_action_status"])
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="cycle.program.business_area",
            user=request.user,
            programs=payment_plan.cycle.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        user_id = str(request.user.pk)
        transaction.on_commit(
            lambda: import_payment_plan_delivery_from_xlsx_async_task(
                payment_plan,
                user_id,
                override=override,
                null_delivery_policy=null_delivery_policy,
            )
        )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"], url_path="fsp-extra-fields-template")
    def fsp_extra_fields_template(self, request: Request, *args: Any, **kwargs: Any) -> FileResponse:
        payment_plan = self.get_object()
        if payment_plan.status != PaymentPlan.Status.LOCKED:
            raise ValidationError("FSP extra fields template is available only for LOCKED Payment Plans.")

        service = XlsxPaymentPlanFspExtraFieldsExportService(payment_plan)
        output = BytesIO()
        service.generate_workbook().save(output)
        output.seek(0)
        return FileResponse(
            output,
            as_attachment=True,
            filename=service.filename,
        )

    @extend_schema(
        request=PaymentPlanImportFileSerializer,
        responses={200: PaymentPlanDetailSerializer, 400: XlsxErrorSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="fsp-extra-fields-import-xlsx",
        parser_classes=[DictDrfNestedParser],
    )
    @transaction.atomic
    def fsp_extra_fields_import_xlsx(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        if payment_plan.status != PaymentPlan.Status.LOCKED:
            raise ValidationError("FSP extra fields can be imported only for LOCKED Payment Plans.")
        if payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.RECALCULATING_ERROR:
            raise ValidationError(
                "USD recalculation failed for this payment plan. Retry it before importing FSP extra fields."
            )
        if not payment_plan.can_start_background_action:
            raise ValidationError("Another background action is already in progress.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]
        import_service = XlsxPaymentPlanFspExtraFieldsImportService(payment_plan, file)
        try:
            import_service.open_workbook()
        except BadZipFile:
            raise ValidationError("Invalid XLSX file. Upload another file.")
        import_service.validate()
        if import_service.errors:
            return Response(
                data=XlsxErrorSerializer(import_service.errors, many=True, context={"request": request}).data,
                status=status.HTTP_400_BAD_REQUEST,
            )

        file.seek(0)
        file_temp = FileTemp.objects.create(
            object_id=payment_plan.pk,
            content_type=get_content_type_for_model(payment_plan),
            created_by=request.user,
            file=file,
        )
        old_payment_plan = copy_model_object(payment_plan)
        payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_FSP_EXTRA_FIELDS
        payment_plan.save(update_fields=["background_action_status", "updated_at"])
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="cycle.program.business_area",
            user=request.user,
            programs=payment_plan.cycle.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        user_id = str(request.user.pk)
        transaction.on_commit(
            lambda: import_payment_plan_fsp_extra_fields_from_xlsx_async_task(
                payment_plan,
                str(file_temp.id),
                user_id,
            )
        )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=None, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="lock")
    def lock(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._run_status_action(request, PaymentPlanService.lock)

    @extend_schema(request=None, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="unlock")
    def unlock(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._run_status_action(request, PaymentPlanService.unlock)

    @extend_schema(request=None, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="send-for-approval")
    def send_for_approval(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._run_status_action(request, lambda service: service.send_for_approval(request.user))

    @extend_schema(request=AcceptanceProcessSerializer, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"])
    def approve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._run_acceptance_action(request, PaymentList.Action.APPROVE)

    @extend_schema(request=AcceptanceProcessSerializer, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"])
    def authorize(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._run_acceptance_action(request, PaymentList.Action.AUTHORIZE)

    @extend_schema(request=AcceptanceProcessSerializer, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def reject(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # The stage permission must match the status the reject is recorded on, so read it from the locked row.
        payment_plan = PaymentPlan.objects.select_for_update().get(pk=self.get_object().pk)
        reject_permission = REJECT_PERMISSION_BY_STATUS.get(payment_plan.status)
        if reject_permission and not request.user.has_perm(reject_permission.value, payment_plan.cycle.program):
            raise PermissionDenied(detail={"required_permissions": [reject_permission.value]})
        return self._run_acceptance_action(request, PaymentList.Action.REJECT)

    @extend_schema(request=AcceptanceProcessSerializer, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="mark-as-released")
    def mark_as_released(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._run_acceptance_action(request, PaymentList.Action.REVIEW)

    @extend_schema(request=None, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="ready-for-closure")
    def ready_for_closure(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._run_status_action(request, lambda service: service.ready_for_closure(request.user))

    @extend_schema(request=None, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="send-back-to-finished")
    def send_back_to_finished(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._run_status_action(request, lambda service: service.send_back_to_finished(request.user))

    @extend_schema(request=PaymentPlanCloseSerializer, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"])
    def close(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        closure_comment = serializer.validated_data.get("closure_comment")
        return self._run_status_action(request, lambda service: service.close(closure_comment, request.user))

    @extend_schema(request=PaymentPlanAbortSerializer, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"])
    def abort(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        abort_comment = serializer.validated_data.get("abort_comment")
        return self._run_status_action(request, lambda service: service.abort(abort_comment, request.user))

    @extend_schema(request=None, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="reactivate-abort")
    def reactivate_abort(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._run_status_action(request, lambda service: service.reactivate_abort(str(request.user.pk)))

    def _run_acceptance_action(self, request: Request, plan_action: "PaymentList.Action") -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.validated_data.get("comment")
        return self._run_status_action(
            request, lambda service: service.acceptance_process(plan_action.value, request.user, comment)
        )

    @transaction.atomic
    def _run_status_action(self, request: Request, action_method: Callable) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)
        payment_plan = action_method(PaymentPlanService(payment_plan))
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="cycle.program.business_area",
            user=request.user,
            programs=payment_plan.cycle.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="send-to-payment-gateway")
    def send_to_payment_gateway(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Queue an async send-to-payment-gateway job for the payment plan's sendable payment lists.

        A payment list is sendable when it is ACCEPTED, its payment plan routes through the payment gateway
        (the payment plan's use_payment_gateway flag is True or its FSP communication_channel is API),
        still has splits not yet sent to the gateway, and is not already being sent. The payment plan object
        is locked for update to prevent double processing the same objects.
        """
        payment_plan = self.get_object()
        if payment_plan.status != PaymentPlan.Status.ACCEPTED:
            raise ValidationError(
                f"Send to Payment Gateway is possible only within Status ACCEPTED, got {payment_plan.status}"
            )

        with transaction.atomic():
            PaymentPlan.objects.select_for_update().get(pk=payment_plan.pk)

            # Take only the pks: the queryset annotates has_unsent_splits, and copy_model_object()
            # below raises TypeError on an annotated instance.
            plans = list(
                PaymentList.objects.filter(
                    pk__in=payment_plan.sendable_to_payment_gateway_plans().values("pk")
                ).select_related("program_cycle")
            )
            if not plans:
                raise ValidationError("No payment lists can be sent to payment gateway.")

            for plan in plans:
                old_plan = copy_model_object(plan)
                program_id = plan.program_cycle.program_id
                updated_plan = PaymentListService(plan).execute_update_status_action(
                    input_data={"action": PaymentList.Action.SEND_TO_PAYMENT_GATEWAY},
                    user=request.user,
                    as_manager=True,
                )
                log_create(
                    mapping=PaymentList.ACTIVITY_LOG_MAPPING,
                    business_area_field="business_area",
                    user=request.user,
                    programs=program_id,
                    old_object=old_plan,
                    new_object=updated_plan,
                )

        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class FinancialInstitutionViewSet(BusinessAreaMixin, SerializerActionMixin, BaseViewSet):
    queryset = FinancialInstitution.objects.all()
    permissions_by_action = {
        "choices": [
            Permissions.RDI_VIEW_DETAILS,
            Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
            Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS,
        ],
    }
    serializer_classes_by_action = {
        "choices": FinancialInstitutionChoiceSerializer,
    }

    def get_queryset(self) -> QuerySet:
        return (
            FinancialInstitution.objects.filter(Q(country__business_areas=self.business_area) | Q(country__isnull=True))
            .distinct()
            .order_by("id")
        )

    @extend_schema(responses={200: FinancialInstitutionChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="choices", url_name="choices", pagination_class=None)
    def choices(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return Response(self.get_serializer(self.get_queryset(), many=True).data)


class PaymentPlanPurposeViewSet(
    CountActionMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = PaymentPlanPurpose.objects.all()
    serializer_class = PaymentPlanPurposeSerializer
    PERMISSIONS = [Permissions.PM_PAYMENT_PLAN_PURPOSE_VIEW_LIST]
    filter_backends = (SearchFilter,)
    search_fields = ("name",)

    def get_queryset(self) -> QuerySet:
        ba_slug = self.kwargs.get("business_area_slug")
        return PaymentPlanPurpose.objects.filter(Q(limit_to__isnull=True) | Q(limit_to__slug=ba_slug)).distinct()

    @etag_decorator(PaymentPlanPurposeListKeyConstructor)
    @cached_response(key_func=PaymentPlanPurposeListKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
