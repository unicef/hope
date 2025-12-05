from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from hope.api.models import Grant
from hope.apps.account.permissions import Permissions
from hope.apps.core.api.mixins import BaseViewSet, PermissionsMixin, ProgramMixin, SerializerActionMixin
from hope.apps.core.api.parsers import DictDrfNestedParser
from hope.apps.generic_import.api.serializers import (
    GenericImportResponseSerializer,
    GenericImportUploadSerializer,
)
from hope.apps.registration_data.models import ImportData, RegistrationDataImport


class GenericImportUploadViewSet(
    PermissionsMixin,
    ProgramMixin,
    SerializerActionMixin,
    BaseViewSet,
):
    """ViewSet for Excel file upload and asynchronous processing via generic import.

    Supports both session-based (cookie) and token-based authentication.
    """

    queryset = ImportData.objects.none()

    permission = Grant.API_GENERIC_IMPORT
    token_permission = Grant.API_GENERIC_IMPORT
    PERMISSIONS = [Permissions.GENERIC_IMPORT_DATA]

    serializer_classes_by_action = {
        "upload": GenericImportUploadSerializer,
    }

    @extend_schema(
        request=GenericImportUploadSerializer,
        responses=GenericImportResponseSerializer,
        summary="Upload Excel file for generic import",
        description=(
            "Upload an Excel file to be processed asynchronously. "
            "Creates ImportData and RDI records, triggers Celery task. "
            "Returns identifiers for status polling."
        ),
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="upload",
        parser_classes=[DictDrfNestedParser],
    )
    @transaction.atomic
    def upload(self, request, *args, **kwargs):
        """Upload Excel file for generic import."""
        from hope.apps.generic_import.celery_tasks import process_generic_import_task

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]

        import_data = ImportData.objects.create(
            status=ImportData.STATUS_PENDING,
            business_area_slug=self.business_area.slug,
            data_type=ImportData.XLSX,
            file=file,
            created_by_id=request.user.id,
        )

        import_name = (
            f"Generic Import API {self.business_area.slug} - "
            f"{self.program.name} - "
            f"{import_data.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        rdi = RegistrationDataImport.objects.create(
            name=import_name,
            status=RegistrationDataImport.IMPORT_SCHEDULED,
            business_area=self.business_area,
            program=self.program,
            imported_by=request.user,
            data_source=RegistrationDataImport.XLS,
            import_data=import_data,
            number_of_individuals=0,
            number_of_households=0,
        )

        transaction.on_commit(
            lambda: process_generic_import_task.delay(
                registration_data_import_id=str(rdi.id),
                import_data_id=str(import_data.id),
            )
        )

        return Response(
            GenericImportResponseSerializer(rdi).data,
            status=status.HTTP_201_CREATED,
        )
