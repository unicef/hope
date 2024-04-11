from typing import Any, Optional

from django.db import transaction
from django.db.models import QuerySet

from django_filters import rest_framework as filters
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from hct_mis_api.apps.account.api.permissions import (
    PaymentViewListManagerialPermission,
    PMViewListPermission,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.core.api.mixins import BusinessAreaMixin, BusinessAreaProgramMixin
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.payment.api.filters import PaymentPlanFilter
from hct_mis_api.apps.payment.api.serializers import (
    PaymentPlanBulkActionSerializer,
    PaymentPlanSerializer,
)
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService


class PaymentPlanMixin:
    serializer_class = PaymentPlanSerializer
    permission_classes = []
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


class PaymentPlanViewSet(BusinessAreaProgramMixin, PaymentPlanMixin, mixins.ListModelMixin, GenericViewSet):
    permission_classes = [
        PMViewListPermission,
    ]

    def get_queryset(self) -> QuerySet:
        business_area = self.get_business_area()
        program = self.get_program()
        return PaymentPlan.objects.filter(business_area=business_area, program=program)


class PaymentPlanManagerialViewSet(BusinessAreaMixin, PaymentPlanMixin, mixins.ListModelMixin, GenericViewSet):
    permission_classes = [
        PMViewListPermission,
        PaymentViewListManagerialPermission,
    ]

    def get_queryset(self) -> QuerySet:
        business_area = self.get_business_area()
        queryset = PaymentPlan.objects.filter(business_area=business_area)
        program_ids = self.request.user.partner.get_program_ids_for_business_area(str(business_area.id))
        return queryset.filter(
            status__in=[
                PaymentPlan.Status.IN_APPROVAL,
                PaymentPlan.Status.IN_AUTHORIZATION,
                PaymentPlan.Status.IN_REVIEW,
            ],
            program__in=program_ids,
        )

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
        business_area = self.get_business_area()

        with transaction.atomic():
            for payment_plan_id_str in serializer.validated_data["ids"]:
                self._perform_payment_plan_status_action(
                    payment_plan_id_str,
                    input_data,
                    business_area,
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

        if not self.request.user.has_permission(
            self._get_action_permission(input_data["action"]),
            business_area,
            payment_plan.program_id,
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
            programs=payment_plan.get_program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )

    def _get_action_permission(self, action_name: str) -> Optional[str]:
        action_to_permissions_map = {
            PaymentPlan.Action.APPROVE.name: Permissions.PM_ACCEPTANCE_PROCESS_APPROVE.name,
            PaymentPlan.Action.AUTHORIZE.name: Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE.name,
            PaymentPlan.Action.REVIEW.name: Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW.name,
        }
        return action_to_permissions_map.get(action_name, None)
