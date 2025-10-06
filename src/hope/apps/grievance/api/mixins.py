from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from hope.apps.account.models import User
from hope.apps.account.permissions import Permissions
from hope.apps.core.utils import nested_dict_get
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.notifications import GrievanceNotification
from hope.apps.grievance.utils import (
    create_grievance_documents,
    delete_grievance_documents,
    update_grievance_documents,
)
from hope.apps.grievance.validators import validate_grievance_documents_size
from hope.apps.household.models import (
    HEAD,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Household,
    Individual,
    IndividualRoleInHousehold,
)
from hope.apps.utils.exceptions import log_and_raise


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
        filters = Q()
        action = self.action
        if action not in permissions_map:
            return filters

        sensitive_category_filter = {"category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE}
        created_by_filter = {"created_by": self.request.user}
        assigned_to_filter = {"assigned_to": self.request.user}

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
                filters |= (Q(programs__id__in=programs_can_view_ex_sensitive_all) | Q(programs__isnull=True)) & ~Q(
                    **sensitive_category_filter
                )
            if programs_can_view_sensitive_all:
                filters |= (Q(programs__id__in=programs_can_view_sensitive_all) | Q(programs__isnull=True)) & Q(
                    **sensitive_category_filter
                )
            if programs_can_view_ex_sensitive_creator:
                filters |= (
                    (Q(programs__id__in=programs_can_view_ex_sensitive_creator) | Q(programs__isnull=True))
                    & Q(**created_by_filter)
                    & ~Q(**sensitive_category_filter)
                )
            if programs_can_view_ex_sensitive_owner:
                filters |= (
                    (Q(programs__id__in=programs_can_view_ex_sensitive_owner) | Q(programs__isnull=True))
                    & Q(**assigned_to_filter)
                    & ~Q(**sensitive_category_filter)
                )
            if programs_can_view_sensitive_creator:
                filters |= (
                    (Q(programs__id__in=programs_can_view_sensitive_creator) | Q(programs__isnull=True))
                    & Q(**created_by_filter)
                    & Q(**sensitive_category_filter)
                )
            if programs_can_view_sensitive_owner:
                filters |= (
                    (Q(programs__id__in=programs_can_view_sensitive_owner) | Q(programs__isnull=True))
                    & Q(**assigned_to_filter)
                    & Q(**sensitive_category_filter)
                )

        return filters


class GrievanceMutationMixin:
    def verify_required_arguments(self, input_data: dict, field_name: str, options: dict) -> None:
        for key, value in options.items():
            if key != input_data.get(field_name):
                continue
            for required in value.get("required"):
                if nested_dict_get(input_data, required) is None:
                    log_and_raise(f"You have to provide {required} in {key}")
            for not_allowed in value.get("not_allowed"):
                if nested_dict_get(input_data, not_allowed) is not None:
                    log_and_raise(f"You can't provide {not_allowed} in {key}")

    CREATE_CATEGORY_OPTIONS = {
        GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION: {
            "required": [],
            "not_allowed": [
                "extras.category.sensitive_grievance_ticket_extras",
                "extras.category.grievance_complaint_ticket_extras",
            ],
        },
        GrievanceTicket.CATEGORY_DATA_CHANGE: {
            "required": [],
            "not_allowed": [
                "extras.category.sensitive_grievance_ticket_extras",
                "extras.category.grievance_complaint_ticket_extras",
            ],
        },
        GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE: {
            "required": ["issue_type"],
            "not_allowed": ["extras.category.grievance_complaint_ticket_extras"],
        },
        GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT: {
            "required": ["issue_type"],
            "not_allowed": ["extras.category.sensitive_grievance_ticket_extras"],
        },
        GrievanceTicket.CATEGORY_REFERRAL: {
            "required": [],
            "not_allowed": [
                "extras.category.sensitive_grievance_ticket_extras",
                "extras.category.grievance_complaint_ticket_extras",
            ],
        },
        GrievanceTicket.CATEGORY_SYSTEM_FLAGGING: {
            "required": [],
            "not_allowed": [
                "extras.category.sensitive_grievance_ticket_extras",
                "extras.category.grievance_complaint_ticket_extras",
            ],
        },
        GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION: {
            "required": [],
            "not_allowed": [
                "extras.category.sensitive_grievance_ticket_extras",
                "extras.category.grievance_complaint_ticket_extras",
            ],
        },
    }

    CREATE_ISSUE_TYPE_OPTIONS = {
        GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE: {
            "required": ["extras.issue_type.household_data_update_issue_type_extras"],
            "not_allowed": [
                "individual_data_update_issue_type_extras",
                "individual_delete_issue_type_extras",
            ],
        },
        GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD: {
            "required": ["extras.issue_type.household_delete_issue_type_extras"],
            "not_allowed": [
                "household_data_update_issue_type_extras",
                "individual_data_update_issue_type_extras",
            ],
        },
        GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE: {
            "required": ["extras.issue_type.individual_data_update_issue_type_extras"],
            "not_allowed": [
                "household_data_update_issue_type_extras",
                "individual_delete_issue_type_extras",
            ],
        },
        GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL: {
            "required": ["extras.issue_type.add_individual_issue_type_extras"],
            "not_allowed": [
                "household_data_update_issue_type_extras",
                "individual_data_update_issue_type_extras",
                "individual_delete_issue_type_extras",
            ],
        },
        GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL: {
            "required": ["extras.issue_type.individual_delete_issue_type_extras"],
            "not_allowed": [
                "household_data_update_issue_type_extras",
                "individual_data_update_issue_type_extras",
            ],
        },
        GrievanceTicket.ISSUE_TYPE_DATA_BREACH: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_BRIBERY_CORRUPTION_KICKBACK: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_FRAUD_FORGERY: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_FRAUD_MISUSE: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_HARASSMENT: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_INAPPROPRIATE_STAFF_CONDUCT: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_UNAUTHORIZED_USE: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_CONFLICT_OF_INTEREST: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_GROSS_MISMANAGEMENT: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_PERSONAL_DISPUTES: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_SEXUAL_HARASSMENT: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS: {"required": [], "not_allowed": []},
    }

    UPDATE_EXTRAS_OPTIONS = {
        GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE: {
            "required": ["extras.household_data_update_issue_type_extras"],
            "not_allowed": [
                "individual_data_update_issue_type_extras",
                "add_individual_issue_type_extras",
            ],
        },
        GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE: {
            "required": ["extras.individual_data_update_issue_type_extras"],
            "not_allowed": [
                "household_data_update_issue_type_extras",
                "add_individual_issue_type_extras",
            ],
        },
        GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL: {
            "required": ["extras.add_individual_issue_type_extras"],
            "not_allowed": [
                "household_data_update_issue_type_extras",
                "individual_data_update_issue_type_extras",
            ],
        },
        GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_DATA_BREACH: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_BRIBERY_CORRUPTION_KICKBACK: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_FRAUD_FORGERY: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_FRAUD_MISUSE: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_HARASSMENT: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_INAPPROPRIATE_STAFF_CONDUCT: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_UNAUTHORIZED_USE: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_CONFLICT_OF_INTEREST: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_GROSS_MISMANAGEMENT: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_PERSONAL_DISPUTES: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_SEXUAL_HARASSMENT: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS: {"required": [], "not_allowed": []},
    }

    MOVE_TO_STATUS_PERMISSION_MAPPING: dict[int, dict[str | int, list[Permissions]]] = {
        GrievanceTicket.STATUS_ASSIGNED: {
            "any": [
                Permissions.GRIEVANCES_UPDATE,
                Permissions.GRIEVANCES_UPDATE_AS_CREATOR,
                Permissions.GRIEVANCES_UPDATE_AS_OWNER,
            ],
        },
        GrievanceTicket.STATUS_IN_PROGRESS: {
            GrievanceTicket.STATUS_ASSIGNED: [
                Permissions.GRIEVANCES_SET_IN_PROGRESS,
                Permissions.GRIEVANCES_SET_IN_PROGRESS_AS_CREATOR,
                Permissions.GRIEVANCES_SET_IN_PROGRESS_AS_OWNER,
            ],
            GrievanceTicket.STATUS_ON_HOLD: [
                Permissions.GRIEVANCES_SET_IN_PROGRESS,
                Permissions.GRIEVANCES_SET_IN_PROGRESS_AS_CREATOR,
                Permissions.GRIEVANCES_SET_IN_PROGRESS_AS_OWNER,
            ],
            GrievanceTicket.STATUS_FOR_APPROVAL: [
                Permissions.GRIEVANCES_SEND_BACK,
                Permissions.GRIEVANCES_SEND_BACK_AS_CREATOR,
                Permissions.GRIEVANCES_SEND_BACK_AS_OWNER,
            ],
        },
        GrievanceTicket.STATUS_ON_HOLD: {
            "any": [
                Permissions.GRIEVANCES_SET_ON_HOLD,
                Permissions.GRIEVANCES_SET_ON_HOLD_AS_CREATOR,
                Permissions.GRIEVANCES_SET_ON_HOLD_AS_OWNER,
            ]
        },
        GrievanceTicket.STATUS_CLOSED: {
            "feedback": [
                Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK,
                Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_CREATOR,
                Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_OWNER,
            ],
            "any": [
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR,
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER,
            ],
        },
    }

    def update_basic_data(self, approver: User, input_data: dict, grievance_ticket: GrievanceTicket) -> GrievanceTicket:
        messages = []

        if ids_to_delete := input_data.pop("documentation_to_delete", None):
            delete_grievance_documents(grievance_ticket.id, ids_to_delete)

        if documents_to_update := input_data.pop("documentation_to_update", None):
            validate_grievance_documents_size(grievance_ticket.id, documents_to_update, is_updated=True)
            update_grievance_documents(documents_to_update)

        if documents := input_data.pop("documentation", None):
            validate_grievance_documents_size(grievance_ticket.id, documents)
            create_grievance_documents(approver, grievance_ticket, documents)

        priority = input_data.pop("priority", grievance_ticket.priority)
        if priority != grievance_ticket.priority:
            grievance_ticket.priority = priority

        urgency = input_data.pop("urgency", grievance_ticket.urgency)
        if urgency != grievance_ticket.urgency:
            grievance_ticket.urgency = urgency

        if partner := input_data.pop("partner", None):
            grievance_ticket.partner = partner

        if program := input_data.pop("program", None):
            grievance_ticket.programs.add(program)

        assigned_to = input_data.pop("assigned_to", None)

        if admin := input_data.pop("admin", None):
            grievance_ticket.admin2 = admin

        linked_tickets = input_data.pop("linked_tickets", [])
        grievance_ticket.linked_tickets.set(linked_tickets)
        grievance_ticket.user_modified = timezone.now()

        for field, value in input_data.items():
            current_value = getattr(grievance_ticket, field, None)
            if not current_value:
                setattr(grievance_ticket, field, value)

        if assigned_to != grievance_ticket.assigned_to:
            messages.append(GrievanceNotification(grievance_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED))

            if grievance_ticket.status == GrievanceTicket.STATUS_NEW and grievance_ticket.assigned_to is None:
                grievance_ticket.status = GrievanceTicket.STATUS_ASSIGNED

            if grievance_ticket.status == GrievanceTicket.STATUS_ON_HOLD:
                grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS

            if grievance_ticket.status == GrievanceTicket.STATUS_FOR_APPROVAL:
                grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
                messages.append(
                    GrievanceNotification(
                        grievance_ticket,
                        GrievanceNotification.ACTION_SEND_BACK_TO_IN_PROGRESS,
                        approver=approver,
                    )
                )

            grievance_ticket.assigned_to = assigned_to
        elif grievance_ticket.status == GrievanceTicket.STATUS_FOR_APPROVAL:
            grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
            messages.append(
                GrievanceNotification(
                    grievance_ticket,
                    GrievanceNotification.ACTION_SEND_BACK_TO_IN_PROGRESS,
                    approver=approver,
                )
            )

        grievance_ticket.save()
        grievance_ticket.refresh_from_db()

        GrievanceNotification.send_all_notifications(messages)
        return grievance_ticket

    def get_permissions_for_status_change(
        self, status: int, current_status: int, is_feedback: bool
    ) -> list[Permissions]:
        permissions = self.MOVE_TO_STATUS_PERMISSION_MAPPING.get(status, {})
        feedback_permissions = permissions.get("feedback", [])
        any_permissions = permissions.get("any", [])
        based_on_current_status_permissions = permissions.get(current_status, [])

        if is_feedback:
            return feedback_permissions or any_permissions or based_on_current_status_permissions
        return any_permissions or based_on_current_status_permissions

    def verify_role_choices(self, role: str) -> None:
        if role not in (ROLE_PRIMARY, ROLE_ALTERNATE, HEAD):
            log_and_raise("Provided role is invalid! Please provide one of those: PRIMARY, ALTERNATE, HEAD")

    def verify_if_role_exists(self, household: Household, current_individual: Individual, role: str) -> None:
        if role == HEAD:
            if household.head_of_household.id != current_individual.id:
                log_and_raise("This individual is not a head of provided household")
        else:
            get_object_or_404(
                IndividualRoleInHousehold,
                individual=current_individual,
                household=household,
                role=role,
            )
