import logging

import graphene
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from graphql import GraphQLError

from hct_mis_api.apps.account.permissions import PermissionMutation, Permissions
from hct_mis_api.apps.account.schema import UserNode
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea, AdminArea
from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.core.scalars import BigInt
from hct_mis_api.apps.core.schema import BusinessAreaNode
from hct_mis_api.apps.core.utils import decode_id_string, to_snake_case, check_concurrency_version_in_mutation
from hct_mis_api.apps.grievance.models import GrievanceTicket, TicketNote
from hct_mis_api.apps.grievance.mutations_extras.data_change import (
    save_data_change_extras,
    close_add_individual_grievance_ticket,
    close_update_individual_grievance_ticket,
    close_update_household_grievance_ticket,
    close_delete_individual_ticket,
    update_data_change_extras,
)
from hct_mis_api.apps.grievance.mutations_extras.grievance_complaint import save_grievance_complaint_extras
from hct_mis_api.apps.grievance.mutations_extras.main import (
    CreateGrievanceTicketExtrasInput,
    UpdateGrievanceTicketExtrasInput,
    _no_operation_close_method,
)
from hct_mis_api.apps.grievance.mutations_extras.payment_verification import save_payment_verification_extras
from hct_mis_api.apps.grievance.mutations_extras.sensitive_grievance import save_sensitive_grievance_extras
from hct_mis_api.apps.grievance.mutations_extras.system_tickets import (
    close_needs_adjudication_ticket,
    close_system_flagging_ticket,
)
from hct_mis_api.apps.grievance.mutations_extras.utils import verify_required_arguments, remove_parsed_data_fields
from hct_mis_api.apps.grievance.schema import GrievanceTicketNode, TicketNoteNode
from hct_mis_api.apps.grievance.validators import DataChangeValidator
from hct_mis_api.apps.household.models import (
    Household,
    Individual,
    HEAD,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.household.schema import HouseholdNode, IndividualNode

logger = logging.getLogger(__name__)


class CreateGrievanceTicketInput(graphene.InputObjectType):
    description = graphene.String(required=True)
    assigned_to = graphene.GlobalID(node=UserNode, required=True)
    category = graphene.Int(required=True)
    issue_type = graphene.Int()
    admin = graphene.String()
    area = graphene.String()
    language = graphene.String(required=True)
    consent = graphene.Boolean(required=True)
    business_area = graphene.GlobalID(node=BusinessAreaNode, required=True)
    linked_tickets = graphene.List(graphene.ID)
    extras = CreateGrievanceTicketExtrasInput()


class UpdateGrievanceTicketInput(graphene.InputObjectType):
    ticket_id = graphene.GlobalID(node=GrievanceTicketNode, required=True)
    description = graphene.String()
    assigned_to = graphene.GlobalID(node=UserNode, required=False)
    admin = graphene.String()
    area = graphene.String()
    language = graphene.String()
    linked_tickets = graphene.List(graphene.ID)
    extras = UpdateGrievanceTicketExtrasInput()


class CreateTicketNoteInput(graphene.InputObjectType):
    description = graphene.String(required=True)
    ticket = graphene.GlobalID(node=GrievanceTicketNode, required=True)


class CreateGrievanceTicketMutation(PermissionMutation):
    grievance_tickets = graphene.List(GrievanceTicketNode)

    CATEGORY_OPTIONS = {
        GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK: {
            "required": [],
            "not_allowed": [
                "extras.category.sensitive_grievance_ticket_extras",
                "extras.category.grievance_complaint_ticket_extras",
            ],
        },
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
            "required": [],
            "not_allowed": ["extras.category.sensitive_grievance_ticket_extras"],
        },
        GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK: {
            "required": [],
            "not_allowed": [
                "extras.category.sensitive_grievance_ticket_extras",
                "extras.category.grievance_complaint_ticket_extras",
            ],
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

    ISSUE_TYPE_OPTIONS = {
        GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE: {
            "required": ["extras.issue_type.household_data_update_issue_type_extras"],
            "not_allowed": [
                "individual_data_update_issue_type_extras",
                "individual_delete_issue_type_extras",
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
        GrievanceTicket.ISSUE_TYPE_BRIBERY_CORRUPTION_KICKBACK: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_FRAUD_FORGERY: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_FRAUD_MISUSE: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_HARASSMENT: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_INAPPROPRIATE_STAFF_CONDUCT: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_UNAUTHORIZED_USE: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_CONFLICT_OF_INTEREST: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_GROSS_MISMANAGEMENT: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_PERSONAL_DISPUTES: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_SEXUAL_HARASSMENT: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS: {"required": [], "not_allowed": []},
    }

    class Arguments:
        input = CreateGrievanceTicketInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input, **kwargs):
        arg = lambda name, default=None: input.get(name, default)
        cls.has_permission(info, Permissions.GRIEVANCES_CREATE, arg("business_area"))

        verify_required_arguments(input, "category", cls.CATEGORY_OPTIONS)
        if arg("issue_type"):
            verify_required_arguments(input, "issue_type", cls.ISSUE_TYPE_OPTIONS)
        category = arg("category")
        grievance_ticket, extras = cls.save_basic_data(root, info, input, **kwargs)
        save_extra_methods = {
            GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION: save_payment_verification_extras,
            GrievanceTicket.CATEGORY_DATA_CHANGE: save_data_change_extras,
            GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT: save_grievance_complaint_extras,
            GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE: save_sensitive_grievance_extras,
        }
        save_extra_method = save_extra_methods.get(category)
        grievances = [grievance_ticket]
        if save_extra_method:
            grievances = save_extra_method(root, info, input, grievance_ticket, extras, **kwargs)
        for grievance in grievances:
            log_create(GrievanceTicket.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, None, grievance)
        return cls(grievance_tickets=grievances)

    @classmethod
    def save_basic_data(cls, root, info, input, **kwargs):
        arg = lambda name, default=None: input.get(name, default)
        user = info.context.user
        assigned_to_id = decode_id_string(arg("assigned_to"))
        linked_tickets_encoded_ids = arg("linked_tickets", [])
        linked_tickets = [decode_id_string(encoded_id) for encoded_id in linked_tickets_encoded_ids]
        business_area_slug = arg("business_area")
        extras = arg("extras", {})
        remove_parsed_data_fields(input, ("linked_tickets", "extras", "business_area", "assigned_to"))
        admin = input.pop("admin", None)
        admin_object = None
        if admin:
            admin_object = get_object_or_404(AdminArea, p_code=admin)
        business_area = get_object_or_404(BusinessArea, slug=business_area_slug)
        assigned_to = get_object_or_404(get_user_model(), id=assigned_to_id)
        grievance_ticket = GrievanceTicket.objects.create(
            **input,
            admin2=admin_object,
            business_area=business_area,
            created_by=user,
            user_modified=timezone.now(),
            assigned_to=assigned_to,
            status=GrievanceTicket.STATUS_ASSIGNED,
        )
        grievance_ticket.linked_tickets.set(linked_tickets)
        return grievance_ticket, extras


class UpdateGrievanceTicketMutation(PermissionMutation):
    grievance_ticket = graphene.Field(GrievanceTicketNode)

    EXTRAS_OPTIONS = {
        GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE: {
            "required": ["extras.household_data_update_issue_type_extras"],
            "not_allowed": ["individual_data_update_issue_type_extras", "add_individual_issue_type_extras"],
        },
        GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE: {
            "required": ["extras.individual_data_update_issue_type_extras"],
            "not_allowed": ["household_data_update_issue_type_extras", "add_individual_issue_type_extras"],
        },
        GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL: {
            "required": ["extras.add_individual_issue_type_extras"],
            "not_allowed": ["household_data_update_issue_type_extras", "individual_data_update_issue_type_extras"],
        },
        GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_DATA_BREACH: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_BRIBERY_CORRUPTION_KICKBACK: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_FRAUD_FORGERY: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_FRAUD_MISUSE: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_HARASSMENT: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_INAPPROPRIATE_STAFF_CONDUCT: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_UNAUTHORIZED_USE: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_CONFLICT_OF_INTEREST: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_GROSS_MISMANAGEMENT: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_PERSONAL_DISPUTES: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_SEXUAL_HARASSMENT: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS: {"required": [], "not_allowed": []},
    }

    class Arguments:
        input = UpdateGrievanceTicketInput(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input, **kwargs):
        arg = lambda name, default=None: input.get(name, default)
        old_grievance_ticket = get_object_or_404(GrievanceTicket, id=decode_id_string(arg("ticket_id")))
        grievance_ticket = get_object_or_404(GrievanceTicket, id=decode_id_string(arg("ticket_id")))
        check_concurrency_version_in_mutation(kwargs.get("version"), grievance_ticket)
        business_area = grievance_ticket.business_area
        cls.has_creator_or_owner_permission(
            info,
            business_area,
            Permissions.GRIEVANCES_UPDATE,
            grievance_ticket.created_by == info.context.user,
            Permissions.GRIEVANCES_UPDATE_AS_CREATOR,
            grievance_ticket.assigned_to == info.context.user,
            Permissions.GRIEVANCES_UPDATE_AS_OWNER,
        )

        if grievance_ticket.status == GrievanceTicket.STATUS_CLOSED:
            logger.error("Grievance Ticket on status Closed is not editable")
            raise GraphQLError("Grievance Ticket on status Closed is not editable")

        if grievance_ticket.issue_type:
            verify_required_arguments(input, "issue_type", cls.EXTRAS_OPTIONS)
        grievance_ticket, extras = cls.update_basic_data(root, info, input, grievance_ticket, **kwargs)

        if cls.has_creator_or_owner_permission(
            info,
            business_area,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE,
            grievance_ticket.created_by == info.context.user,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR,
            grievance_ticket.assigned_to == info.context.user,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER,
            False,
        ):
            update_extra_methods = {
                GrievanceTicket.CATEGORY_DATA_CHANGE: update_data_change_extras,
            }
            category = grievance_ticket.category
            update_extra_method = update_extra_methods.get(category)
            if update_extra_method:
                grievance_ticket = update_extra_method(root, info, input, grievance_ticket, extras, **kwargs)
        log_create(
            GrievanceTicket.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_grievance_ticket,
            grievance_ticket,
        )
        return cls(grievance_ticket=grievance_ticket)

    @classmethod
    def update_basic_data(cls, root, info, input, grievance_ticket, **kwargs):
        arg = lambda name, default=None: input.get(name, default)
        assigned_to_id = decode_id_string(arg("assigned_to"))
        linked_tickets_encoded_ids = arg("linked_tickets", [])
        linked_tickets = [decode_id_string(encoded_id) for encoded_id in linked_tickets_encoded_ids]
        extras = arg("extras", {})
        remove_parsed_data_fields(input, ("linked_tickets", "extras", "assigned_to"))
        assigned_to = get_object_or_404(get_user_model(), id=assigned_to_id)
        for field, value in input.items():
            current_value = getattr(grievance_ticket, field, None)
            if not current_value:
                setattr(grievance_ticket, field, value)

        if assigned_to != grievance_ticket.assigned_to:
            if grievance_ticket.status == GrievanceTicket.STATUS_NEW and grievance_ticket.assigned_to is None:
                grievance_ticket.status = GrievanceTicket.STATUS_ASSIGNED
            grievance_ticket.assigned_to = assigned_to
            if grievance_ticket.status in (GrievanceTicket.STATUS_ON_HOLD, GrievanceTicket.STATUS_FOR_APPROVAL):
                grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        else:
            if grievance_ticket.status == GrievanceTicket.STATUS_FOR_APPROVAL:
                grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS

        admin = input.pop("admin", None)
        if admin:
            grievance_ticket.admin2 = get_object_or_404(AdminArea, p_code=admin)
        grievance_ticket.user_modified = timezone.now()
        grievance_ticket.save()

        grievance_ticket.linked_tickets.set(linked_tickets)
        grievance_ticket.refresh_from_db()
        return grievance_ticket, extras


POSSIBLE_STATUS_FLOW = {
    GrievanceTicket.STATUS_NEW: (GrievanceTicket.STATUS_ASSIGNED,),
    GrievanceTicket.STATUS_ASSIGNED: (GrievanceTicket.STATUS_IN_PROGRESS,),
    GrievanceTicket.STATUS_IN_PROGRESS: (GrievanceTicket.STATUS_ON_HOLD, GrievanceTicket.STATUS_FOR_APPROVAL),
    GrievanceTicket.STATUS_ON_HOLD: (GrievanceTicket.STATUS_IN_PROGRESS, GrievanceTicket.STATUS_FOR_APPROVAL),
    GrievanceTicket.STATUS_FOR_APPROVAL: (GrievanceTicket.STATUS_IN_PROGRESS, GrievanceTicket.STATUS_CLOSED),
    GrievanceTicket.STATUS_CLOSED: (),
}
POSSIBLE_FEEDBACK_STATUS_FLOW = {
    GrievanceTicket.STATUS_NEW: (GrievanceTicket.STATUS_ASSIGNED,),
    GrievanceTicket.STATUS_ASSIGNED: (GrievanceTicket.STATUS_IN_PROGRESS,),
    GrievanceTicket.STATUS_IN_PROGRESS: (
        GrievanceTicket.STATUS_ON_HOLD,
        GrievanceTicket.STATUS_FOR_APPROVAL,
        GrievanceTicket.STATUS_CLOSED,
    ),
    GrievanceTicket.STATUS_ON_HOLD: (
        GrievanceTicket.STATUS_IN_PROGRESS,
        GrievanceTicket.STATUS_FOR_APPROVAL,
        GrievanceTicket.STATUS_CLOSED,
    ),
    GrievanceTicket.STATUS_FOR_APPROVAL: (GrievanceTicket.STATUS_IN_PROGRESS, GrievanceTicket.STATUS_CLOSED),
    GrievanceTicket.STATUS_CLOSED: (),
}


class GrievanceStatusChangeMutation(PermissionMutation):
    grievance_ticket = graphene.Field(GrievanceTicketNode)

    CATEGORY_ISSUE_TYPE_TO_CLOSE_FUNCTION_MAPPING = {
        GrievanceTicket.CATEGORY_DATA_CHANGE: {
            GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE: close_update_household_grievance_ticket,
            GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE: close_update_individual_grievance_ticket,
            GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL: close_add_individual_grievance_ticket,
            GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL: close_delete_individual_ticket,
        },
        GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE: {
            GrievanceTicket.ISSUE_TYPE_DATA_BREACH: _no_operation_close_method,
            GrievanceTicket.ISSUE_TYPE_BRIBERY_CORRUPTION_KICKBACK: _no_operation_close_method,
            GrievanceTicket.ISSUE_TYPE_FRAUD_FORGERY: _no_operation_close_method,
            GrievanceTicket.ISSUE_TYPE_FRAUD_MISUSE: _no_operation_close_method,
            GrievanceTicket.ISSUE_TYPE_HARASSMENT: _no_operation_close_method,
            GrievanceTicket.ISSUE_TYPE_INAPPROPRIATE_STAFF_CONDUCT: _no_operation_close_method,
            GrievanceTicket.ISSUE_TYPE_UNAUTHORIZED_USE: _no_operation_close_method,
            GrievanceTicket.ISSUE_TYPE_CONFLICT_OF_INTEREST: _no_operation_close_method,
            GrievanceTicket.ISSUE_TYPE_GROSS_MISMANAGEMENT: _no_operation_close_method,
            GrievanceTicket.ISSUE_TYPE_PERSONAL_DISPUTES: _no_operation_close_method,
            GrievanceTicket.ISSUE_TYPE_SEXUAL_HARASSMENT: _no_operation_close_method,
            GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS: _no_operation_close_method,
        },
        GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION: _no_operation_close_method,
        GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT: _no_operation_close_method,
        GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK: _no_operation_close_method,
        GrievanceTicket.CATEGORY_REFERRAL: _no_operation_close_method,
        GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK: _no_operation_close_method,
        GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION: close_needs_adjudication_ticket,
        GrievanceTicket.CATEGORY_SYSTEM_FLAGGING: close_system_flagging_ticket,
    }

    MOVE_TO_STATUS_PERMISSION_MAPPING = {
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

    class Arguments:
        grievance_ticket_id = graphene.Argument(graphene.ID)
        status = graphene.Int()
        version = BigInt(required=False)

    @classmethod
    def get_close_function(cls, category, issue_type):
        function_or_nested_issue_types = cls.CATEGORY_ISSUE_TYPE_TO_CLOSE_FUNCTION_MAPPING.get(category)
        if isinstance(function_or_nested_issue_types, dict) and issue_type:
            return function_or_nested_issue_types.get(issue_type)
        return function_or_nested_issue_types

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, grievance_ticket_id, status, **kwargs):
        grievance_ticket_id = decode_id_string(grievance_ticket_id)
        old_grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), grievance_ticket)
        if grievance_ticket.status == status:
            return cls(grievance_ticket)

        if cls.MOVE_TO_STATUS_PERMISSION_MAPPING.get(status):
            permissions_to_use = None
            if cls.MOVE_TO_STATUS_PERMISSION_MAPPING[status].get("feedback"):
                if grievance_ticket.is_feedback:
                    permissions_to_use = cls.MOVE_TO_STATUS_PERMISSION_MAPPING[status].get("feedback")
                else:
                    permissions_to_use = cls.MOVE_TO_STATUS_PERMISSION_MAPPING[status].get("any")
            else:
                permissions_to_use = cls.MOVE_TO_STATUS_PERMISSION_MAPPING[status].get(
                    grievance_ticket.status
                ) or cls.MOVE_TO_STATUS_PERMISSION_MAPPING[status].get("any")
            if permissions_to_use:
                cls.has_creator_or_owner_permission(
                    info,
                    grievance_ticket.business_area,
                    permissions_to_use[0],
                    grievance_ticket.created_by == info.context.user,
                    permissions_to_use[1],
                    grievance_ticket.assigned_to == info.context.user,
                    permissions_to_use[2],
                )

        status_flow = POSSIBLE_STATUS_FLOW
        if grievance_ticket.is_feedback:
            status_flow = POSSIBLE_FEEDBACK_STATUS_FLOW
        if status not in status_flow[grievance_ticket.status]:
            logger.error("New status is incorrect")
            raise GraphQLError("New status is incorrect")
        if status == GrievanceTicket.STATUS_CLOSED:
            close_function = cls.get_close_function(grievance_ticket.category, grievance_ticket.issue_type)
            close_function(grievance_ticket, info)
        if status == GrievanceTicket.STATUS_ASSIGNED and not grievance_ticket.assigned_to:
            grievance_ticket.assigned_to = info.context.user
        grievance_ticket.status = status
        grievance_ticket.save()
        grievance_ticket.refresh_from_db()
        log_create(
            GrievanceTicket.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_grievance_ticket,
            grievance_ticket,
        )
        return cls(grievance_ticket=grievance_ticket)


class CreateTicketNoteMutation(PermissionMutation):
    grievance_ticket_note = graphene.Field(TicketNoteNode)

    class Arguments:
        note_input = CreateTicketNoteInput(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, note_input, **kwargs):
        grievance_ticket_id = decode_id_string(note_input["ticket"])
        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), grievance_ticket)
        cls.has_creator_or_owner_permission(
            info,
            grievance_ticket.business_area,
            Permissions.GRIEVANCES_ADD_NOTE,
            grievance_ticket.created_by == info.context.user,
            Permissions.GRIEVANCES_ADD_NOTE_AS_CREATOR,
            grievance_ticket.assigned_to == info.context.user,
            Permissions.GRIEVANCES_ADD_NOTE_AS_OWNER,
        )

        description = note_input["description"]
        created_by = info.context.user

        ticket_note = TicketNote.objects.create(ticket=grievance_ticket, description=description, created_by=created_by)

        return cls(grievance_ticket_note=ticket_note)


