import logging
from enum import Enum
from typing import Union

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.grievance.documents import bulk_update_assigned_to
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.payment.models import PaymentRecord

import graphene
from graphql import GraphQLError

from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.account.permissions import PermissionMutation, Permissions
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.core.scalars import BigInt
from hct_mis_api.apps.core.utils import (
    check_concurrency_version_in_mutation,
    decode_id_string,
    to_snake_case,
)
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.grievance.models import GrievanceTicket, TicketNote
from hct_mis_api.apps.grievance.mutations_extras.data_change import (
    close_add_individual_grievance_ticket,
    close_delete_household_ticket,
    close_delete_individual_ticket,
    close_update_household_grievance_ticket,
    close_update_individual_grievance_ticket,
    save_data_change_extras,
    update_data_change_extras,
)
from hct_mis_api.apps.grievance.mutations_extras.feedback import (
    save_negative_feedback_extras,
    save_positive_feedback_extras,
    update_negative_feedback_extras,
    update_positive_feedback_extras,
)
from hct_mis_api.apps.grievance.mutations_extras.grievance_complaint import (
    save_grievance_complaint_extras,
)
from hct_mis_api.apps.grievance.mutations_extras.main import (
    _no_operation_close_method,
)
from hct_mis_api.apps.grievance.mutations_extras.payment_verification import (
    save_payment_verification_extras,
)
from hct_mis_api.apps.grievance.mutations_extras.referral import (
    save_referral_extras,
    update_referral_extras,
)
from hct_mis_api.apps.grievance.mutations_extras.sensitive_grievance import (
    save_sensitive_grievance_extras,
)
from hct_mis_api.apps.grievance.mutations_extras.system_tickets import (
    close_needs_adjudication_ticket,
    close_system_flagging_ticket,
)
from hct_mis_api.apps.grievance.mutations_extras.ticket_payment_verification_details import (
    update_ticket_payment_verification_details_extras,
)
from hct_mis_api.apps.grievance.mutations_extras.utils import (
    remove_parsed_data_fields,
    verify_required_arguments,
)
from hct_mis_api.apps.grievance.notifications import GrievanceNotification
from hct_mis_api.apps.grievance.schema import GrievanceTicketNode, TicketNoteNode
from hct_mis_api.apps.grievance.utils import get_individual, traverse_sibling_tickets
from hct_mis_api.apps.grievance.validators import DataChangeValidator
from hct_mis_api.apps.household.models import (
    HEAD,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Household,
    Individual,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.household.schema import HouseholdNode, IndividualNode
from hct_mis_api.apps.grievance.inputs import (
    CreateGrievanceTicketInput,
    CreateTicketNoteInput,
    UpdateGrievanceTicketInput,
)

logger = logging.getLogger(__name__)


def get_partner(id: int):
    if id:
        try:
            return Partner.objects.get(id=id)
        except Partner.DoesNotExist as dne:
            logger.error(f"Partner {id} does not exist")
            raise GraphQLError(f"Partner {id} does not exist") from dne


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
            "required": ["issue_type"],
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

        # TODO
        # if category in (
        #     GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
        #     GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        # ):
        #     raise GraphQLError("Feedback tickets are not allowed to be created through this mutation.")

        grievance_ticket, extras = cls.save_basic_data(root, info, input, **kwargs)
        save_extra_methods = {
            GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION: save_payment_verification_extras,
            GrievanceTicket.CATEGORY_DATA_CHANGE: save_data_change_extras,
            GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT: save_grievance_complaint_extras,
            GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE: save_sensitive_grievance_extras,
            GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK: save_positive_feedback_extras,
            GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK: save_negative_feedback_extras,
            GrievanceTicket.CATEGORY_REFERRAL: save_referral_extras,
        }
        save_extra_method = save_extra_methods.get(category)
        grievances = [grievance_ticket]
        if save_extra_method:
            grievances = save_extra_method(root, info, input, grievance_ticket, extras, **kwargs)
        for grievance in grievances:
            log_create(
                GrievanceTicket.ACTIVITY_LOG_MAPPING,
                "business_area",
                info.context.user,
                None,
                grievance,
            )
        return cls(grievance_tickets=grievances)

    @classmethod
    def save_basic_data(cls, root, info, input, **kwargs):
        arg = lambda name, default=None: input.get(name, default)
        user = info.context.user
        assigned_to_id = decode_id_string(arg("assigned_to"))
        linked_tickets_encoded_ids = arg("linked_tickets", [])
        linked_tickets = [decode_id_string(encoded_id) for encoded_id in linked_tickets_encoded_ids]
        business_area_slug = arg("business_area")
        partner = get_partner(input.pop("partner", None))
        extras = arg("extras", {})
        remove_parsed_data_fields(input, ("linked_tickets", "extras", "business_area", "assigned_to"))
        admin = input.pop("admin", None)
        admin_object = None
        assigned_to = None
        if admin:
            admin_object = get_object_or_404(Area, p_code=admin)
        business_area = get_object_or_404(BusinessArea, slug=business_area_slug)
        if assigned_to_id is not None:
            assigned_to = get_object_or_404(get_user_model(), id=assigned_to_id)
        programme = input.pop("programme", None)
        if programme:
            programme = get_object_or_404(Program, pk=decode_id_string(programme))
        linked_feedback_id = input.pop("linked_feedback_id")
        grievance_ticket = GrievanceTicket.objects.create(
            **input,
            admin2=admin_object,
            business_area=business_area,
            created_by=user,
            user_modified=timezone.now(),
            assigned_to=assigned_to,
            status=GrievanceTicket.STATUS_ASSIGNED,
            partner=partner,
            programme=programme,
        )
        GrievanceNotification.send_all_notifications(
            GrievanceNotification.prepare_notification_for_ticket_creation(grievance_ticket)
        )
        if linked_feedback_id:
            linked_feedback = Feedback.objects.get(id=linked_feedback_id)
            linked_feedback.linked_grievance = grievance_ticket
            linked_feedback.save()
        grievance_ticket.linked_tickets.set(linked_tickets)
        return grievance_ticket, extras


class UpdateGrievanceTicketMutation(PermissionMutation):
    grievance_ticket = graphene.Field(GrievanceTicketNode)

    EXTRAS_OPTIONS = {
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
        GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD: {"required": [], "not_allowed": []},
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
        household, individual, payment_record = None, None, None

        if arg("household") is not None:
            household = get_object_or_404(Household, id=decode_id_string(arg("household")))

        if arg("individual") is not None:
            individual = get_object_or_404(Individual, id=decode_id_string(arg("individual")))

        if arg("payment_record") is not None:
            payment_record = get_object_or_404(PaymentRecord, id=decode_id_string(arg("payment_record")))

        if arg("priority") is not None:
            grievance_ticket.priority = arg("priority")

        if arg("urgency") is not None:
            grievance_ticket.urgency = arg("urgency")

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

        update_extra_methods = {
            GrievanceTicket.CATEGORY_REFERRAL: update_referral_extras,
            GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK: update_positive_feedback_extras,
            GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK: update_negative_feedback_extras,
            GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION: update_ticket_payment_verification_details_extras,
        }
        update_extra_method = update_extra_methods.get(grievance_ticket.category)
        if update_extra_method:
            grievance_ticket = update_extra_method(root, info, input, grievance_ticket, extras, **kwargs)

        if grievance_ticket.category in (
            GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        ):
            ticket_details = grievance_ticket.ticket_details

            if ticket_details.household and ticket_details.household != household:
                raise GraphQLError("Cannot change household")
            if ticket_details.individual and ticket_details.individual != individual:
                raise GraphQLError("Cannot change individual")

            if household:
                ticket_details.household = household
            if individual:
                ticket_details.individual = individual
            if payment_record:
                ticket_details.payment_record = payment_record
            ticket_details.save()

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
        old_status = grievance_ticket.status
        old_assigned_to = grievance_ticket.assigned_to
        arg = lambda name, default=None: input.get(name, default)
        assigned_to_id = decode_id_string(arg("assigned_to"))
        linked_tickets_encoded_ids = arg("linked_tickets", [])
        linked_tickets = [decode_id_string(encoded_id) for encoded_id in linked_tickets_encoded_ids]
        partner = get_partner(input.pop("partner", None))
        if partner:
            grievance_ticket.partner = partner
        programme = input.pop("programme", None)
        if programme:
            grievance_ticket.programme = get_object_or_404(Program, pk=decode_id_string(programme))
        extras = arg("extras", {})
        remove_parsed_data_fields(input, ("linked_tickets", "extras", "assigned_to"))
        assigned_to = get_object_or_404(get_user_model(), id=assigned_to_id) if assigned_to_id else None
        for field, value in input.items():
            current_value = getattr(grievance_ticket, field, None)
            if not current_value:
                setattr(grievance_ticket, field, value)

        if assigned_to != grievance_ticket.assigned_to:
            if grievance_ticket.status == GrievanceTicket.STATUS_NEW and grievance_ticket.assigned_to is None:
                grievance_ticket.status = GrievanceTicket.STATUS_ASSIGNED
            grievance_ticket.assigned_to = assigned_to
            if grievance_ticket.status in (
                GrievanceTicket.STATUS_ON_HOLD,
                GrievanceTicket.STATUS_FOR_APPROVAL,
            ):
                grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
        else:
            if grievance_ticket.status == GrievanceTicket.STATUS_FOR_APPROVAL:
                grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS

        grievance_ticket.partner = get_partner(input.pop("partner", None))
        grievance_ticket.user_modified = timezone.now()
        grievance_ticket.save()

        grievance_ticket.linked_tickets.set(linked_tickets)
        grievance_ticket.refresh_from_db()
        if (
            old_status == GrievanceTicket.STATUS_FOR_APPROVAL
            and grievance_ticket.status == GrievanceTicket.STATUS_IN_PROGRESS
        ):
            back_to_in_progress_notification = GrievanceNotification(
                grievance_ticket,
                GrievanceNotification.ACTION_SEND_BACK_TO_IN_PROGRESS,
                approver=info.context.user,
            )
            back_to_in_progress_notification.send_email_notification()
        if old_assigned_to != grievance_ticket.assigned_to:
            assignment_notification = GrievanceNotification(
                grievance_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED
            )
            assignment_notification.send_email_notification()
        return grievance_ticket, extras


POSSIBLE_STATUS_FLOW = {
    GrievanceTicket.STATUS_NEW: (GrievanceTicket.STATUS_ASSIGNED,),
    GrievanceTicket.STATUS_ASSIGNED: (GrievanceTicket.STATUS_IN_PROGRESS,),
    GrievanceTicket.STATUS_IN_PROGRESS: (
        GrievanceTicket.STATUS_ON_HOLD,
        GrievanceTicket.STATUS_FOR_APPROVAL,
    ),
    GrievanceTicket.STATUS_ON_HOLD: (
        GrievanceTicket.STATUS_IN_PROGRESS,
        GrievanceTicket.STATUS_FOR_APPROVAL,
    ),
    GrievanceTicket.STATUS_FOR_APPROVAL: (
        GrievanceTicket.STATUS_IN_PROGRESS,
        GrievanceTicket.STATUS_CLOSED,
    ),
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
    GrievanceTicket.STATUS_FOR_APPROVAL: (
        GrievanceTicket.STATUS_IN_PROGRESS,
        GrievanceTicket.STATUS_CLOSED,
    ),
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
            GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD: close_delete_household_ticket,
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
        GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION: save_payment_verification_extras,
        GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT: _no_operation_close_method,
        GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK: _no_operation_close_method,
        GrievanceTicket.CATEGORY_REFERRAL: _no_operation_close_method,
        GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK: _no_operation_close_method,
        GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION: close_needs_adjudication_ticket,
        GrievanceTicket.CATEGORY_SYSTEM_FLAGGING: close_system_flagging_ticket,
    }

    MOVE_TO_STATUS_PERMISSION_MAPPING: dict[str, dict[Union[str, int], list[Enum]]] = {
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
            ticket_details = grievance_ticket.ticket_details
            if getattr(grievance_ticket.ticket_details, "is_multiple_duplicates_version", False):
                selected_individuals = ticket_details.selected_individuals.all()
                for individual in selected_individuals:
                    traverse_sibling_tickets(grievance_ticket, individual)

            close_function = cls.get_close_function(grievance_ticket.category, grievance_ticket.issue_type)
            close_function(grievance_ticket, info)
            grievance_ticket.refresh_from_db()
        if status == GrievanceTicket.STATUS_ASSIGNED and not grievance_ticket.assigned_to:
            cls.has_permission(info, Permissions.GRIEVANCE_ASSIGN, grievance_ticket.business_area)
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
        if (
            old_grievance_ticket.status != GrievanceTicket.STATUS_FOR_APPROVAL
            and grievance_ticket.status == GrievanceTicket.STATUS_FOR_APPROVAL
        ):
            for_approval_notification = GrievanceNotification(
                grievance_ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL
            )
            for_approval_notification.send_email_notification()
        if (
            old_grievance_ticket.status == GrievanceTicket.STATUS_FOR_APPROVAL
            and grievance_ticket.status == GrievanceTicket.STATUS_IN_PROGRESS
        ):
            back_to_in_progress_notification = GrievanceNotification(
                grievance_ticket,
                GrievanceNotification.ACTION_SEND_BACK_TO_IN_PROGRESS,
                approver=info.context.user,
            )
            back_to_in_progress_notification.send_email_notification()
        if old_grievance_ticket.assigned_to != grievance_ticket.assigned_to:
            assignment_notification = GrievanceNotification(
                grievance_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED
            )
            assignment_notification.send_email_notification()
        return cls(grievance_ticket=grievance_ticket)


class BulkUpdateGrievanceTicketsAssigneesMutation(PermissionMutation):
    grievance_tickets = graphene.List(GrievanceTicketNode)

    class Arguments:
        grievance_ticket_unicef_ids = graphene.List(graphene.ID)
        assigned_to = graphene.String()
        business_area_slug = graphene.String(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, grievance_ticket_unicef_ids, assigned_to, business_area_slug, **kwargs):
        cls.has_permission(info, Permissions.GRIEVANCES_UPDATE, business_area_slug)
        assigned_to_id = decode_id_string(assigned_to)
        assigned_to = get_object_or_404(get_user_model(), id=assigned_to_id)
        grievance_tickets = GrievanceTicket.objects.filter(
            ~Q(status=GrievanceTicket.STATUS_CLOSED),
            ~Q(assigned_to__id=assigned_to.id),
            unicef_id__in=grievance_ticket_unicef_ids,
        )
        grievance_tickets_ids = list(grievance_tickets.values_list("id", flat=True))

        if grievance_tickets.exists():
            grievance_tickets.update(assigned_to=assigned_to)
            bulk_update_assigned_to(grievance_tickets_ids, assigned_to_id)

        return cls(grievance_tickets=GrievanceTicket.objects.filter(id__in=grievance_tickets_ids))


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
        notification = GrievanceNotification(
            grievance_ticket,
            GrievanceNotification.ACTION_NOTES_ADDED,
            created_by=created_by,
            ticket_note=ticket_note,
        )
        notification.send_email_notification()
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
        approved_documents_to_edit = graphene.List(graphene.Int)
        approved_documents_to_remove = graphene.List(graphene.Int)
        approved_identities_to_create = graphene.List(graphene.Int)
        approved_identities_to_edit = graphene.List(graphene.Int)
        approved_identities_to_remove = graphene.List(graphene.Int)
        approved_payment_channels_to_create = graphene.List(graphene.Int)
        approved_payment_channels_to_edit = graphene.List(graphene.Int)
        approved_payment_channels_to_remove = graphene.List(graphene.Int)
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
        approved_documents_to_edit,
        approved_documents_to_remove,
        approved_identities_to_create,
        approved_identities_to_edit,
        approved_identities_to_remove,
        approved_payment_channels_to_create,
        approved_payment_channels_to_edit,
        approved_payment_channels_to_remove,
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

        documents_mapping = {
            "documents": approved_documents_to_create,
            "documents_to_remove": approved_documents_to_remove,
            "documents_to_edit": approved_documents_to_edit,
            "identities": approved_identities_to_create,
            "identities_to_remove": approved_identities_to_remove,
            "identities_to_edit": approved_identities_to_edit,
            "payment_channels": approved_payment_channels_to_create,
            "payment_channels_to_remove": approved_payment_channels_to_remove,
            "payment_channels_to_edit": approved_payment_channels_to_edit,
        }

        for field_name, item in individual_data.items():
            field_to_approve = individual_approve_data.get(field_name)
            if field_name in documents_mapping:
                for index, document_data in enumerate(individual_data[field_name]):
                    approved_documents_indexes = documents_mapping.get(field_name, [])
                    document_data["approve_status"] = index in approved_documents_indexes
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
    def mutate(
        cls,
        root,
        info,
        grievance_ticket_id,
        household_approve_data,
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
        new_individual_id = graphene.Argument(graphene.ID, required=False)
        individual_version = BigInt(required=False)
        role = graphene.String(required=True)
        version = BigInt(required=False)

    @classmethod
    def verify_role_choices(cls, role):
        if role not in (ROLE_PRIMARY, ROLE_ALTERNATE, HEAD):
            logger.error("Provided role is invalid! Please provide one of those: PRIMARY, ALTERNATE, HEAD")
            raise GraphQLError("Provided role is invalid! Please provide one of those: PRIMARY, ALTERNATE, HEAD")

    @classmethod
    def verify_if_role_exists(cls, household, current_individual, role):
        if role == HEAD:
            if household.head_of_household.id != current_individual.id:
                logger.error("This individual is not a head of provided household")
                raise GraphQLError("This individual is not a head of provided household")
        else:
            get_object_or_404(
                IndividualRoleInHousehold,
                individual=current_individual,
                household=household,
                role=role,
            )

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
            if ticket_details.is_multiple_duplicates_version:
                ticket_individual = individual
            else:
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
                IndividualRoleInHousehold,
                individual=ticket_individual,
                household=household,
                role=role,
            )
            role_data_key = str(role_object.id)

        ticket_details.role_reassign_data[role_data_key] = {
            "role": role,
            "household": household_id,
            "individual": individual_id,
        }

        if getattr(ticket_details, "is_multiple_duplicates_version", False):
            new_individual_id = kwargs.get("new_individual_id")
            ticket_details.role_reassign_data[role_data_key]["new_individual"] = new_individual_id
        ticket_details.save()

        return cls(household=household, individual=individual)


class NeedsAdjudicationApproveMutation(PermissionMutation):
    grievance_ticket = graphene.Field(GrievanceTicketNode)

    class Arguments:
        grievance_ticket_id = graphene.Argument(graphene.ID, required=True)
        selected_individual_id = graphene.Argument(graphene.ID, required=False)
        selected_individual_ids = graphene.List(graphene.ID, required=False)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, grievance_ticket_id, **kwargs):
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

        selected_individual_id = kwargs.get("selected_individual_id", None)
        selected_individual_ids = kwargs.get("selected_individual_ids", None)

        if selected_individual_id and selected_individual_ids:
            logger.error("Only one option for selected individuals is available")
            raise GraphQLError("Only one option for selected individuals is available")

        ticket_details = grievance_ticket.ticket_details

        if selected_individual_id:
            selected_individual = get_individual(selected_individual_id)

            if selected_individual not in (
                ticket_details.golden_records_individual,
                ticket_details.possible_duplicate,
            ):
                logger.error("The selected individual is not valid, must be one of those attached to the ticket")
                raise GraphQLError("The selected individual is not valid, must be one of those attached to the ticket")

            ticket_details.selected_individual = selected_individual
            ticket_details.role_reassign_data = {}

        if selected_individual_ids:  # Allow choosing multiple individuals
            selected_individuals = [get_individual(_id) for _id in selected_individual_ids]
            ticket_details.selected_individuals.remove(*ticket_details.selected_individuals.all())
            ticket_details.selected_individuals.add(*selected_individuals)

        ticket_details.save()
        grievance_ticket.refresh_from_db()

        return cls(grievance_ticket=grievance_ticket)


class PaymentDetailsApproveMutation(PermissionMutation):
    grievance_ticket = graphene.Field(GrievanceTicketNode)

    class Arguments:
        grievance_ticket_id = graphene.Argument(graphene.ID, required=True)
        approve_status = graphene.Boolean(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, grievance_ticket_id, **kwargs):
        grievance_ticket_id = decode_id_string(grievance_ticket_id)
        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), grievance_ticket)
        cls.has_creator_or_owner_permission(
            info,
            grievance_ticket.business_area,
            Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION,
            grievance_ticket.created_by == info.context.user,
            Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_CREATOR,
            grievance_ticket.assigned_to == info.context.user,
            Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_OWNER,
        )

        if grievance_ticket.status != GrievanceTicket.STATUS_FOR_APPROVAL:
            logger.error("Payment Details changes can approve only for Grievance Ticket on status For Approval")
            raise GraphQLError("Payment Details changes can approve only for Grievance Ticket on status For Approval")

        old_payment_verification_ticket_details = grievance_ticket.payment_verification_ticket_details
        grievance_ticket.payment_verification_ticket_details.approve_status = kwargs.get("approve_status", False)
        grievance_ticket.payment_verification_ticket_details.save()

        return cls(grievance_ticket=grievance_ticket)


class Mutations(graphene.ObjectType):
    create_grievance_ticket = CreateGrievanceTicketMutation.Field()
    update_grievance_ticket = UpdateGrievanceTicketMutation.Field()
    grievance_status_change = GrievanceStatusChangeMutation.Field()
    bulk_update_grievance_assignee = BulkUpdateGrievanceTicketsAssigneesMutation.Field()
    create_ticket_note = CreateTicketNoteMutation.Field()
    approve_individual_data_change = IndividualDataChangeApproveMutation.Field()
    approve_household_data_change = HouseholdDataChangeApproveMutation.Field()
    approve_add_individual = SimpleApproveMutation.Field()
    approve_delete_individual = SimpleApproveMutation.Field()
    approve_delete_household = SimpleApproveMutation.Field()
    approve_system_flagging = SimpleApproveMutation.Field()
    approve_needs_adjudication = NeedsAdjudicationApproveMutation.Field()
    approve_payment_details = PaymentDetailsApproveMutation.Field()
    reassign_role = ReassignRoleMutation.Field()
