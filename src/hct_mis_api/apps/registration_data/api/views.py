import logging
from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.api.mixins import (
    BaseViewSet,
    CountActionMixin,
    ProgramMixin,
    SerializerActionMixin,
)
from hct_mis_api.apps.core.utils import check_concurrency_version_in_mutation
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.api.serializers import (
    RegistrationDataImportDetailSerializer,
    RegistrationDataImportListSerializer,
)
from hct_mis_api.apps.registration_data.filters import RegistrationDataImportFilter
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.celery_tasks import (
    deduplication_engine_process,
    fetch_biometric_deduplication_results_and_process,
    merge_registration_data_import_task,
)

logger = logging.getLogger(__name__)


class RegistrationDataImportViewSet(
    ProgramMixin,
    SerializerActionMixin,
    CountActionMixin,
    RetrieveModelMixin,
    ListModelMixin,
    BaseViewSet,
):
    queryset = RegistrationDataImport.objects.all()
    serializer_classes_by_action = {
        "list": RegistrationDataImportListSerializer,
        "retrieve": RegistrationDataImportDetailSerializer,
    }
    permissions_by_action = {
        "list": [
            Permissions.RDI_VIEW_LIST,
        ],
        "retrieve": [
            Permissions.RDI_VIEW_DETAILS,
        ],
        "merge": [Permissions.RDI_MERGE_IMPORT],
        "erase": [Permissions.RDI_REFUSE_IMPORT],
    }
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = RegistrationDataImportFilter

    #
    # @etag_decorator(RDIKeyConstructor)
    # @cache_response(timeout=config.REST_API_TTL, key_func=RDIKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["POST"], url_path="run-deduplication")
    def run_deduplication(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        deduplication_engine_process.delay(str(self.program.id))
        return Response({"message": "Deduplication process started"}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["GET"],
        url_path="webhookdeduplication",
        url_name="webhook-deduplication",
        permission_classes=[AllowAny],
    )
    def webhook_deduplication(
        self, request: Request, business_area_slug: str, program_slug: str, *args: Any, **kwargs: Any
    ) -> Response:
        program = Program.objects.get(business_area__slug=business_area_slug, slug=program_slug)
        fetch_biometric_deduplication_results_and_process.delay(program.deduplication_set_id)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def merge(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        rdi = self.get_object()
        old_rdi = RegistrationDataImport.objects.get(
            id=rdi.id,
        )
        check_concurrency_version_in_mutation(kwargs.get("version"), rdi)

        if not rdi.can_be_merged():
            raise ValidationError(f"Can't merge RDI {rdi} with {rdi.status} status")

        rdi.status = RegistrationDataImport.MERGE_SCHEDULED
        rdi.save()
        merge_registration_data_import_task.delay(registration_data_import_id=rdi.id)
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            rdi.program_id,
            old_rdi,
            rdi,
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Registration Data Import Merge Scheduled"})

    @action(detail=True, methods=["post"])
    def erase(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        rdi = self.get_object()
        old_rdi = RegistrationDataImport.objects.get(
            id=rdi.id,
        )

        if rdi.status not in (
            RegistrationDataImport.IMPORT_ERROR,
            RegistrationDataImport.MERGE_ERROR,
            RegistrationDataImport.DEDUPLICATION_FAILED,
        ):
            msg = "RDI can be erased only when status is: IMPORT_ERROR, MERGE_ERROR, DEDUPLICATION_FAILED"
            logger.warning(msg)
            raise ValidationError(msg)

        Household.all_objects.filter(registration_data_import=rdi).delete()

        rdi.erased = True
        rdi.save()

        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            request.user,
            rdi.program_id,
            old_rdi,
            rdi,
        )
        return Response(status=status.HTTP_200_OK, data={"message": "Registration Data Import Erased"})
