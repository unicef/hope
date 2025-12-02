from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from hope.api.auth import HOPEAuthentication, HOPEPermission
from hope.api.models import Grant
from hope.apps.core.api.mixins import BaseViewSet, ProgramMixin, SerializerActionMixin
from hope.apps.core.api.parsers import DictDrfNestedParser
from hope.apps.generic_import.api.serializers import (
    GenericImportResponseSerializer,
    GenericImportUploadSerializer,
)
from hope.apps.registration_data.models import ImportData, RegistrationDataImport


class GenericImportUploadViewSet(
    ProgramMixin,
    SerializerActionMixin,
    BaseViewSet,
):
    """ViewSet dla uploadu plików Excel - generic import.

    Endpoint program-specific dla upload i asynchronicznego przetwarzania.
    Reużywa istniejącej infrastruktury generic_import.
    """

    queryset = ImportData.objects.none()

    # Autoryzacja przez ApiToken
    authentication_classes = [HOPEAuthentication]
    permission_classes = [HOPEPermission]
    permission = Grant.API_GENERIC_IMPORT

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

        # Walidacja
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]

        # Utwórz ImportData
        import_data = ImportData.objects.create(
            status=ImportData.STATUS_PENDING,
            business_area_slug=self.business_area.slug,
            data_type=ImportData.XLSX,
            file=file,
            created_by_id=request.user.id,
        )

        # Utwórz RegistrationDataImport
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

        # Zaplanuj Celery task po commit transakcji
        transaction.on_commit(
            lambda: process_generic_import_task.delay(
                registration_data_import_id=str(rdi.id),
                import_data_id=str(import_data.id),
            )
        )

        # Zwróć response z ID obu obiektów
        return Response(
            GenericImportResponseSerializer(rdi).data,
            status=status.HTTP_201_CREATED,
        )
