import logging
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import QuerySet

from constance import config
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework_extensions.cache.decorators import cache_response

from hct_mis_api.api.caches import etag_decorator
from hct_mis_api.apps.account.api.permissions import (
    PDUTemplateCreatePermission,
    PDUTemplateDownloadPermission,
    PDUUploadPermission,
    PDUViewListAndDetailsPermission,
)
from hct_mis_api.apps.core.api.mixins import (
    ActionMixin,
    BusinessAreaProgramMixin,
    ProgramMixin,
)
from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.periodic_data_update.api.caches import (
    PDUTemplateKeyConstructor,
    PDUUpdateKeyConstructor,
    PeriodicDataFieldKeyConstructor,
)
from hct_mis_api.apps.periodic_data_update.api.serializers import (
    PeriodicDataFieldSerializer,
    PeriodicDataUpdateTemplateCreateSerializer,
    PeriodicDataUpdateTemplateDetailSerializer,
    PeriodicDataUpdateTemplateListSerializer,
    PeriodicDataUpdateUploadDetailSerializer,
    PeriodicDataUpdateUploadListSerializer,
    PeriodicDataUpdateUploadSerializer,
)
from hct_mis_api.apps.periodic_data_update.models import (
    PeriodicDataUpdateTemplate,
    PeriodicDataUpdateUpload,
)
from hct_mis_api.apps.periodic_data_update.service.periodic_data_update_export_template_service import (
    PeriodicDataUpdateExportTemplateService,
)
from hct_mis_api.apps.periodic_data_update.service.periodic_data_update_import_service import (
    PeriodicDataUpdateImportService,
)

logger = logging.getLogger(__name__)


class PeriodicDataUpdateTemplateViewSet(
    ActionMixin,
    BusinessAreaProgramMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_classes_by_action = {
        "list": PeriodicDataUpdateTemplateListSerializer,
        "retrieve": PeriodicDataUpdateTemplateDetailSerializer,
        "create": PeriodicDataUpdateTemplateCreateSerializer,
    }
    permission_classes_by_action = {
        "list": [PDUViewListAndDetailsPermission],
        "retrieve": [PDUViewListAndDetailsPermission],
        "create": [PDUTemplateCreatePermission],
        "export": [PDUTemplateCreatePermission],
        "download": [PDUTemplateDownloadPermission],
    }
    filter_backends = (OrderingFilter,)

    def get_queryset(self) -> QuerySet:
        business_area = self.get_business_area()
        program = self.get_program()
        return PeriodicDataUpdateTemplate.objects.filter(business_area=business_area, program=program)

    @etag_decorator(PDUTemplateKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=PDUTemplateKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    # export the template during template creation
    def perform_create(self, serializer: BaseSerializer) -> None:
        pdu_template = serializer.save()
        service = PeriodicDataUpdateExportTemplateService(pdu_template)
        service.generate_workbook()
        service.save_xlsx_file()

    @action(detail=True, methods=["get"])
    def export(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        pdu_template = self.get_object()
        if pdu_template.status == PeriodicDataUpdateTemplate.Status.EXPORTING:
            raise ValidationError("Template is already being exported")
        if pdu_template.file:
            raise ValidationError("Template is already exported")
        pdu_template.queue()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    def download(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        pdu_template = self.get_object()

        if pdu_template.status != PeriodicDataUpdateTemplate.Status.EXPORTED:
            raise ValidationError("Template is not exported yet")
        if not pdu_template.number_of_records:
            raise ValidationError("Template has no records")
        if template_file := pdu_template.file:
            return Response({"url": template_file.file.url}, status=status.HTTP_200_OK)
        else:
            logger.error(f"XLSX File not found. PeriodicDataUpdateTemplate ID: {pdu_template.id}")
            raise ValidationError("Template file is missing")


class PeriodicDataUpdateUploadViewSet(
    ActionMixin,
    BusinessAreaProgramMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_classes_by_action = {
        "list": PeriodicDataUpdateUploadListSerializer,
        "upload": PeriodicDataUpdateUploadSerializer,
        "retrieve": PeriodicDataUpdateUploadDetailSerializer,
    }
    permission_classes_by_action = {
        "list": [PDUViewListAndDetailsPermission],
        "retrieve": [PDUViewListAndDetailsPermission],
        "upload": [PDUUploadPermission],
    }
    filter_backends = (OrderingFilter,)

    def get_queryset(self) -> QuerySet:
        business_area = self.get_business_area()
        program = self.get_program()
        return PeriodicDataUpdateUpload.objects.filter(template__business_area=business_area, template__program=program)

    @etag_decorator(PDUUpdateKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=PDUUpdateKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["post"])
    def upload(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(
            data=request.data,
        )
        if serializer.is_valid():
            serializer.validated_data["created_by"] = request.user
            try:
                serializer.validated_data[
                    "template"
                ] = PeriodicDataUpdateImportService.read_periodic_data_update_template_object(
                    serializer.validated_data["file"]
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
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PeriodicDataFieldViewSet(
    ProgramMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_class = PeriodicDataFieldSerializer
    filter_backends = (OrderingFilter,)

    def get_queryset(self) -> QuerySet:
        program = self.get_program()
        return FlexibleAttribute.objects.filter(program=program, type=FlexibleAttribute.PDU)

    @etag_decorator(PeriodicDataFieldKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=PeriodicDataFieldKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
