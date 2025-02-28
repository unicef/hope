from typing import Any

from django.db.models import Q, QuerySet

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from hct_mis_api.apps.account.api.permissions import HasOneOfPermissions
from hct_mis_api.apps.account.permissions import (
    ALL_GRIEVANCES_CREATE_MODIFY,
    Permissions,
)
from hct_mis_api.apps.core.api.mixins import (
    ActionMixin,
    BaseViewSet,
    BusinessAreaMixin,
    BusinessAreaProgramMixin,
    DecodeIdForDetailMixin,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.api.mixins import CreatorOrOwnerPermissionMixin
from hct_mis_api.apps.household.api.serializers.household import (
    HouseholdDetailSerializer,
    HouseholdListSerializer,
)
from hct_mis_api.apps.household.filters import HouseholdFilter
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.program.models import Program


class HouseholdViewSet(
    BusinessAreaProgramMixin,
    ActionMixin,
    DecodeIdForDetailMixin,
    CreatorOrOwnerPermissionMixin,
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
    PERMISSIONS = [
        Permissions.RDI_VIEW_DETAILS,
        Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
        *ALL_GRIEVANCES_CREATE_MODIFY,
    ]
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

    def get_queryset(self) -> QuerySet:
        program = self.get_program()
        if program.status == Program.DRAFT:
            return Household.objects.none()

        # apply admin area limits if partner has restrictions
        filter_q = Q()
        area_limits = self.request.user.partner.get_area_limits_for_program(program.id)
        if area_limits.exists():
            areas_null = Q(admin_area__isnull=True)
            areas_query = Q(Q(admin1__in=area_limits) | Q(admin2__in=area_limits) | Q(admin3__in=area_limits))
            filter_q = Q(areas_null | Q(areas_query))
        return (
            super().get_queryset().filter(filter_q).select_related("head_of_household", "program", "admin1", "admin2")
        )

    def check_object_permissions(self, request: Any, obj: Household) -> None:
        super().check_object_permissions(request, obj)
        user = request.user
        if obj.admin_area_id:
            # check if user has access to the area
            area_limits = user.partner.get_area_limits_for_program(obj.program_id)
            if area_limits.exists():
                areas_from_household = [
                    obj.admin1_id,
                    obj.admin2_id,
                    obj.admin3_id,
                ]
                if not area_limits.filter(id__in=areas_from_household).exists():
                    raise PermissionDenied()

        # if user doesn't have permission to view all households or RDI details, we check based on their grievance tickets
        if not user.has_perm(
            Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS.value,
            obj.program or obj.business_area,
        ) and not user.has_perm(
            Permissions.RDI_VIEW_DETAILS.value,
            obj.program or obj.business_area,
        ):
            grievance_tickets = GrievanceTicket.objects.filter(
                complaint_ticket_details__in=obj.complaint_ticket_details.all()
            )

            self.check_creator_or_owner_permission(
                user,
                self.get_program() or obj.business_area,
                Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS.value,
                any(user_ticket in user.created_tickets.all() for user_ticket in grievance_tickets),
                Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR.value,
                any(user_ticket in user.assigned_tickets.all() for user_ticket in grievance_tickets),
                Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER.value,
            )


class HouseholdGlobalViewSet(
    BusinessAreaMixin,
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

    def get_queryset(self) -> QuerySet:
        business_area = self.get_business_area()
        business_area_id = business_area.id
        user = self.request.user

        programs_for_business_area = user.get_program_ids_for_permission_in_business_area(
            business_area_id,
            self.PERMISSIONS,
            one_of_permissions=True,
        )

        filter_q = Q()
        for program_id in (
            Program.objects.filter(id__in=programs_for_business_area)
            .exclude(status=Program.DRAFT)
            .values_list("id", flat=True)
        ):
            program_q = Q(program_id=program_id)
            areas_null_and_program_q = program_q & Q(admin_area__isnull=True)
            # apply admin area limits if partner has restrictions
            area_limits = user.partner.get_area_limits_for_program(program_id)
            areas_query = (
                Q(Q(admin1__in=area_limits) | Q(admin2__in=area_limits) | Q(admin3__in=area_limits))
                if area_limits.exists()
                else Q()
            )

            filter_q |= Q(areas_null_and_program_q | Q(program_q & areas_query))

        queryset = super().get_queryset().filter(filter_q)
        return queryset
