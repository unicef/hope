import logging
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q, Prefetch, QuerySet
from django.http import FileResponse
from django.utils import timezone

from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework_extensions.cache.decorators import cache_response

from hope.api.caches import etag_decorator
from hope.apps.account.models import RoleAssignment, User
from hope.apps.account.permissions import Permissions
from hope.apps.core.api.filters import UpdatedAtFilter
from hope.apps.core.api.mixins import (
    BaseViewSet,
    ProgramMixin,
    SerializerActionMixin, CountActionMixin,
)
from hope.apps.core.api.parsers import DictDrfNestedParser
from hope.apps.core.models import FlexibleAttribute
from hope.apps.periodic_data_update.api.caches import PeriodicFieldKeyConstructor
from hope.apps.periodic_data_update.api.filters import PDUOnlineEditFilter
from hope.apps.periodic_data_update.api.mixins import PDUOnlineEditAuthorizedUserMixin
from hope.apps.periodic_data_update.api.serializers import (
    PDUXlsxTemplateCreateSerializer,
    PDUXlsxTemplateDetailSerializer,
    PDUXlsxTemplateListSerializer,
    PDUXlsxUploadDetailSerializer,
    PDUXlsxUploadListSerializer,
    PDUXlsxUploadSerializer,
    PeriodicFieldSerializer,
    PDUOnlineEditListSerializer,
    PDUOnlineEditDetailSerializer,
    PDUOnlineEditCreateSerializer,
    PDUOnlineEditSaveDataSerializer,
    PDUOnlineEditSendBackSerializer,
    BulkSerializer,
    PDUOnlineEditUpdateAuthorizedUsersSerializer,
    AuthorizedUserSerializer,
    PDU_ONLINE_EDIT_RELATED_PERMISSIONS,
)
from hope.apps.periodic_data_update.models import (
    PDUXlsxTemplate,
    PDUXlsxUpload,
    PDUOnlineEdit,
    PDUOnlineEditSentBackComment,
)
from hope.apps.periodic_data_update.service.periodic_data_update_import_service import PDUXlsxImportService

logger = logging.getLogger(__name__)


