import logging
import mimetypes
from datetime import datetime
from decimal import Decimal
from typing import Any
from zipfile import BadZipFile

from django.db import transaction
from django.db.models import Q, QuerySet
from django.http import FileResponse
from django.utils import timezone

from constance import config
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
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
    ProgramMixin,
    SerializerActionMixin,
)
from hct_mis_api.apps.core.api.parsers import DictDrfNestedParser
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import check_concurrency_version_in_mutation
from hct_mis_api.apps.payment.api.caches import (
    PaymentPlanKeyConstructor,
    PaymentPlanListKeyConstructor,
    TargetPopulationListKeyConstructor,
)
from hct_mis_api.apps.payment.api.filters import (
    PaymentPlanFilter,
    TargetPopulationFilter,
)
from hct_mis_api.apps.payment.api.serializers import (
    AcceptanceProcessSerializer,
    ApplyEngineFormulaSerializer,
    AssignFundsCommitmentsSerializer,
    FspChoicesSerializer,
    FSPXlsxTemplateSerializer,
    PaymentDetailSerializer,
    PaymentListSerializer,
    PaymentPlanBulkActionSerializer,
    PaymentPlanCreateFollowUpSerializer,
    PaymentPlanCreateUpdateSerializer,
    PaymentPlanDetailSerializer,
    PaymentPlanExcludeBeneficiariesSerializer,
    PaymentPlanExportAuthCodeSerializer,
    PaymentPlanImportFileSerializer,
    PaymentPlanListSerializer,
    PaymentPlanSerializer,
    PaymentPlanSupportingDocumentSerializer,
    PaymentVerificationPlanActivateSerializer,
    PaymentVerificationPlanCreateSerializer,
    PaymentVerificationPlanDetailsSerializer,
    PaymentVerificationPlanImportSerializer,
    PaymentVerificationPlanListSerializer,
    PaymentVerificationUpdateSerializer,
    RevertMarkPaymentAsFailedSerializer,
    SplitPaymentPlanSerializer,
    TargetPopulationCopySerializer,
    TargetPopulationCreateSerializer,
    TargetPopulationDetailSerializer,
    PendingPaymentSerializer,
    XlsxErrorSerializer,
)
from hct_mis_api.apps.payment.celery_tasks import (
    export_pdf_payment_plan_summary,
    import_payment_plan_payment_list_from_xlsx,
    payment_plan_apply_engine_rule,
    payment_plan_apply_steficon_hh_selection,
    payment_plan_exclude_beneficiaries,
    payment_plan_full_rebuild,
)
from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
    PaymentPlanSupportingDocument,
    PaymentVerification,
    PaymentVerificationPlan,
)
from hct_mis_api.apps.payment.services.mark_as_failed import (
    mark_as_failed,
    revert_mark_as_failed,
)
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.payment.services.verification_plan_crud_services import (
    VerificationPlanCrudServices,
)
from hct_mis_api.apps.payment.services.verification_plan_status_change_services import (
    VerificationPlanStatusChangeServices,
)
from hct_mis_api.apps.payment.utils import calculate_counts, from_received_to_status
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_import_service import (
    XlsxPaymentPlanImportService,
)
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service import (
    XlsxPaymentPlanImportPerFspService,
)
from hct_mis_api.apps.payment.xlsx.xlsx_verification_import_service import (
    XlsxVerificationImportService,
)
from hct_mis_api.apps.program.models import ProgramCycle
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.targeting.api.serializers import TargetPopulationListSerializer
from hct_mis_api.contrib.vision.models import FundsCommitmentItem

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


