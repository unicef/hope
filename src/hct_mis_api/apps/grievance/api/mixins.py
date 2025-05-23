from django.db.models import Q

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.grievance.models import GrievanceTicket


class GrievancePermissionsMixin:
    @property
    def grievance_permissions_query(self) -> Q:
        user = self.request.user
        permissions_map = {
            "list": [
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
            ],
            "retrieve": [
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
            ],
            "count": [
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
            ],
            "partial_update": [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,],
        }
        action = self.action
        sensitive_category_filter = {"category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE}
        created_by_filter = {"created_by": self.request.user}
        assigned_to_filter = {"assigned_to": self.request.user}

        filters = Q()

        # program-nested viewset
        if hasattr(self, "program"):
            permissions_in_program = user.permissions_in_business_area(self.business_area_slug, self.program.id)

            can_view_ex_sensitive_all = permissions_map[action][0].value in permissions_in_program
            can_view_ex_sensitive_creator = permissions_map[action][1].value in permissions_in_program
            can_view_ex_sensitive_owner = permissions_map[action][2].value in permissions_in_program
            can_view_sensitive_all = permissions_map[action][3].value in permissions_in_program
            can_view_sensitive_creator = permissions_map[action][4].value in permissions_in_program
            can_view_sensitive_owner = permissions_map[action][5].value in permissions_in_program

            if can_view_ex_sensitive_all:
                filters |= ~Q(**sensitive_category_filter)
            if can_view_sensitive_all:
                filters |= Q(**sensitive_category_filter)
            if can_view_ex_sensitive_creator:
                filters |= Q(**created_by_filter) & ~Q(**sensitive_category_filter)
            if can_view_ex_sensitive_owner:
                filters |= Q(**assigned_to_filter) & ~Q(**sensitive_category_filter)
            if can_view_sensitive_creator:
                filters |= Q(**created_by_filter) & Q(**sensitive_category_filter)
            if can_view_sensitive_owner:
                filters |= Q(**assigned_to_filter) & Q(**sensitive_category_filter)

        # global viewset
        else:
            programs_can_view_ex_sensitive_all = set(
                user.get_program_ids_for_permissions_in_business_area(
                    self.business_area.id, [permissions_map[action][0]]
                )
            )
            programs_can_view_ex_sensitive_creator = set(
                user.get_program_ids_for_permissions_in_business_area(
                    self.business_area.id, [permissions_map[action][1]]
                )
            )
            programs_can_view_ex_sensitive_owner = set(
                user.get_program_ids_for_permissions_in_business_area(
                    self.business_area.id, [permissions_map[action][2]]
                )
            )
            programs_can_view_sensitive_all = set(
                user.get_program_ids_for_permissions_in_business_area(
                    self.business_area.id, [permissions_map[action][3]]
                )
            )
            programs_can_view_sensitive_creator = set(
                user.get_program_ids_for_permissions_in_business_area(
                    self.business_area.id, [permissions_map[action][4]]
                )
            )
            programs_can_view_sensitive_owner = set(
                user.get_program_ids_for_permissions_in_business_area(
                    self.business_area.id, [permissions_map[action][5]]
                )
            )

            if programs_can_view_ex_sensitive_all:
                filters |= Q(programs__id__in=programs_can_view_ex_sensitive_all) & ~Q(**sensitive_category_filter)
            if programs_can_view_sensitive_all:
                filters |= Q(programs__id__in=programs_can_view_sensitive_all, **sensitive_category_filter)
            if programs_can_view_ex_sensitive_creator:
                filters |= (
                    Q(programs__id__in=programs_can_view_ex_sensitive_creator)
                    & Q(**created_by_filter)
                    & ~Q(**sensitive_category_filter)
                )
            if programs_can_view_ex_sensitive_owner:
                filters |= (
                    Q(programs__id__in=programs_can_view_ex_sensitive_owner)
                    & Q(**assigned_to_filter)
                    & ~Q(**sensitive_category_filter)
                )
            if programs_can_view_sensitive_creator:
                filters |= (
                    Q(programs__id__in=programs_can_view_sensitive_creator)
                    & Q(**created_by_filter)
                    & Q(**sensitive_category_filter)
                )
            if programs_can_view_sensitive_owner:
                filters |= (
                    Q(programs__id__in=programs_can_view_sensitive_owner)
                    & Q(**assigned_to_filter)
                    & Q(**sensitive_category_filter)
                )

        return filters
