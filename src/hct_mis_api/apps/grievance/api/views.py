from typing import Any

from django.db.models import Prefetch, QuerySet

from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from hct_mis_api.api.caches import etag_decorator
from hct_mis_api.apps.account.permissions import Permissions, POPULATION_DETAILS
from hct_mis_api.apps.core.api.mixins import (
    BaseViewSet,
    BusinessAreaVisibilityMixin,
    CountActionMixin,
    ProgramVisibilityMixin,
    SerializerActionMixin, GrievanceVisibilityMixin,
)
from hct_mis_api.apps.grievance.api.mixins import GrievancePermissionsMixin
from hct_mis_api.apps.grievance.api.serializers import GrievanceTicketListSerializer
from hct_mis_api.apps.grievance.filters import GrievanceTicketFilter
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.api.caches import (
    HouseholdListKeyConstructor,
    IndividualListKeyConstructor,
)
from hct_mis_api.apps.household.api.serializers.household import (
    HouseholdDetailSerializer,
    HouseholdListSerializer,
    HouseholdMemberSerializer,
)
from hct_mis_api.apps.household.api.serializers.individual import (
    IndividualDetailSerializer,
    IndividualListSerializer,
)
from hct_mis_api.apps.household.filters import HouseholdFilter, IndividualFilter
from hct_mis_api.apps.household.models import (
    Household,
    Individual,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.models import Program


class GrievanceTicketViewSet(
    ProgramVisibilityMixin,
    GrievancePermissionsMixin,
    CountActionMixin,
    ListModelMixin,
    BaseViewSet,
):
    queryset = GrievanceTicket.objects.filter(ignored=False)
    serializer_class = GrievanceTicketListSerializer,
    PERMISSIONS = [
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
    ]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = GrievanceTicketFilter
    admin_area_model_fields = ["admin2"]
    program_model_fields = ["programs"]

    def get_queryset(self) -> QuerySet:
        to_prefetch = []
        for key, value in GrievanceTicket.SEARCH_TICKET_TYPES_LOOKUPS.items():
            to_prefetch.append(key)
            if "household" in value:
                to_prefetch.append(f"{key}__{value['household']}")
            if "golden_records_individual" in value:
                to_prefetch.append(f"{key}__{value['golden_records_individual']}__household")
        return (
            super()
            .get_queryset()
            .filter(self.grievance_permissions_query)
            .select_related("admin2", "assigned_to", "created_by")
            .prefetch_related(*to_prefetch)
            .order_by("created_at")
        )

    @etag_decorator(GrievanceTicketListKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=GrievanceTicketListKeyConstructor())
    def list(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        return super().list(request, *args, **kwargs)


class GrievanceTicketGlobalViewSet(
    BusinessAreaVisibilityMixin,
    GrievancePermissionsMixin,
    SerializerActionMixin,
    CountActionMixin,
    ListModelMixin,
    RetrieveModelMixin,
    BaseViewSet,
):
    queryset = GrievanceTicket.objects.all()
    serializer_classes_by_action = {
        "list": GrievanceTicketListSerializer,
        "retrieve": GrievanceTicketDetailSerializer,
    }
    permissions_by_action = {
        "list":
            [
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
                *POPULATION_DETAILS,
            ],
        "retrieve":
            [
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
            ],
    }
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = GrievanceTicketFilter
    admin_area_model_fields = ["admin2"]
    program_model_fields = ["programs"]

    def get_queryset(self) -> QuerySet:
        to_prefetch = []
        for key, value in GrievanceTicket.SEARCH_TICKET_TYPES_LOOKUPS.items():
            to_prefetch.append(key)
            if "household" in value:
                to_prefetch.append(f"{key}__{value['household']}")
            if "golden_records_individual" in value:
                to_prefetch.append(f"{key}__{value['golden_records_individual']}__household")
        return (
            super()
            .get_queryset()
            .filter(self.grievance_permissions_query)
            .select_related("admin2", "assigned_to", "created_by")
            .prefetch_related(*to_prefetch)
            .order_by("created_at")
        )