class PDUXlsxTemplateViewSet(
    SerializerActionMixin,
    ProgramMixin,
    CountActionMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = PDUXlsxTemplate.objects.all()
    serializer_classes_by_action = {
        "list": PDUXlsxTemplateListSerializer,
        "retrieve": PDUXlsxTemplateDetailSerializer,
        "create": PDUXlsxTemplateCreateSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        "retrieve": [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        "create": [Permissions.PDU_TEMPLATE_CREATE],
        "export": [Permissions.PDU_TEMPLATE_CREATE],
        "download": [Permissions.PDU_TEMPLATE_DOWNLOAD],
    }
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = UpdatedAtFilter

    # caching disabled until we decide how to handle cache + dynamic status
    # to enable - just uncomment the decorators and related tests
    # @etag_decorator(PDUTemplateKeyConstructor)
    # @cache_response(timeout=config.REST_API_TTL, key_func=PDUTemplateKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    # export the template during template creation
    def perform_create(self, serializer: BaseSerializer) -> None:
        pdu_template = serializer.save()
        pdu_template.queue()

    @action(detail=True, methods=["post"])
    def export(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        pdu_template = self.get_object()

        if pdu_template.status == PDUXlsxTemplate.Status.EXPORTING:
            raise ValidationError("Template is already being exported")
        if pdu_template.file:
            raise ValidationError("Template is already exported")

        pdu_template.queue()
        return Response(status=status.HTTP_200_OK, data={"message": "Exporting template"})

    @action(detail=True, methods=["get"])
    def download(self, request: Request, *args: Any, **kwargs: Any) -> FileResponse:
        pdu_template = self.get_object()

        if pdu_template.status != PDUXlsxTemplate.Status.EXPORTED:
            raise ValidationError("Template is not exported yet")
        if not pdu_template.number_of_records:
            raise ValidationError("Template has no records")
        if not pdu_template.file:
            logger.warning(f"XLSX File not found. PDUXlsxTemplate ID: {pdu_template.id}")
            raise ValidationError("Template file is missing")

        return FileResponse(
            pdu_template.file.file.open(),
            as_attachment=True,
            filename=pdu_template.file.file.name,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


class PDUXlsxUploadViewSet(
    SerializerActionMixin,
    ProgramMixin,
    CountActionMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = PDUXlsxUpload.objects.all()
    program_model_field = "template__program"
    serializer_classes_by_action = {
        "list": PDUXlsxUploadListSerializer,
        "upload": PDUXlsxUploadSerializer,
        "retrieve": PDUXlsxUploadDetailSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        "retrieve": [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        "upload": [Permissions.PDU_UPLOAD],
    }
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = UpdatedAtFilter

    # caching disabled until we decide how to handle cache + dynamic status
    # to enable - just uncomment the decorators and related tests
    # @etag_decorator(PDUUpdateKeyConstructor)
    # @cache_response(timeout=config.REST_API_TTL, key_func=PDUUpdateKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["post"], parser_classes=[DictDrfNestedParser])
    def upload(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(
            data=request.data,
        )
        if serializer.is_valid():
            serializer.validated_data["created_by"] = request.user
            try:
                serializer.validated_data["template"] = (
                    PDUXlsxImportService.read_periodic_data_update_template_object(
                        serializer.validated_data["file"]
                    )
                )
            except DjangoValidationError as e:
                return Response(
                    data={"error": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            upload_instance = serializer.save()

            upload_instance.queue()

            return Response(
                data=serializer.data,
                status=status.HTTP_202_ACCEPTED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # pragma: no cover


class PDUOnlineEditViewSet(
    PDUOnlineEditAuthorizedUserMixin,
    SerializerActionMixin,
    ProgramMixin,
    CountActionMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = PDUOnlineEdit.objects.all()
    serializer_classes_by_action = {
        "list": PDUOnlineEditListSerializer,
        "retrieve": PDUOnlineEditDetailSerializer,
        "create": PDUOnlineEditCreateSerializer,
        "update_authorized_users": PDUOnlineEditUpdateAuthorizedUsersSerializer,
        "save_data": PDUOnlineEditSaveDataSerializer, # TODO: PDU - handle the update of edit_data
        "send_back": PDUOnlineEditSendBackSerializer,
        "bulk_approve": BulkSerializer,
        "bulk_merge": BulkSerializer,
        "users_available": AuthorizedUserSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        "retrieve": [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        "create": [Permissions.PDU_TEMPLATE_CREATE],
        "update_authorized_users": [Permissions.PDU_TEMPLATE_CREATE],
        "save_data": [Permissions.PDU_ONLINE_SAVE_DATA],
        "send_for_approval": [Permissions.PDU_ONLINE_SAVE_DATA],
        "send_back": [Permissions.PDU_ONLINE_APPROVE],
        "bulk_approve": [Permissions.PDU_ONLINE_APPROVE],
        "bulk_merge": [Permissions.PDU_ONLINE_MERGE],
        "users_available": [Permissions.PDU_TEMPLATE_CREATE],
    }
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = PDUOnlineEditFilter

    def get_queryset(self) -> QuerySet[PDUOnlineEdit]:
        return (
            super()
            .get_queryset()
            .select_related("created_by", "approved_by")
            .prefetch_related(
                Prefetch("authorized_users", queryset=User.objects.order_by("first_name", "last_name", "username")),
            )
        )

    def perform_create(self, serializer: BaseSerializer) -> None:
        filters = serializer.validated_data.get("filters", {})
        rounds_data = serializer.validated_data.get("rounds_data", [])
        pdu_online_edit = serializer.save()
        task_kwargs = {
            "pdu_online_edit_id": pdu_online_edit.id,
            "filters": filters,
            "rounds_data": rounds_data,
        }
        pdu_online_edit.queue(task_name="generate_edit_data", **task_kwargs)

    @action(detail=True, methods=["post"])
    def update_authorized_users(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if self.request.user != instance.created_by:
            raise ValidationError("Only the creator of the PDU Online Edit can update authorized users.")

        serializer.save()
        return Response(status=status.HTTP_200_OK, data={"message": "Authorized users updated successfully."})

    @action(detail=True, methods=["post"])
    def send_for_approval(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        self.check_user_authorization(request)
        instance = self.get_object()
        if instance.status != PDUOnlineEdit.Status.NEW:
            raise ValidationError("Only new edits can be sent for approval.")
        if hasattr(instance, "sent_back_comment"):  # clean up any previous sent back comment
            instance.sent_back_comment.delete()
        instance.status = PDUOnlineEdit.Status.READY
        instance.save()
        return Response(status=status.HTTP_200_OK, data={"message": "PDU Online Edit sent for approval."})

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def send_back(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        self.check_user_authorization(request)
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if instance.status != PDUOnlineEdit.Status.READY:
            raise ValidationError("PDU Online Edit is not in the 'Ready' status and cannot be sent back.")

        instance.status = PDUOnlineEdit.Status.NEW
        instance.save()

        PDUOnlineEditSentBackComment.objects.create(
            comment=serializer.validated_data["sent_back_comment"],
            created_by=request.user,
            pdu_online_edit=instance,
        )

        return Response(status=status.HTTP_200_OK, data={"message": "PDU Online Edit sent back successfully."})

    @action(detail=False, methods=["post"])
    def bulk_approve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        self.check_user_authorization(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pdu_edits = self.get_queryset().filter(pk__in=serializer.validated_data["ids"])

        if pdu_edits.exclude(status=PDUOnlineEdit.Status.READY).exists():
            raise ValidationError("PDU Online Edit is not in the 'Ready' status and cannot be approved.")

        approved_count = pdu_edits.update(
            status=PDUOnlineEdit.Status.APPROVED,
            approved_by=request.user,
            approved_at=timezone.now(),
        )

        return Response(
            status=status.HTTP_200_OK, data={"message": f"{approved_count} PDU Online Edits approved successfully."}
        )

    @action(detail=False, methods=["post"])
    def bulk_merge(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        self.check_user_authorization(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pdu_edits = self.get_queryset().filter(pk__in=serializer.validated_data["ids"])

        if pdu_edits.exclude(status=PDUOnlineEdit.Status.APPROVED).exists():
            raise ValidationError(
                "PDU Online Edit is not in the 'Approved' status and cannot be merged."
            )

        pdu_edits.update(status=PDUOnlineEdit.Status.PENDING_MERGE)

        for pdu_edit in pdu_edits:
            pdu_edit.queue(task_name="merge")

        return Response(
            status=status.HTTP_200_OK, data={"message": f"{pdu_edits.count()} PDU Online Edits queued for merging."}
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="permission",
                type=str,
                description="Filter by permission",
                required=False,
                enum=[perm.value for perm in PDU_ONLINE_EDIT_RELATED_PERMISSIONS],
            )
        ],
        responses={200: AuthorizedUserSerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def users_available(self, request: Request, *args: Any, **kwargs: Any
    ) -> Response:
        business_area_slug = self.kwargs.get("business_area_slug")
        program_slug = self.kwargs.get("program_slug")
        permissions_to_check = [perm.value for perm in PDU_ONLINE_EDIT_RELATED_PERMISSIONS]

        # possible to filter by specific pdu permission
        permission_filter = self.request.query_params.get("permission")
        if permission_filter:
            if permission_filter not in permissions_to_check:
                raise ValidationError(f"Invalid permission. Choose from {', '.join(permissions_to_check)}")
            permissions_to_check = [permission_filter]

        role_assignments_with_pdu_online_edit_related_permissions = RoleAssignment.objects.filter(
            role__permissions__overlap=permissions_to_check,
            business_area__slug=business_area_slug,
            program__slug=program_slug,
        ).exclude(expiry_date__lt=timezone.now())
        users_available = User.objects.filter(
            Q(role_assignments__in=role_assignments_with_pdu_online_edit_related_permissions) |
            Q(partner__role_assignments__in=role_assignments_with_pdu_online_edit_related_permissions)
        ).distinct().order_by("first_name", "last_name", "username")

        # Prefetch role_assignments with relevant permissions for user and partner to avoid extra queries in serializer
        users_available = users_available.prefetch_related(
            Prefetch(
                "role_assignments",
                queryset=role_assignments_with_pdu_online_edit_related_permissions,
                to_attr="cached_relevant_role_assignments"
            ),
            Prefetch(
                "partner__role_assignments",
                queryset=role_assignments_with_pdu_online_edit_related_permissions,
                to_attr="cached_relevant_role_assignments_partner"
            )
        )

        serializer = self.get_serializer(users_available, many=True)
        return Response(serializer.data)


class PeriodicFieldViewSet(
    ProgramMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = FlexibleAttribute.objects.filter(type=FlexibleAttribute.PDU)
    serializer_class = PeriodicFieldSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = UpdatedAtFilter

    @etag_decorator(PeriodicFieldKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=PeriodicFieldKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