class PaymentVerificationViewSet(
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
    PaymentPlanMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    program_model_field = "program_cycle__program"
    queryset = PaymentPlan.objects.filter(
        status__in=(PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED)
    ).order_by("unicef_id")
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
    }

    def get_object(self) -> PaymentPlan:
        return get_object_or_404(PaymentPlan, id=self.kwargs.get("pk"))

    def get_verification_plan_object(self) -> PaymentVerificationPlan:
        return get_object_or_404(PaymentVerificationPlan, id=self.kwargs.get("verification_plan_id"))

    # @etag_decorator(PaymentVerificationListKeyConstructor)
    # @cache_response(timeout=config.REST_API_TTL, key_func=PaymentVerificationListKeyConstructor())
    # TODO: Enable cache on verification list, it is not working due to the fact that when summary is invalidated payment plan cache is not invalidated (key is stored as hash) updated_at in payment plan is not updated
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=PaymentVerificationPlanCreateSerializer, responses={201: PaymentVerificationPlanDetailsSerializer}
    )
    @action(detail=True, methods=["post"], url_path="create-verification-plan")
    @transaction.atomic
    def create_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create Payment Verification Plan"""
        payment_plan = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        verification_plan = VerificationPlanCrudServices.create(payment_plan, serializer.validated_data)
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            payment_plan.program,
            None,
            verification_plan,
        )
        payment_plan.refresh_from_db()
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_plan).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        request=PaymentVerificationPlanCreateSerializer, responses={200: PaymentVerificationPlanDetailsSerializer}
    )
    @action(detail=True, methods=["patch"], url_path="update-verification-plan/(?P<verification_plan_id>[^/.]+)")
    @transaction.atomic
    def update_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        pvp = self.get_verification_plan_object()
        serializer = self.get_serializer(pvp, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        old_payment_verification_plan = copy_model_object(pvp)
        pvp.verification_channel = serializer.validated_data.get("verification_channel")
        pvp.payment_record_verifications.all().delete()

        payment_verification_plan = VerificationPlanCrudServices.update(pvp, serializer.validated_data)

        payment_plan.refresh_from_db()
        log_create(
            PaymentVerificationPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            getattr(payment_verification_plan.get_program, "pk", None),
            old_payment_verification_plan,
            payment_verification_plan,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_verification_plan.payment_plan).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentVerificationPlanActivateSerializer, responses={200: PaymentVerificationPlanDetailsSerializer}
    )
    @action(detail=True, methods=["post"], url_path="activate-verification-plan/(?P<verification_plan_id>[^/.]+)")
    @transaction.atomic
    def activate_payment_verification_plan(
        self, request: Request, verification_plan_id: str, *args: Any, **kwargs: Any
    ) -> Response:
        payment_plan = self.get_object()
        payment_verification_plan = self.get_verification_plan_object()
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
            old_payment_verification_plan,
            payment_verification_plan,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_plan).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentVerificationPlanActivateSerializer, responses={200: PaymentVerificationPlanDetailsSerializer}
    )
    @action(detail=True, methods=["post"], url_path="finish-verification-plan/(?P<verification_plan_id>[^/.]+)")
    @transaction.atomic
    def finish_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
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
            old_payment_verification_plan,
            payment_verification_plan,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_plan).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentVerificationPlanActivateSerializer, responses={200: PaymentVerificationPlanDetailsSerializer}
    )
    @action(detail=True, methods=["post"], url_path="discard-verification-plan/(?P<verification_plan_id>[^/.]+)")
    @transaction.atomic
    def discard_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
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
            old_payment_verification_plan,
            payment_verification_plan,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_plan).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentVerificationPlanActivateSerializer, responses={200: PaymentVerificationPlanDetailsSerializer}
    )
    @action(detail=True, methods=["post"], url_path="invalid-verification-plan/(?P<verification_plan_id>[^/.]+)")
    @transaction.atomic
    def invalid_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
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
            old_payment_verification_plan,
            payment_verification_plan,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_plan).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentVerificationPlanActivateSerializer, responses={200: PaymentVerificationPlanDetailsSerializer}
    )
    @action(detail=True, methods=["post"], url_path="delete-verification-plan/(?P<verification_plan_id>[^/.]+)")
    @transaction.atomic
    def delete_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
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
            old_payment_verification_plan,
            None,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_plan).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentVerificationPlanActivateSerializer, responses={200: PaymentVerificationPlanDetailsSerializer}
    )
    @action(detail=True, methods=["post"], url_path="export-xlsx/(?P<verification_plan_id>[^/.]+)")
    @transaction.atomic
    def export_xlsx_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
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
            old_payment_verification_plan,
            payment_verification_plan,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_plan).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PaymentVerificationPlanImportSerializer,
        responses={200: PaymentVerificationPlanDetailsSerializer, 400: XlsxErrorSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="import-xlsx/(?P<verification_plan_id>[^/.]+)",
        parser_classes=[DictDrfNestedParser],
    )
    @transaction.atomic
    def import_xlsx_payment_verification_plan(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
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
            old_payment_verification_plan,
            payment_verification_plan,
        )
        return Response(
            data=PaymentVerificationPlanDetailsSerializer(payment_plan).data,
            status=status.HTTP_200_OK,
        )


class PaymentVerificationRecordViewSet(
    CountActionMixin, ProgramMixin, SerializerActionMixin, PaymentPlanMixin, BaseViewSet
):
    program_model_field = "program_cycle__program"
    queryset = PaymentPlan.objects.filter(
        status__in=(PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED)
    ).order_by("unicef_id")
    PERMISSIONS = [Permissions.PAYMENT_VERIFICATION_VIEW_LIST]
    serializer_classes_by_action = {
        "list": PaymentListSerializer,
        "retrieve": PaymentDetailSerializer,
        "partial_update": PaymentVerificationUpdateSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS],
        "retrieve": [Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS],
        "partial_update": [Permissions.PAYMENT_VERIFICATION_VERIFY],
    }

    def get_object(self) -> PaymentPlan:
        return get_object_or_404(PaymentPlan, id=self.kwargs.get("payment_verification_pk"))

    def get_verification_record(self) -> PaymentVerificationPlan:
        return get_object_or_404(Payment, id=self.kwargs.get("pk"))

    @extend_schema(
        responses={
            200: PaymentListSerializer(many=True),
        },
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return list of verification records."""
        payment_plan = self.get_object()
        payments = payment_plan.eligible_payments.all()
        page = self.paginate_queryset(payments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment = self.get_verification_record()
        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=PaymentVerificationUpdateSerializer, responses={200: PaymentDetailSerializer})
    @transaction.atomic
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """update verification amount"""

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
                f"You can only update status of payment verification for {PaymentVerificationPlan.STATUS_ACTIVE} cash plan verification"
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

        payment_verification.status = from_received_to_status(received, received_amount, delivered_amount)
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
            old_payment_verification,
            payment_verification,
        )
        payment.refresh_from_db()

        return Response(PaymentDetailSerializer(payment, context={"request": request}).data, status=status.HTTP_200_OK)