class IndividualDataChangeApproveMutation(DataChangeValidator, PermissionMutation):
    grievance_ticket = graphene.Field(GrievanceTicketNode)

    class Arguments:
        grievance_ticket_id = graphene.Argument(graphene.ID, required=True)
        """
        individual_approve_data have to be a dictionary with field name as key and boolean as a value,
        indicating whether field change is approved or not.
        """
        individual_approve_data = graphene.JSONString()
        approved_documents_to_create = graphene.List(graphene.Int)
        approved_documents_to_remove = graphene.List(graphene.Int)
        approved_identities_to_create = graphene.List(graphene.Int)
        approved_identities_to_remove = graphene.List(graphene.Int)
        flex_fields_approve_data = graphene.JSONString()
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls,
        root,
        info,
        grievance_ticket_id,
        individual_approve_data,
        approved_documents_to_create,
        approved_documents_to_remove,
        approved_identities_to_create,
        approved_identities_to_remove,
        flex_fields_approve_data,
        **kwargs,
    ):
        grievance_ticket_id = decode_id_string(grievance_ticket_id)
        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), grievance_ticket)
        cls.has_creator_or_owner_permission(
            info,
            grievance_ticket.business_area,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
            grievance_ticket.created_by == info.context.user,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR,
            grievance_ticket.assigned_to == info.context.user,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER,
        )
        cls.verify_approve_data(individual_approve_data)
        cls.verify_approve_data(flex_fields_approve_data)
        individual_approve_data = {to_snake_case(key): value for key, value in individual_approve_data.items()}
        individual_data_details = grievance_ticket.individual_data_update_ticket_details
        individual_data = individual_data_details.individual_data
        cls.verify_approve_data_against_object_data(individual_data, individual_approve_data)
        cls.verify_approve_data_against_object_data(individual_data.get("flex_fields"), flex_fields_approve_data)
        for field_name, item in individual_data.items():
            field_to_approve = individual_approve_data.get(field_name)
            if field_name in ("documents", "documents_to_remove"):
                for index, document_data in enumerate(individual_data[field_name]):
                    approved_documents_indexes = (
                        approved_documents_to_create if field_name == "documents" else approved_documents_to_remove
                    )
                    if index in approved_documents_indexes:
                        document_data["approve_status"] = True
                    else:
                        document_data["approve_status"] = False
            elif field_name in ("identities", "identities_to_remove"):
                for index, identity_data in enumerate(individual_data[field_name]):
                    approved_identities_indexes = (
                        approved_identities_to_create if field_name == "identities" else approved_identities_to_remove
                    )
                    if index in approved_identities_indexes:
                        identity_data["approve_status"] = True
                    else:
                        identity_data["approve_status"] = False
            elif field_name == "flex_fields":
                for flex_field_name in item.keys():
                    individual_data["flex_fields"][flex_field_name]["approve_status"] = flex_fields_approve_data.get(
                        flex_field_name
                    )
            elif field_to_approve:
                individual_data[field_name]["approve_status"] = True
            else:
                individual_data[field_name]["approve_status"] = False

        individual_data_details.individual_data = individual_data
        individual_data_details.save()
        grievance_ticket.refresh_from_db()

        return cls(grievance_ticket=grievance_ticket)


