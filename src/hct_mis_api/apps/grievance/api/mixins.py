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

            # if can_view_ex_sensitive_all and can_view_sensitive_all:
            #     return Q()
            #
            # filters_1 = {}
            # filters_1_exclude = {}
            # filters_2 = {}
            # filters_2_exclude = {}
            #
            # if can_view_ex_sensitive_all or can_view_sensitive_all:
            #     if can_view_sensitive_creator or can_view_ex_sensitive_creator:
            #         filters_1.update(created_by_filter)
            #     if can_view_sensitive_owner or can_view_ex_sensitive_owner:
            #         filters_2.update(assigned_to_filter)
            #
            #     if can_view_ex_sensitive_all:
            #         return ~Q(**sensitive_category_filter) | Q(**filters_1) | Q(**filters_2)
            #     else:
            #         return Q(**sensitive_category_filter) | Q(**filters_1) | Q(**filters_2)
            #
            # else:
            #     if can_view_ex_sensitive_creator:
            #         filters_1.update(created_by_filter)
            #         if not can_view_sensitive_creator:
            #             filters_1_exclude.update(sensitive_category_filter)
            #     if can_view_ex_sensitive_owner:
            #         filters_2.update(assigned_to_filter)
            #         if not can_view_sensitive_owner:
            #             filters_2_exclude.update(sensitive_category_filter)
            #     if filters_1 or filters_2:
            #         return Q(Q(**filters_1), ~Q(**filters_1_exclude)) | Q(Q(**filters_2), ~Q(**filters_2_exclude))
            #     else:
            #         # return empty queryset if user does not have any permissions
            #         return Q(pk__in=[])

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

            # only_ex_sensitive = programs_can_view_ex_sensitive_all - programs_can_view_sensitive_all
            # if only_ex_sensitive:
            #     filters |= Q(program_id__in=only_ex_sensitive) & ~Q(**sensitive_category_filter)
            #
            # only_sensitive = programs_can_view_sensitive_all - programs_can_view_ex_sensitive_all
            # if only_sensitive:
            #     filters |= Q(program_id__in=only_sensitive, **sensitive_category_filter)
            #
            # all = programs_can_view_ex_sensitive_all & programs_can_view_sensitive_all
            # if all:
            #     filters |= Q(program_id__in=all)
            #
            # ex_sensitive_creator = programs_can_view_ex_sensitive_all & programs_can_view_ex_sensitive_creator
            # if ex_sensitive_creator:
            #     filters |= Q(program_id__in=ex_sensitive_creator) & Q(**created_by_filter) & ~Q(**sensitive_category_filter)
            #
            # ex_sensitive_owner = programs_can_view_ex_sensitive_all & programs_can_view_ex_sensitive_owner
            # if ex_sensitive_owner:
            #     filters |= Q(program_id__in=ex_sensitive_owner) & Q(**assigned_to_filter) & ~Q(**sensitive_category_filter)
            #
            # sensitive_creator = programs_can_view_sensitive_all & programs_can_view_sensitive_creator
            # if sensitive_creator:
            #     filters |= Q(program_id__in=sensitive_creator) & Q(**created_by_filter) & Q(**sensitive_category_filter)
            #
            # sensitive_owner = programs_can_view_sensitive_all & programs_can_view_sensitive_owner
            # if sensitive_owner:
            #     filters |= Q(program_id__in=sensitive_owner) & Q(**assigned_to_filter) & Q(**sensitive_category_filter)
            #
            # creator_ex_sensitive = programs_can_view_ex_sensitive_creator - programs_can_view_sensitive_creator
            # if creator_ex_sensitive:
            #     filters |= Q(program_id__in=creator_ex_sensitive) & Q(**created_by_filter) & ~Q(**sensitive_category_filter)
            #
            # owner_ex_sensitive = programs_can_view_ex_sensitive_owner - programs_can_view_sensitive_owner
            # if owner_ex_sensitive:
            #     filters |= Q(program_id__in=owner_ex_sensitive) & Q(**assigned_to_filter) & ~Q(**sensitive_category_filter)
            #
            # creator_sensitive = programs_can_view_sensitive_creator - programs_can_view_ex_sensitive_creator
            # if creator_sensitive:
            #     filters |= Q(program_id__in=creator_sensitive) & Q(**created_by_filter) & Q(**sensitive_category_filter)
            #
            # owner_sensitive = programs_can_view_sensitive_owner - programs_can_view_ex_sensitive_owner
            # if owner_sensitive:
            #     filters |= Q(program_id__in=owner_sensitive) & Q(**assigned_to_filter) & Q(**sensitive_category_filter)

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
