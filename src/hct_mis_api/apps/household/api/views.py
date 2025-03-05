from typing import Any

from django.db.models import QuerySet

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response

from hct_mis_api.apps.account.permissions import (
    ALL_GRIEVANCES_CREATE_MODIFY,
    Permissions,
)
from hct_mis_api.apps.core.api.mixins import (
    BaseViewSet,
    BusinessAreaVisibilityMixin,
    CountActionMixin,
    DecodeIdForDetailMixin,
    ProgramVisibilityMixin,
    SerializerActionMixin,
)
from hct_mis_api.apps.household.api.serializers.household import (
    HouseholdDetailSerializer,
    HouseholdListSerializer,
)
from hct_mis_api.apps.household.filters import HouseholdFilter
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.program.models import Program


class HouseholdViewSet(
    CountActionMixin,
    ProgramVisibilityMixin,
    SerializerActionMixin,
    DecodeIdForDetailMixin,
    RetrieveModelMixin,
    ListModelMixin,
    BaseViewSet,
):
    queryset = Household.all_merge_status_objects.all()
    serializer_class = HouseholdListSerializer
    serializer_classes_by_action = {
        "list": HouseholdListSerializer,
        "retrieve": HouseholdDetailSerializer,
    }
    permissions_by_action = {
        "list": [
            Permissions.RDI_VIEW_DETAILS,
            Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
            *ALL_GRIEVANCES_CREATE_MODIFY,
        ],
        "retrieve": [
            Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
            Permissions.RDI_VIEW_DETAILS,
            Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS,
            Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER,
        ],
    }
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = HouseholdFilter
    admin_area_model_fields = ["admin1", "admin2", "admin3"]

    def get_queryset(self) -> QuerySet:
        if self.program.status == Program.DRAFT:
            return Household.objects.none()

        return super().get_queryset().select_related("head_of_household", "program", "admin1", "admin2")

    @action(
        detail=True,
        methods=["post"],
    )
    def withdraw(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        instance = self.get_object()
        instance.withdraw()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HouseholdGlobalViewSet(
    BusinessAreaVisibilityMixin,
    ListModelMixin,
    BaseViewSet,
):
    queryset = Household.all_merge_status_objects.all()
    serializer_class = HouseholdListSerializer
    PERMISSIONS = [
        Permissions.RDI_VIEW_DETAILS,
        Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
        *ALL_GRIEVANCES_CREATE_MODIFY,
    ]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = HouseholdFilter
    admin_area_model_fields = ["admin1", "admin2", "admin3"]

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().select_related("head_of_household", "program", "admin1", "admin2")
