import logging
from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt

from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_extensions.cache.decorators import cache_response

from hct_mis_api.api.caches import etag_decorator
from hct_mis_api.apps.account.api.permissions import RDIViewListPermission
from hct_mis_api.apps.core.api.mixins import BusinessAreaProgramMixin
from hct_mis_api.apps.payment.celery_tasks import (
    fetch_biometric_deduplication_results_and_process,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.api.caches import RDIKeyConstructor
from hct_mis_api.apps.registration_data.api.filters import RegistrationDataImportFilter
from hct_mis_api.apps.registration_data.api.serializers import (
    DeduplicationEngineStatusSerializer,
    RegistrationDataImportListSerializer,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.celery_tasks import (
    deduplication_engine_process,
)
from hct_mis_api.apps.registration_datahub.services.biometric_deduplication import (
    BiometricDeduplicationService,
)

logger = logging.getLogger(__name__)


class RegistrationDataImportViewSet(
    BusinessAreaProgramMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_class = RegistrationDataImportListSerializer
    permission_classes = [RDIViewListPermission]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = RegistrationDataImportFilter

    def get_queryset(self) -> QuerySet:
        business_area = self.get_business_area()
        program = self.get_program()
        return RegistrationDataImport.objects.filter(business_area=business_area, program=program)

    @etag_decorator(RDIKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=RDIKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["POST"], url_path="run-deduplication")
    def run_deduplication(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        program = self.get_program()
        deduplication_engine_process.delay(program.id)
        return Response({"message": "Deduplication process started"}, status=status.HTTP_200_OK)


class WebhookDeduplicationView(APIView):
    serializer_class = DeduplicationEngineStatusSerializer

    @csrf_exempt
    def post(self, request: HttpRequest, program_id: str) -> Response:
        serializer = self.serializer_class(data=request.data)
        program = Program.objects.get(id=program_id)

        if serializer.is_valid():
            if serializer.validated_data["state"] == "CLEAN":
                fetch_biometric_deduplication_results_and_process.delay(program.deduplication_set_id)
            else:
                service = BiometricDeduplicationService()
                service.mark_rdis_as_deduplication_error(program.deduplication_set_id)
                logger.error(
                    f"Failed to process deduplication set {program.deduplication_set_id} {serializer.validated_data}"
                )

            return Response(status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