class HouseholdDataChangeApproveMutation(DataChangeValidator, PermissionMutation):
    grievance_ticket = graphene.Field(GrievanceTicketNode)

    class Arguments:
        grievance_ticket_id = graphene.Argument(graphene.ID, required=True)
        """
        household_approve_data have to be a dictionary with field name as key and boolean as a value,
        indicating whether field change is approved or not.
        """
        household_approve_data = graphene.JSONString()
        flex_fields_approve_data = graphene.JSONString()
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, grievance_ticket_id, household_approve_data, flex_fields_approve_data, **kwargs):
        grievance_ticket_id = decode_id_string(grievance_ticket_id)
        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), grievance_ticket)
        cls.has_creator_or_owner_permission(
            info,
            grievance_ticket.business_area,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
            grievance_ticket.created_by == info.context.user,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR,
            grievance_ticket.assigned_to == info.context.user,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER,
        )
        cls.verify_approve_data(household_approve_data)
        cls.verify_approve_data(flex_fields_approve_data)
        household_approve_data = {to_snake_case(key): value for key, value in household_approve_data.items()}
        household_data_details = grievance_ticket.household_data_update_ticket_details
        household_data = household_data_details.household_data
        cls.verify_approve_data_against_object_data(household_data, household_approve_data)
        cls.verify_approve_data_against_object_data(household_data.get("flex_fields"), flex_fields_approve_data)

        for field_name, item in household_data.items():
            if field_name == "flex_fields":
                for flex_field_name in item.keys():
                    household_data["flex_fields"][flex_field_name]["approve_status"] = flex_fields_approve_data.get(
                        flex_field_name
                    )
            elif household_approve_data.get(field_name):
                household_data[field_name]["approve_status"] = True
            else:
                household_data[field_name]["approve_status"] = False

        household_data_details.household_data = household_data
        household_data_details.save()
        grievance_ticket.refresh_from_db()

        return cls(grievance_ticket=grievance_ticket)


