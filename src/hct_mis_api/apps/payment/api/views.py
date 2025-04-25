import logging
import mimetypes
from typing import Any, Optional

from django.db import transaction
from django.db.models import QuerySet
from django.http import FileResponse

from constance import config
from django_filters import rest_framework as filters
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
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
    ProgramMixin,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.payment.api.caches import PaymentPlanKeyConstructor
from hct_mis_api.apps.payment.api.filters import PaymentPlanFilter
from hct_mis_api.apps.payment.api.serializers import (
    PaymentPlanBulkActionSerializer,
    PaymentPlanSerializer,
    PaymentPlanSupportingDocumentSerializer,
)
from hct_mis_api.apps.payment.models import PaymentPlan, PaymentPlanSupportingDocument
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService

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


class PaymentPlanViewSet(ProgramMixin, PaymentPlanMixin, mixins.ListModelMixin, BaseViewSet):
    program_model_field = "program_cycle__program"
    queryset = PaymentPlan.objects.all()
    PERMISSIONS = [Permissions.PM_VIEW_LIST]


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
            input_data=input_data, user=request.user  # type: ignore
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
