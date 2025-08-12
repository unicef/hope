import logging
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.http import FileResponse
from django.utils import timezone

from constance import config
from django_filters.rest_framework import DjangoFilterBackend
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
from hope.apps.periodic_data_update.api.mixins import PeriodicDataUpdateOnlineEditAuthorizedUserMixin
from hope.apps.periodic_data_update.api.serializers import (
    PeriodicDataUpdateXlsxTemplateCreateSerializer,
    PeriodicDataUpdateXlsxTemplateDetailSerializer,
    PeriodicDataUpdateXlsxTemplateListSerializer,
    PeriodicDataUpdateXlsxUploadDetailSerializer,
    PeriodicDataUpdateXlsxUploadListSerializer,
    PeriodicDataUpdateXlsxUploadSerializer,
    PeriodicFieldSerializer, PeriodicDataUpdateOnlineEditListSerializer, PeriodicDataUpdateOnlineEditDetailSerializer,
    PeriodicDataUpdateOnlineEditCreateSerializer, PeriodicDataUpdateOnlineEditSaveDataSerializer,
    PeriodicDataUpdateOnlineEditSendBackSerializer, BulkSerializer,
)
from hope.apps.periodic_data_update.models import (
    PeriodicDataUpdateXlsxTemplate,
    PeriodicDataUpdateXlsxUpload, PeriodicDataUpdateOnlineEdit, PeriodicDataUpdateOnlineEditSentBackComment,
)
from hope.apps.periodic_data_update.service.periodic_data_update_import_service import PeriodicDataUpdateImportService

logger = logging.getLogger(__name__)


class PeriodicDataUpdateXlsxTemplateViewSet(
    SerializerActionMixin,
    ProgramMixin,
    CountActionMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = PeriodicDataUpdateXlsxTemplate.objects.all()
    serializer_classes_by_action = {
        "list": PeriodicDataUpdateXlsxTemplateListSerializer,
        "retrieve": PeriodicDataUpdateXlsxTemplateDetailSerializer,
        "create": PeriodicDataUpdateXlsxTemplateCreateSerializer,
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

        if pdu_template.status == PeriodicDataUpdateXlsxTemplate.Status.EXPORTING:
            raise ValidationError("Template is already being exported")
        if pdu_template.file:
            raise ValidationError("Template is already exported")

        pdu_template.queue()
        return Response(status=status.HTTP_200_OK, data={"message": "Exporting template"})

    @action(detail=True, methods=["get"])
    def download(self, request: Request, *args: Any, **kwargs: Any) -> FileResponse:
        pdu_template = self.get_object()

        if pdu_template.status != PeriodicDataUpdateXlsxTemplate.Status.EXPORTED:
            raise ValidationError("Template is not exported yet")
        if not pdu_template.number_of_records:
            raise ValidationError("Template has no records")
        if not pdu_template.file:
            logger.warning(f"XLSX File not found. PeriodicDataUpdateXlsxTemplate ID: {pdu_template.id}")
            raise ValidationError("Template file is missing")

        return FileResponse(
            pdu_template.file.file.open(),
            as_attachment=True,
            filename=pdu_template.file.file.name,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


class PeriodicDataUpdateXlsxUploadViewSet(
    SerializerActionMixin,
    ProgramMixin,
    CountActionMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = PeriodicDataUpdateXlsxUpload.objects.all()
    program_model_field = "template__program"
    serializer_classes_by_action = {
        "list": PeriodicDataUpdateXlsxUploadListSerializer,
        "upload": PeriodicDataUpdateXlsxUploadSerializer,
        "retrieve": PeriodicDataUpdateXlsxUploadDetailSerializer,
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
                    PeriodicDataUpdateImportService.read_periodic_data_update_template_object(
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


class PeriodicDataUpdateOnlineEditViewSet(
    PeriodicDataUpdateOnlineEditAuthorizedUserMixin,
    SerializerActionMixin,
    ProgramMixin,
    CountActionMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = PeriodicDataUpdateOnlineEdit.objects.all()
    serializer_classes_by_action = {
        "list": PeriodicDataUpdateOnlineEditListSerializer,
        "retrieve": PeriodicDataUpdateOnlineEditDetailSerializer,
        "create": PeriodicDataUpdateOnlineEditCreateSerializer,
        "save_data": PeriodicDataUpdateOnlineEditSaveDataSerializer,
        "send_back": PeriodicDataUpdateOnlineEditSendBackSerializer,
        "bulk_approve": BulkSerializer,
        "bulk_merge": BulkSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        "retrieve": [Permissions.PDU_VIEW_LIST_AND_DETAILS],
        "create": [Permissions.PDU_TEMPLATE_CREATE],
        "save_data": [Permissions.PDU_ONLINE_SAVE_DATA],
        "send_for_approval": [Permissions.PDU_ONLINE_SAVE_DATA],
        "send_back": [Permissions.PDU_ONLINE_APPROVE],
        "bulk_approve": [Permissions.PDU_ONLINE_APPROVE],
        "bulk_merge": [Permissions.PDU_ONLINE_MERGE],
    }
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = UpdatedAtFilter # TODO: PDU - add custom filter for status

    @action(detail=True, methods=["post"])
    def send_for_approval(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        self.check_user_authorization(request)
        instance = self.get_object()
        if instance.status != PeriodicDataUpdateOnlineEdit.Status.NEW:
            raise ValidationError("Only new edits can be sent for approval.")
        if hasattr(instance, "sent_back_comment"):  # clean up any previous sent back comment
            instance.sent_back_comment.delete()
        instance.status = PeriodicDataUpdateOnlineEdit.Status.READY
        instance.save()
        return Response(status=status.HTTP_200_OK, data={"message": "PDU Online Edit sent for approval."})

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def send_back(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        self.check_user_authorization(request)
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if instance.status != PeriodicDataUpdateOnlineEdit.Status.READY:
            raise ValidationError("PDU Online Edit is not in the 'Ready' status and cannot be sent back.")

        instance.status = PeriodicDataUpdateOnlineEdit.Status.NEW
        instance.save()

        PeriodicDataUpdateOnlineEditSentBackComment.objects.create(
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

        if pdu_edits.exclude(status=PeriodicDataUpdateOnlineEdit.Status.READY).exists():
            raise ValidationError("PDU Online Edit is not in the 'Ready' status and cannot be approved.")

        approved_count = pdu_edits.update(
            status=PeriodicDataUpdateOnlineEdit.Status.APPROVED,
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

        if pdu_edits.exclude(status=PeriodicDataUpdateOnlineEdit.Status.APPROVED).exists():
            raise ValidationError(
                "PDU Online Edit is not in the 'Approved' status and cannot be merged."
            )

        merged_count = pdu_edits.update(
            status=PeriodicDataUpdateOnlineEdit.Status.MERGED,
        )

        return Response(
            status=status.HTTP_200_OK, data={"message": f"{merged_count} PDU Online Edits merged successfully."}
        )


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