class SimpleApproveMutation(PermissionMutation):
    grievance_ticket = graphene.Field(GrievanceTicketNode)

    class Arguments:
        grievance_ticket_id = graphene.Argument(graphene.ID, required=True)
        approve_status = graphene.Boolean(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, grievance_ticket_id, approve_status, **kwargs):
        grievance_ticket_id = decode_id_string(grievance_ticket_id)
        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), grievance_ticket)
        if grievance_ticket.category in [
            GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
            GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        ]:
            cls.has_creator_or_owner_permission(
                info,
                grievance_ticket.business_area,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
                grievance_ticket.created_by == info.context.user,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
                grievance_ticket.assigned_to == info.context.user,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
            )
        else:
            cls.has_creator_or_owner_permission(
                info,
                grievance_ticket.business_area,
                Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
                grievance_ticket.created_by == info.context.user,
                Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR,
                grievance_ticket.assigned_to == info.context.user,
                Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER,
            )
        ticket_details = grievance_ticket.ticket_details
        ticket_details.approve_status = approve_status
        ticket_details.save()
        grievance_ticket.refresh_from_db()

        return cls(grievance_ticket=grievance_ticket)


class ReassignRoleMutation(graphene.Mutation):
    household = graphene.Field(HouseholdNode)
    individual = graphene.Field(IndividualNode)

    class Arguments:
        grievance_ticket_id = graphene.Argument(graphene.ID, required=True)
        household_id = graphene.Argument(graphene.ID, required=True)
        household_version = BigInt(required=False)
        individual_id = graphene.Argument(graphene.ID, required=True)
        individual_version = BigInt(required=False)
        role = graphene.String(required=True)
        version = BigInt(required=False)

    @classmethod
    def verify_role_choices(cls, role):
        if role not in [ROLE_PRIMARY, ROLE_ALTERNATE, HEAD]:
            logger.error("Provided role is invalid! Please provide one of those: PRIMARY, ALTERNATE, HEAD")
            raise GraphQLError("Provided role is invalid! Please provide one of those: PRIMARY, ALTERNATE, HEAD")

    @classmethod
    def verify_if_role_exists(cls, household, current_individual, role):
        if role == HEAD:
            if household.head_of_household.id != current_individual.id:
                logger.error("This individual is not a head of provided household")
                raise GraphQLError("This individual is not a head of provided household")
        else:
            get_object_or_404(IndividualRoleInHousehold, individual=current_individual, household=household, role=role)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls,
        root,
        info,
        household_id,
        individual_id,
        grievance_ticket_id,
        role,
        **kwargs,
    ):
        cls.verify_role_choices(role)
        decoded_household_id = decode_id_string(household_id)
        decoded_individual_id = decode_id_string(individual_id)
        grievance_ticket_id = decode_id_string(grievance_ticket_id)

        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), grievance_ticket)
        household = get_object_or_404(Household, id=decoded_household_id)
        check_concurrency_version_in_mutation(kwargs.get("household_version"), household)
        individual = get_object_or_404(Individual, id=decoded_individual_id)
        check_concurrency_version_in_mutation(kwargs.get("individual_version"), individual)

        ticket_details = grievance_ticket.ticket_details
        if grievance_ticket.category == GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION:
            ticket_individual = ticket_details.selected_individual
        elif grievance_ticket.category == GrievanceTicket.CATEGORY_SYSTEM_FLAGGING:
            ticket_individual = ticket_details.golden_records_individual
        else:
            ticket_individual = ticket_details.individual
        cls.verify_if_role_exists(household, ticket_individual, role)

        if role == HEAD:
            role_data_key = role
        else:
            role_object = get_object_or_404(
                IndividualRoleInHousehold, individual=ticket_individual, household=household, role=role
            )
            role_data_key = str(role_object.id)

        ticket_details.role_reassign_data[role_data_key] = {
            "role": role,
            "household": household_id,
            "individual": individual_id,
        }
        ticket_details.save()

        return cls(household=household, individual=individual)


