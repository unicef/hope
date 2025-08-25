from typing import Any

from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response

from hope.apps.account.permissions import Permissions
from hope.apps.core.api.mixins import (
    BaseViewSet,
    CountActionMixin,
    SerializerActionMixin,
)
from hope.apps.registration_datahub.validators import XlsxError, XLSXValidator
from hope.apps.sanction_list.api.serializers import (
    CheckAgainstSanctionListCreateSerializer,
    CheckAgainstSanctionListSerializer,
    SanctionListIndividualSerializer,
)
from hope.apps.sanction_list.celery_tasks import check_against_sanction_list_task
from hope.apps.sanction_list.filters import SanctionListIndividualFilter
from hope.models.sanction_list import SanctionListIndividual, UploadedXLSXFile


class SanctionListIndividualViewSet(
    CountActionMixin,
    SerializerActionMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
    XLSXValidator,
):
    queryset = SanctionListIndividual.objects.all()
    serializer_classes_by_action = {
        "list": SanctionListIndividualSerializer,
        "retrieve": SanctionListIndividualSerializer,
        "check_against_sanction_list": CheckAgainstSanctionListCreateSerializer,
    }
    PERMISSIONS = [
        Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
        Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
    ]
    filter_backends = (
        filters.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    filterset_class = SanctionListIndividualFilter
    search_fields = (
        "reference_number",
        "id",
        "full_name",
    )

    @extend_schema(
        request=CheckAgainstSanctionListCreateSerializer,
        responses={202: CheckAgainstSanctionListSerializer},
    )
    @action(detail=False, methods=["post"], url_path="check-against-sanction-list")
    def check_against_sanction_list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]
        user = request.user
        try:
            self.validate(file=file)
        except XlsxError as e:
            return Response(
                CheckAgainstSanctionListSerializer({"ok": False, "errors": e.errors}).data,
                status=status.HTTP_400_BAD_REQUEST,
            )

        uploaded_file = UploadedXLSXFile.objects.create(file=file, associated_email=user.email)

        check_against_sanction_list_task.delay(
            uploaded_file_id=str(uploaded_file.id),
            original_file_name=file.name,
        )
        return Response(
            CheckAgainstSanctionListSerializer({"ok": False, "errors": []}).data,
            status=status.HTTP_202_ACCEPTED,
        )