class PaymentPlanViewSet(
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
    PaymentPlanMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
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
        "create": PaymentPlanCreateUpdateSerializer,
        "create_follow_up": PaymentPlanCreateFollowUpSerializer,
        "partial_update": PaymentPlanCreateUpdateSerializer,
        "exclude_beneficiaries": PaymentPlanExcludeBeneficiariesSerializer,
        "apply_engine_formula": ApplyEngineFormulaSerializer,
        "entitlement_import_xlsx": PaymentPlanImportFileSerializer,
        "reject": AcceptanceProcessSerializer,
        "approve": AcceptanceProcessSerializer,
        "authorize": AcceptanceProcessSerializer,
        "mark_as_released": AcceptanceProcessSerializer,
        "generate_xlsx_with_auth_code": PaymentPlanExportAuthCodeSerializer,
        "split": SplitPaymentPlanSerializer,
        "reconciliation_import_xlsx": PaymentPlanImportFileSerializer,
        "fsp_xlsx_template_list": FSPXlsxTemplateSerializer,
        "assign_funds_commitments": AssignFundsCommitmentsSerializer,
    }
    permissions_by_action = {
        "list": [
            Permissions.PM_VIEW_LIST,
        ],
        "retrieve": [
            Permissions.PM_VIEW_DETAILS,
        ],
        "create": [Permissions.PM_CREATE],
        "create_follow_up": [Permissions.PM_CREATE],
        "partial_update": [Permissions.PM_CREATE],
        "destroy": [Permissions.PM_CREATE],
        "exclude_beneficiaries": [Permissions.PM_EXCLUDE_BENEFICIARIES_FROM_FOLLOW_UP_PP],
        "apply_engine_formula": [Permissions.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS],
        "approve": [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        "authorize": [Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE],
        "mark_as_released": [Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW],
        "send_to_payment_gateway": [Permissions.PM_SEND_TO_PAYMENT_GATEWAY],
        "send_xlsx_password": [Permissions.PM_SEND_XLSX_PASSWORD],
        "generate_xlsx_with_auth_code": [Permissions.PM_DOWNLOAD_FSP_AUTH_CODE],
        "split": [Permissions.PM_SPLIT],
        "reconciliation_import_xlsx": [Permissions.PM_IMPORT_XLSX_WITH_RECONCILIATION],
        "export_pdf_payment_plan_summary": [Permissions.PM_EXPORT_PDF_SUMMARY],
        "fsp_xlsx_template_list": [Permissions.PM_EXPORT_XLSX_FOR_FSP],
        "assign_funds_commitments": [Permissions.PM_ASSIGN_FUNDS_COMMITMENTS],
    }

    def get_object(self) -> PaymentPlan:
        return get_object_or_404(PaymentPlan, id=self.kwargs.get("pk"))

    @etag_decorator(PaymentPlanListKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=PaymentPlanListKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if "target_population_id" not in request.data:
            raise ValidationError("target_population_id is required")
        payment_plan = get_object_or_404(PaymentPlan, id=request.data["target_population_id"])
        serializer = self.get_serializer(data=request.data, context={"payment_plan": payment_plan})
        serializer.is_valid(raise_exception=True)
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

    @extend_schema(request=PaymentPlanCreateFollowUpSerializer, responses={201: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="create-follow-up")
    @transaction.atomic
    def create_follow_up(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        user = request.user
        serializer = self.get_serializer(data=request.data, context={"payment_plan": payment_plan})
        serializer.is_valid(raise_exception=True)
        follow_up_pp = PaymentPlanService(payment_plan).create_follow_up(
            user,
            serializer.validated_data["dispersion_start_date"],
            serializer.validated_data["dispersion_end_date"],
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=user,
            programs=follow_up_pp.program,
            old_object=None,
            new_object=follow_up_pp,
        )
        response_serializer = PaymentPlanDetailSerializer(follow_up_pp, context={"request": request})
        return Response(
            data=response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
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

    @extend_schema(request=PaymentPlanExcludeBeneficiariesSerializer, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="exclude-beneficiaries")
    @transaction.atomic
    def exclude_beneficiaries(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()

        if payment_plan.status not in (PaymentPlan.Status.OPEN, PaymentPlan.Status.LOCKED):
            raise ValidationError("Beneficiary can be excluded only for 'Open' or 'Locked' status of Payment Plan")

        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
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

    @action(detail=True, methods=["get"], PERMISSIONS=[Permissions.PM_LOCK_AND_UNLOCK])
    @transaction.atomic
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
    @transaction.atomic
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

    @action(detail=True, methods=["get"], PERMISSIONS=[Permissions.PM_LOCK_AND_UNLOCK_FSP], url_path="lock-fsp")
    @transaction.atomic
    def lock_fsp(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)
        payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(
            input_data={"action": PaymentPlan.Action.LOCK_FSP}, user=request.user
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Payment Plan FSP locked"})

    @action(detail=True, methods=["get"], PERMISSIONS=[Permissions.PM_LOCK_AND_UNLOCK_FSP], url_path="unlock-fsp")
    @transaction.atomic
    def unlock_fsp(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)
        payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(
            input_data={"action": PaymentPlan.Action.UNLOCK_FSP}, user=request.user
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Payment Plan FSP unlocked"})

    @extend_schema(request=ApplyEngineFormulaSerializer, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="apply-engine-formula")
    @transaction.atomic
    def apply_engine_formula(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
        )
        if serializer.is_valid():
            engine_formula_rule_id = serializer.validated_data["engine_formula_rule_id"]
            if version := serializer.validated_data.get("version"):
                check_concurrency_version_in_mutation(version, payment_plan)
            engine_rule = get_object_or_404(Rule, id=engine_formula_rule_id)
            if payment_plan.status not in PaymentPlan.CAN_RUN_ENGINE_FORMULA_FOR_ENTITLEMENT:
                raise ValidationError(f"Not allowed to run engine formula within status {payment_plan.status}.")
            if not engine_rule.enabled or engine_rule.deprecated:
                raise ValidationError("This engine rule is not enabled or is deprecated.")
            # PaymentPlan entitlement
            if payment_plan.status in PaymentPlan.CAN_RUN_ENGINE_FORMULA_FOR_ENTITLEMENT:
                old_payment_plan = copy_model_object(payment_plan)
                if payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.RULE_ENGINE_RUN:
                    raise ValidationError("Rule Engine run in progress")
                payment_plan.background_action_status_steficon_run()
                payment_plan.save()
                payment_plan_apply_engine_rule.delay(str(payment_plan.pk), str(engine_rule.pk))

            log_create(
                mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
                business_area_field="business_area",
                user=request.user,
                programs=payment_plan.program.pk,
                old_object=old_payment_plan,
                new_object=payment_plan,
            )
            response_serializer = PaymentPlanDetailSerializer(payment_plan, context={"request": request})
            return Response(
                data=response_serializer.data,
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], PERMISSIONS=[Permissions.PM_VIEW_LIST], url_path="entitlement-export-xlsx")
    @transaction.atomic
    def entitlement_export_xlsx(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)

        if payment_plan.status not in [PaymentPlan.Status.LOCKED]:
            raise ValidationError("You can only export Payment List for LOCKED Payment Plan")

        payment_plan = PaymentPlanService(payment_plan=payment_plan).export_xlsx(user_id=request.user.pk)
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        request=PaymentPlanImportFileSerializer, responses={200: PaymentPlanDetailSerializer, 400: XlsxErrorSerializer}
    )
    @action(
        detail=True,
        methods=["post"],
        PERMISSIONS=[Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS],
        url_path="entitlement-import-xlsx",
    )
    @transaction.atomic
    def entitlement_import_xlsx(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        if payment_plan.status != PaymentPlan.Status.LOCKED:
            raise ValidationError("User can only import for LOCKED Payment Plan")
        if payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS:
            raise ValidationError("Import in progress")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]
        with transaction.atomic():
            import_service = XlsxPaymentPlanImportService(payment_plan, file)
            import_service.open_workbook()
            import_service.validate()
            if import_service.errors:
                return Response(
                    data=XlsxErrorSerializer(import_service.errors, many=True, context={"request": request}).data,
                    status=status.HTTP_400_BAD_REQUEST,
                )
            old_payment_plan = copy_model_object(payment_plan)
            if old_payment_plan.imported_file:
                old_payment_plan.imported_file = copy_model_object(payment_plan.imported_file)
            payment_plan.background_action_status_xlsx_importing_entitlements()
            payment_plan.save()
            payment_plan = import_service.create_import_xlsx_file(request.user)

            transaction.on_commit(lambda: import_payment_plan_payment_list_from_xlsx.delay(payment_plan.id))
            log_create(
                mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
                business_area_field="business_area",
                user=request.user,
                programs=payment_plan.program.pk,
                old_object=old_payment_plan,
                new_object=payment_plan,
            )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get"], PERMISSIONS=[Permissions.PM_SEND_FOR_APPROVAL], url_path="send-for-approval")
    @transaction.atomic
    def send_for_approval(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)
        payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(
            input_data={"action": PaymentPlan.Action.SEND_FOR_APPROVAL}, user=request.user
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def reject(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)

        def _get_reject_permission(status: str) -> Any:
            status_to_perm_map = {
                PaymentPlan.Status.IN_APPROVAL.name: Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
                PaymentPlan.Status.IN_AUTHORIZATION.name: Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
                PaymentPlan.Status.IN_REVIEW.name: Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
            }
            return status_to_perm_map.get(status, list(status_to_perm_map.values()))

        reject_permission = _get_reject_permission(payment_plan.status)
        request.user.has_perm(reject_permission)
        data = dict(request.data)
        data["action"] = PaymentPlan.Action.REJECT
        payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(input_data=data, user=request.user)
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def approve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)
        data = dict(request.data)
        data["action"] = PaymentPlan.Action.APPROVE
        payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(input_data=data, user=request.user)
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def authorize(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)
        data = dict(request.data)
        data["action"] = PaymentPlan.Action.AUTHORIZE
        payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(input_data=data, user=request.user)
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="mark-as-released")
    @transaction.atomic
    def mark_as_released(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)
        data = dict(request.data)
        data["action"] = PaymentPlan.Action.REVIEW
        payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(input_data=data, user=request.user)
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get"], url_path="send-to-payment-gateway")
    @transaction.atomic
    def send_to_payment_gateway(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)
        payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(
            input_data={"action": PaymentPlan.Action.SEND_TO_PAYMENT_GATEWAY}, user=request.user
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data, status=status.HTTP_200_OK
        )

    # TODO:
    @action(detail=True, methods=["post"], url_path="generate-xlsx-with-auth-code")
    @transaction.atomic
    def generate_xlsx_with_auth_code(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)
        fsp_xlsx_template_id = request.data.get("fsp_xlsx_template_id")

        if payment_plan.status not in [PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED]:
            raise ValidationError(
                "Payment List Per FSP export is only available for ACCEPTED or FINISHED Payment Plans."
            )
        if payment_plan.export_file_per_fsp is not None:
            raise ValidationError("Export failed: Payment Plan already has created exported file.")
        if fsp_xlsx_template_id and not payment_plan.can_create_xlsx_with_fsp_auth_code:
            raise ValidationError(
                "Export failed: There could be not Pending Payments and FSP communication channel should be set to API."
            )

        payment_plan = PaymentPlanService(payment_plan=payment_plan).export_xlsx_per_fsp(
            request.user.pk, fsp_xlsx_template_id
        )

        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get"], url_path="send-xlsx-password")
    @transaction.atomic
    def send_xlsx_password(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        old_payment_plan = copy_model_object(payment_plan)
        payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(
            input_data={"action": PaymentPlan.Action.SEND_XLSX_PASSWORD}, user=request.user
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get"], PERMISSIONS=[Permissions.PM_VIEW_LIST], url_path="reconciliation-export-xlsx")
    @transaction.atomic
    def reconciliation_export_xlsx(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        if payment_plan.status not in [PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED]:
            raise ValidationError(
                "Payment List Per FSP export is only available for ACCEPTED or FINISHED Payment Plans."
            )
        if not payment_plan.eligible_payments:
            raise ValidationError("Export failed: The Payment List is empty.")
        old_payment_plan = copy_model_object(payment_plan)

        payment_plan = PaymentPlanService(payment_plan=payment_plan).export_xlsx_per_fsp(request.user.id, None)
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        request=PaymentPlanImportFileSerializer, responses={200: PaymentPlanDetailSerializer, 400: XlsxErrorSerializer}
    )
    @action(detail=True, methods=["post"], url_path="reconciliation-import-xlsx", parser_classes=[DictDrfNestedParser])
    @transaction.atomic
    def reconciliation_import_xlsx(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        if payment_plan.status not in [PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED]:
            raise ValidationError(
                "Payment List Per FSP export is only available for ACCEPTED or FINISHED Payment Plans."
            )
        if (
            payment_plan.financial_service_provider.communication_channel
            != FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX
        ):
            raise ValidationError(
                "Only for FSP with Communication Channel XLSX can be imported reconciliation manually."
            )

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        file = serializer.validated_data["file"]
        with transaction.atomic():
            import_service = XlsxPaymentPlanImportPerFspService(payment_plan, file)
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

            old_payment_plan = copy_model_object(payment_plan)

            payment_plan = PaymentPlanService(payment_plan=payment_plan).import_xlsx_per_fsp(
                user=request.user, file=file
            )
            log_create(
                mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
                business_area_field="business_area",
                user=request.user,
                programs=payment_plan.program.pk,
                old_object=old_payment_plan,
                new_object=payment_plan,
            )
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def split(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        splits_sent_to_pg = payment_plan.splits.filter(
            sent_to_payment_gateway=True,
        )
        if splits_sent_to_pg.exists():
            raise ValidationError("Payment plan is already sent to payment gateway")

        if payment_plan.status != PaymentPlan.Status.ACCEPTED:
            raise ValidationError("Payment plan must be accepted to make a split")

        payments_no = request.data.get("payments_no")
        split_type = request.data["split_type"]
        if split_type == PaymentPlanSplit.SplitType.BY_RECORDS:
            if not payments_no:
                raise ValidationError("Payment Number is required for split by records")
            if (payment_plan.eligible_payments.count() // payments_no) > PaymentPlanSplit.MAX_CHUNKS:
                raise ValidationError(f"Cannot split Payment Plan into more than {PaymentPlanSplit.MAX_CHUNKS} parts")

        with transaction.atomic():
            payment_plan_service = PaymentPlanService(payment_plan=payment_plan)
            payment_plan_service.split(split_type, payments_no)
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get"], url_path="export-pdf-payment-plan-summary")
    @transaction.atomic
    def export_pdf_payment_plan_summary(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment_plan = self.get_object()
        export_pdf_payment_plan_summary.delay(payment_plan.pk, str(request.user.pk))
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data, status=status.HTTP_200_OK
        )

    @extend_schema(responses={200: FSPXlsxTemplateSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="fsp-xlsx-template-list")
    @transaction.atomic
    def fsp_xlsx_template_list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        qs = FinancialServiceProviderXlsxTemplate.objects.filter(
            financial_service_providers__allowed_business_areas__slug=self.business_area_slug
        ).order_by("name")
        return Response(data=FSPXlsxTemplateSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(request=AssignFundsCommitmentsSerializer, responses={200: PaymentPlanDetailSerializer})
    @action(detail=True, methods=["post"], url_path="assign-funds-commitments")
    @transaction.atomic
    def assign_funds_commitments(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fund_commitment_items_ids = serializer.validated_data["fund_commitment_items_ids"]

        payment_plan = self.get_object()
        if payment_plan.status != PaymentPlan.Status.IN_REVIEW:
            raise ValidationError("Payment plan must be in review")

        funds_commitment_items = FundsCommitmentItem.objects.filter(rec_serial_number__in=fund_commitment_items_ids)
        if funds_commitment_items.filter(payment_plan_id__isnull=False).exclude(payment_plan=payment_plan).exists():
            raise ValidationError("Chosen Funds Commitments are already assigned to different Payment Plan")

        if funds_commitment_items.exclude(office=payment_plan.business_area).exists():
            raise ValidationError("Chosen Funds Commitments have wrong Business Area")

        FundsCommitmentItem.objects.filter(payment_plan=payment_plan).update(payment_plan=None)
        funds_commitment_items.update(payment_plan=payment_plan)

        payment_plan.refresh_from_db()
        return Response(
            data=PaymentPlanDetailSerializer(payment_plan, context={"request": request}).data, status=status.HTTP_200_OK
        )


class TargetPopulationViewSet(
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
    PaymentPlanMixin,
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
    }
    filterset_class = TargetPopulationFilter

    def get_object(self) -> PaymentPlan:
        return get_object_or_404(PaymentPlan, id=self.kwargs.get("pk"))

    @etag_decorator(TargetPopulationListKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=TargetPopulationListKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @transaction.atomic
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
    @transaction.atomic
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
    @transaction.atomic
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
    @transaction.atomic
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

    @extend_schema(responses={200: PendingPaymentSerializer(many=True)})
    @action(
        detail=True,
        methods=["get"],
        url_path="pending-payments",
        PERMISSIONS=[Permissions.TARGETING_VIEW_DETAILS],
        filter_backends=(),
    )
    @transaction.atomic
    def pending_payments(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        tp = self.get_object()
        queryset = tp.payment_items.all()
        data = PendingPaymentSerializer(self.paginate_queryset(queryset), many=True).data
        return self.get_paginated_response(data)

    @action(
        detail=True,
        methods=["get"],
        PERMISSIONS=[Permissions.TARGETING_CREATE, Permissions.TARGETING_SEND],
        url_path="mark-ready",
    )
    @transaction.atomic
    def mark_ready(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        tp = self.get_object()
        old_tp = copy_model_object(tp)

        payment_plan = PaymentPlanService(tp).execute_update_status_action(
            input_data={"action": PaymentPlan.Action.DRAFT}, user=request.user
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
    @transaction.atomic
    def copy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        request.data["target_population_id"] = kwargs.get("pk")

        serializer = self.get_serializer(
            data=request.data,
        )
        if serializer.is_valid():
            name = serializer.validated_data["name"].strip()
            payment_plan_id = serializer.validated_data["target_population_id"]
            program_cycle_id = serializer.validated_data["program_cycle_id"]
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
            PaymentPlanService.copy_target_criteria(payment_plan, payment_plan_copy)
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
        engine_rule = get_object_or_404(Rule, id=engine_formula_rule_id)
        # tp vulnerability_score
        if tp.status not in PaymentPlan.CAN_RUN_ENGINE_FORMULA_FOR_VULNERABILITY_SCORE:
            raise ValidationError(f"Not allowed to run engine formula within status {tp.status}.")
        if not engine_rule.enabled or engine_rule.deprecated:
            raise ValidationError("This engine rule is not enabled or is deprecated.")
        old_tp = copy_model_object(tp)
        tp.steficon_rule_targeting = engine_rule.latest
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
    @transaction.atomic
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

    @transaction.atomic
    def _perform_payment_plan_status_action(
        self,
        payment_plan_id: str,
        input_data: dict,
        business_area: BusinessArea,
        request: Request,
    ) -> None:
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

    def _get_action_permission(self, action_name: str) -> str | None:
        action_to_permissions_map = {
            PaymentPlan.Action.APPROVE.name: Permissions.PM_ACCEPTANCE_PROCESS_APPROVE.name,
            PaymentPlan.Action.AUTHORIZE.name: Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE.name,
            PaymentPlan.Action.REVIEW.name: Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW.name,
        }
        return action_to_permissions_map.get(action_name)


class PaymentPlanSupportingDocumentViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, BaseViewSet):
    serializer_class = PaymentPlanSupportingDocumentSerializer
    lookup_field = "file_id"

    permissions_by_action = {
        "create": [Permissions.PM_UPLOAD_SUPPORTING_DOCUMENT],
        "delete": [Permissions.PM_DELETE_SUPPORTING_DOCUMENT],
        "destroy": [Permissions.PM_DELETE_SUPPORTING_DOCUMENT],
        "download": [Permissions.PM_DOWNLOAD_SUPPORTING_DOCUMENT],
    }

    def get_queryset(self) -> QuerySet:
        payment_plan_id = self.kwargs.get("payment_plan_id")
        return PaymentPlanSupportingDocument.objects.filter(payment_plan_id=payment_plan_id)

    def get_object(self) -> PaymentPlanSupportingDocument:
        payment_plan = get_object_or_404(PaymentPlan, id=self.kwargs.get("payment_plan_id"))
        return get_object_or_404(
            PaymentPlanSupportingDocument, id=self.kwargs.get("file_id"), payment_plan=payment_plan
        )

    @transaction.atomic
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        document = self.get_object()
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    @transaction.atomic
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
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    lookup_field = "payment_id"
    PERMISSIONS = [Permissions.PM_VIEW_DETAILS, Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS]
    serializer_classes_by_action = {
        "list": PaymentListSerializer,
        "retrieve": PaymentDetailSerializer,
        "revert_mark_as_failed": RevertMarkPaymentAsFailedSerializer,
    }
    permissions_by_action = {
        "list": [
            Permissions.PM_VIEW_DETAILS,
        ],
        "retrieve": [
            Permissions.PM_VIEW_DETAILS,
        ],
    }

    def get_object(self) -> Payment:
        payment_id = self.kwargs["payment_id"]
        return get_object_or_404(Payment, id=payment_id)

    def get_queryset(self) -> QuerySet:
        return Payment.objects.filter(parent_id=self.kwargs["payment_plan_id"])

    @action(
        detail=True, methods=["get"], PERMISSIONS=[Permissions.PM_MARK_PAYMENT_AS_FAILED], url_path="mark-as-failed"
    )
    @transaction.atomic
    def mark_as_failed(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        payment = self.get_object()
        mark_as_failed(payment)
        return Response(
            data=PaymentDetailSerializer(payment, context={"request": request}).data, status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["post"],
        PERMISSIONS=[Permissions.PM_MARK_PAYMENT_AS_FAILED],
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
        delivery_date = datetime.combine(delivery_date, datetime.min.time())
        revert_mark_as_failed(payment, Decimal(delivered_quantity), delivery_date)
        return Response(
            data=PaymentDetailSerializer(payment, context={"request": request}).data, status=status.HTTP_200_OK
        )


@extend_schema(responses={200: FspChoicesSerializer(many=True)})  # type: ignore
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def available_fsps_for_delivery_mechanisms(
    request: Request, business_area_slug: str, *args: Any, **kwargs: Any
) -> Response:
    delivery_mechanisms = DeliveryMechanism.get_choices()

    def get_fsps(mechanism_name: str) -> list[dict[str, Any]]:
        fsps_qs = FinancialServiceProvider.objects.filter(
            Q(fsp_xlsx_template_per_delivery_mechanisms__delivery_mechanism__name=mechanism_name)
            | Q(fsp_xlsx_template_per_delivery_mechanisms__isnull=True),
            delivery_mechanisms__name=mechanism_name,
            allowed_business_areas__slug=business_area_slug,
        ).distinct()

        return list(fsps_qs.values("id", "name"))

    list_resp = [
        {
            "delivery_mechanism": {"code": delivery_mechanism[0], "name": delivery_mechanism[1]},
            "fsps": get_fsps(delivery_mechanism[1]),
        }
        for delivery_mechanism in delivery_mechanisms
    ]

    serializer = FspChoicesSerializer(list_resp, many=True)
    return Response(serializer.data)