class NeedsAdjudicationApproveMutation(PermissionMutation):
    grievance_ticket = graphene.Field(GrievanceTicketNode)

    class Arguments:
        grievance_ticket_id = graphene.Argument(graphene.ID, required=True)
        selected_individual_id = graphene.Argument(graphene.ID, required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, grievance_ticket_id, selected_individual_id, **kwargs):
        grievance_ticket_id = decode_id_string(grievance_ticket_id)
        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), grievance_ticket)
        cls.has_creator_or_owner_permission(
            info,
            grievance_ticket.business_area,
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            grievance_ticket.created_by == info.context.user,
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
            grievance_ticket.assigned_to == info.context.user,
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
        )
        decoded_selected_individual_id = decode_id_string(selected_individual_id)
        selected_individual = get_object_or_404(Individual, id=decoded_selected_individual_id)
        ticket_details = grievance_ticket.ticket_details

        if selected_individual not in (ticket_details.golden_records_individual, ticket_details.possible_duplicate):
            logger.error("The selected individual is not valid, must be one of those attached to the ticket")
            raise GraphQLError("The selected individual is not valid, must be one of those attached to the ticket")

        ticket_details.selected_individual = selected_individual
        ticket_details.role_reassign_data = {}
        ticket_details.save()
        grievance_ticket.refresh_from_db()

        return cls(grievance_ticket=grievance_ticket)


class Mutations(graphene.ObjectType):
    create_grievance_ticket = CreateGrievanceTicketMutation.Field()
    update_grievance_ticket = UpdateGrievanceTicketMutation.Field()
    grievance_status_change = GrievanceStatusChangeMutation.Field()
    create_ticket_note = CreateTicketNoteMutation.Field()
    approve_individual_data_change = IndividualDataChangeApproveMutation.Field()
    approve_household_data_change = HouseholdDataChangeApproveMutation.Field()
    approve_add_individual = SimpleApproveMutation.Field()
    approve_delete_individual = SimpleApproveMutation.Field()
    approve_system_flagging = SimpleApproveMutation.Field()
    approve_needs_adjudication = NeedsAdjudicationApproveMutation.Field()
    reassign_role = ReassignRoleMutation.Field()
