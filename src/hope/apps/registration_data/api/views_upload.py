from hope.apps.core.api.mixins import BaseViewSet, ProgramMixin, SerializerActionMixin
from hope.apps.account.permissions import Permissions
from hope.apps.core.api.parsers import DictDrfNestedParser
from hope.apps.registration_data.models import ImportData, KoboImportData
from hope.apps.registration_data.api.serializers import (
    ImportDataSerializer,
    KoboImportDataSerializer,
    UploadXlsxFileSerializer,
    SaveKoboImportDataSerializer,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from drf_spectacular.utils import extend_schema


class ImportDataUploadViewSet(
    ProgramMixin,
    SerializerActionMixin,
    BaseViewSet,
):
    """ViewSet for uploading XLSX files for import data.

    Program-specific endpoints for file upload and processing.
    """

    queryset = ImportData.objects.none()  # No list/retrieve needed
    serializer_classes_by_action = {
        "upload_xlsx_file": UploadXlsxFileSerializer,
    }
    permissions_by_action = {
        "upload_xlsx_file": [Permissions.RDI_IMPORT_DATA],
    }

    @extend_schema(
        request=UploadXlsxFileSerializer,
        responses=ImportDataSerializer,
    )
    @action(detail=False, methods=["post"], url_path="upload-xlsx-file", parser_classes=[DictDrfNestedParser])
    @transaction.atomic
    def upload_xlsx_file(self, request, *args, **kwargs):
        """Upload an XLSX file asynchronously for registration data import."""
        from hope.apps.registration_datahub.celery_tasks import validate_xlsx_import_task

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]

        import_data = ImportData.objects.create(
            file=file,
            data_type=ImportData.XLSX,
            status=ImportData.STATUS_PENDING,
            created_by_id=request.user.id,
            business_area_slug=self.business_area.slug,
        )

        transaction.on_commit(lambda: validate_xlsx_import_task.delay(import_data.id, str(self.program.id)))

        return Response(
            ImportDataSerializer(import_data, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )


class KoboImportDataUploadViewSet(
    ProgramMixin,
    SerializerActionMixin,
    BaseViewSet,
):
    """ViewSet for saving KoBo import data.

    Program-specific endpoints for KoBo data processing.
    """

    queryset = KoboImportData.objects.none()  # No list/retrieve needed
    serializer_classes_by_action = {
        "save_kobo_import_data": SaveKoboImportDataSerializer,
    }
    permissions_by_action = {
        "save_kobo_import_data": [Permissions.RDI_IMPORT_DATA],
    }

    @extend_schema(
        request=SaveKoboImportDataSerializer,
        responses=KoboImportDataSerializer,
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="save-kobo-import-data",
    )
    @transaction.atomic
    def save_kobo_import_data(self, request, *args, **kwargs):
        """Save KoBo project import data asynchronously."""
        from hope.apps.registration_datahub.celery_tasks import pull_kobo_submissions_task

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        uid = validated_data["uid"]
        only_active_submissions = validated_data["only_active_submissions"]
        pull_pictures = validated_data["pull_pictures"]

        import_data = KoboImportData.objects.create(
            data_type=ImportData.JSON,
            kobo_asset_id=uid,
            only_active_submissions=only_active_submissions,
            status=ImportData.STATUS_PENDING,
            business_area_slug=self.business_area.slug,
            created_by_id=request.user.id,
            pull_pictures=pull_pictures,
        )

        pull_kobo_submissions_task.delay(import_data.id, str(self.program.id))

        return Response(
            KoboImportDataSerializer(import_data, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )
