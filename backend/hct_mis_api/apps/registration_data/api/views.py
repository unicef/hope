import logging
from typing import Any

from django.db.models import QuerySet

from constance import config
from rest_framework import mixins
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_extensions.cache.decorators import cache_response

from hct_mis_api.api.caches import etag_decorator
from hct_mis_api.apps.account.api.permissions import RDIViewListPermission
from hct_mis_api.apps.core.api.mixins import BusinessAreaProgramMixin
from hct_mis_api.apps.registration_data.api.caches import RDIKeyConstructor
from hct_mis_api.apps.registration_data.api.serializers import (
    RegistrationDataImportListSerializer,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport

logger = logging.getLogger(__name__)


class RegistrationDataImportViewSet(
    BusinessAreaProgramMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_class = RegistrationDataImportListSerializer
    permission_classes = [RDIViewListPermission]
    filter_backends = (OrderingFilter,)

    def get_queryset(self) -> QuerySet:
        business_area = self.get_business_area()
        program = self.get_program()
        return RegistrationDataImport.objects.filter(business_area=business_area, program=program)

    @etag_decorator(RDIKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=RDIKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)
