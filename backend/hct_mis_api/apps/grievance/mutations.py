import logging
from typing import Any, Dict, List, Optional, Union

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

import graphene
from graphql import GraphQLError

from hct_mis_api.apps.account.models import Partner, User
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
from hct_mis_api.apps.grievance.documents import bulk_update_assigned_to
from hct_mis_api.apps.grievance.inputs import (
    CreateGrievanceTicketInput,
    CreateTicketNoteInput,
    UpdateGrievanceTicketInput,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket, TicketNote
from hct_mis_api.apps.grievance.notifications import GrievanceNotification
from hct_mis_api.apps.grievance.schema import GrievanceTicketNode, TicketNoteNode
from hct_mis_api.apps.grievance.services.data_change_services import (
    update_data_change_extras,
)
from hct_mis_api.apps.grievance.services.payment_verification_services import (
    update_ticket_payment_verification_service,
)
from hct_mis_api.apps.grievance.services.referral_services import (
    update_referral_service,
)
from hct_mis_api.apps.grievance.services.ticket_based_on_payment_record_services import (
    update_ticket_based_on_payment_record_service,
)
from hct_mis_api.apps.grievance.services.ticket_creator_service import (
    TicketCreatorService,
    TicketDetailsCreatorFactory,
)
from hct_mis_api.apps.grievance.services.ticket_status_changer_service import (
    TicketStatusChangerService,
)
from hct_mis_api.apps.grievance.utils import (
    clear_cache,
    create_grievance_documents,
    delete_grievance_documents,
    get_individual,
    update_grievance_documents,
)
from hct_mis_api.apps.grievance.validators import (
    DataChangeValidator,
    validate_grievance_documents_size,
)
from hct_mis_api.apps.household.models import (
    HEAD,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Household,
    Individual,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.household.schema import HouseholdNode, IndividualNode
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.exceptions import log_and_raise

logger = logging.getLogger(__name__)


def get_partner(partner: int) -> Optional[Partner]:
    if partner:
        try:
            return Partner.objects.get(id=partner)
        except Partner.DoesNotExist as dne:
            logger.error(f"Partner {partner} does not exist")
            raise GraphQLError(f"Partner {partner} does not exist") from dne
    return None


def verify_required_arguments(input_data: Dict, field_name: str, options: Dict) -> None:
    from hct_mis_api.apps.core.utils import nested_dict_get

    for key, value in options.items():
        if key != input_data.get(field_name):
            continue
        for required in value.get("required"):
            if nested_dict_get(input_data, required) is None:
                log_and_raise(f"You have to provide {required} in {key}")
        for not_allowed in value.get("not_allowed"):
            if nested_dict_get(input_data, not_allowed) is not None:
                log_and_raise(f"You can't provide {not_allowed} in {key}")


class CreateGrievanceTicketMutation(PermissionMutation):
    grievance_tickets = graphene.List(GrievanceTicketNode)

    CATEGORY_OPTIONS = {
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
    def mutate(cls, root: Any, info: Any, input: Dict, **kwargs: Any) -> "CreateGrievanceTicketMutation":
        user = info.context.user
        business_area = get_object_or_404(BusinessArea, slug=input.pop("business_area"))
        cls.has_permission(info, Permissions.GRIEVANCES_CREATE, business_area)

        if input.get("category") in (
            GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
            GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        ):
            raise GraphQLError("Feedback tickets are not allowed to be created through this mutation.")

        verify_required_arguments(input, "category", cls.CATEGORY_OPTIONS)
        if input.get("issue_type"):
            verify_required_arguments(input, "issue_type", cls.ISSUE_TYPE_OPTIONS)

        if input.get("documentation", None):
            cls.has_permission(info, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD, business_area)

        details_creator = TicketDetailsCreatorFactory.get_for_category(input.get("category"))
        creator = TicketCreatorService(details_creator)
        grievances = creator.create(user, business_area, input)
        return cls(grievance_tickets=grievances)


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
    def mutate(cls, root: Any, info: Any, input: Dict, **kwargs: Any) -> "UpdateGrievanceTicketMutation":
        user = info.context.user
        ticket_id = decode_id_string(input.pop("ticket_id"))
        old_grievance_ticket = get_object_or_404(GrievanceTicket, id=ticket_id)
        grievance_ticket = get_object_or_404(GrievanceTicket, id=ticket_id)
        business_area = grievance_ticket.business_area

        check_concurrency_version_in_mutation(kwargs.get("version"), grievance_ticket)

        cls.has_creator_or_owner_permission(
            info,
            business_area,
            Permissions.GRIEVANCES_UPDATE,
            grievance_ticket.created_by == user,
            Permissions.GRIEVANCES_UPDATE_AS_CREATOR,
            grievance_ticket.assigned_to == user,
            Permissions.GRIEVANCES_UPDATE_AS_OWNER,
        )

        if grievance_ticket.category in (
            GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
            GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        ):
            raise GraphQLError("Feedback tickets are not allowed to be created through this mutation.")

        if grievance_ticket.status == GrievanceTicket.STATUS_CLOSED:
            raise ValidationError("Grievance Ticket in status Closed is not editable")

        if grievance_ticket.issue_type:
            verify_required_arguments(input, "issue_type", cls.EXTRAS_OPTIONS)

        extras = input.pop("extras", {})
        grievance_ticket = cls.update_basic_data(user, input, grievance_ticket)

        update_extra_methods = {
            GrievanceTicket.CATEGORY_REFERRAL: update_referral_service,
            GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION: update_ticket_payment_verification_service,
            GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE: update_ticket_based_on_payment_record_service,
            GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT: update_ticket_based_on_payment_record_service,
        }

        if cls.has_creator_or_owner_permission(
            info,
            business_area,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE,
            grievance_ticket.created_by == user,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR,
            grievance_ticket.assigned_to == user,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER,
            False,
        ):
            update_extra_methods[GrievanceTicket.CATEGORY_DATA_CHANGE] = update_data_change_extras

        if update_extra_method := update_extra_methods.get(grievance_ticket.category):
            grievance_ticket = update_extra_method(grievance_ticket, extras, input)

        log_create(
            GrievanceTicket.ACTIVITY_LOG_MAPPING,
            "business_area",
            user,
            old_grievance_ticket,
            grievance_ticket,
        )
        return cls(grievance_ticket=grievance_ticket)

    @classmethod
    def update_basic_data(cls, approver: User, input_data: Dict, grievance_ticket: GrievanceTicket) -> GrievanceTicket:
        messages = []

        if ids_to_delete := input_data.pop("documentation_to_delete", None):
            delete_grievance_documents(grievance_ticket.id, ids_to_delete)

        if documents_to_update := input_data.pop("documentation_to_update", None):
            validate_grievance_documents_size(grievance_ticket.id, documents_to_update, is_updated=True)
            update_grievance_documents(documents_to_update)

        if documents := input_data.pop("documentation", None):
            validate_grievance_documents_size(grievance_ticket.id, documents)
            create_grievance_documents(approver, grievance_ticket, documents)

        if priority := input_data.pop("priority", None):
            grievance_ticket.priority = priority

        if urgency := input_data.pop("urgency", None):
            grievance_ticket.urgency = urgency

        if partner := get_partner(input_data.pop("partner", None)):
            grievance_ticket.partner = partner

        if programme := input_data.pop("programme", None):
            grievance_ticket.programme = get_object_or_404(Program, pk=decode_id_string(programme))

        assigned_to_id = decode_id_string(input_data.pop("assigned_to", None))
        assigned_to = get_object_or_404(get_user_model(), id=assigned_to_id) if assigned_to_id else None

        if admin := input_data.pop("admin", None):
            grievance_ticket.admin2 = get_object_or_404(Area, p_code=admin)

        linked_tickets_encoded_ids = input_data.pop("linked_tickets", [])
        linked_tickets = [decode_id_string(encoded_id) for encoded_id in linked_tickets_encoded_ids]
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


class GrievanceStatusChangeMutation(PermissionMutation):
    grievance_ticket = graphene.Field(GrievanceTicketNode)

    MOVE_TO_STATUS_PERMISSION_MAPPING: Dict[int, Dict[Union[str, int], List[Permissions]]] = {
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
    def get_permissions(cls, status: int, current_status: int, is_feedback: bool) -> List[Permissions]:
        permissions = cls.MOVE_TO_STATUS_PERMISSION_MAPPING.get(status, {})
        feedback_permissions = permissions.get("feedback", [])
        any_permissions = permissions.get("any", [])
        based_on_current_status_permissions = permissions.get(current_status, [])

        if is_feedback:
            return feedback_permissions or any_permissions or based_on_current_status_permissions
        return any_permissions or based_on_current_status_permissions

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls, root: Any, info: Any, grievance_ticket_id: Optional[str], status: int, **kwargs: Any
    ) -> "GrievanceStatusChangeMutation":
        user = info.context.user
        notifications = []
        grievance_ticket_id = decode_id_string(grievance_ticket_id)
        old_grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), grievance_ticket)

        if grievance_ticket.category in (
            GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
            GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        ):
            raise GraphQLError("Feedback tickets are not allowed to be created through this mutation.")

        if grievance_ticket.status == status:
            return cls(grievance_ticket)

        if permissions_to_use := cls.get_permissions(status, grievance_ticket.status, grievance_ticket.is_feedback):
            cls.has_creator_or_owner_permission(
                info,
                grievance_ticket.business_area,
                permissions_to_use[0],
                grievance_ticket.created_by == user,
                permissions_to_use[1],
                grievance_ticket.assigned_to == user,
                permissions_to_use[2],
            )

        if status == GrievanceTicket.STATUS_ASSIGNED and not grievance_ticket.assigned_to:
            cls.has_permission(info, Permissions.GRIEVANCE_ASSIGN, grievance_ticket.business_area)
            notifications.append(
                GrievanceNotification(grievance_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)
            )

        if not grievance_ticket.can_change_status(status):
            log_and_raise("New status is incorrect")

        status_changer = TicketStatusChangerService(grievance_ticket, user)
        status_changer.change_status(status)

        grievance_ticket.refresh_from_db()

        if grievance_ticket.status == GrievanceTicket.STATUS_FOR_APPROVAL:
            notifications.append(GrievanceNotification(grievance_ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL))

        if grievance_ticket.status == GrievanceTicket.STATUS_CLOSED:
            clear_cache(grievance_ticket.ticket_details, grievance_ticket.business_area.slug)

        if (
            old_grievance_ticket.status == GrievanceTicket.STATUS_FOR_APPROVAL
            and grievance_ticket.status == GrievanceTicket.STATUS_IN_PROGRESS
        ):
            notifications.append(
                GrievanceNotification(
                    grievance_ticket,
                    GrievanceNotification.ACTION_SEND_BACK_TO_IN_PROGRESS,
                    approver=user,
                )
            )

        log_create(
            GrievanceTicket.ACTIVITY_LOG_MAPPING,
            "business_area",
            user,
            old_grievance_ticket,
            grievance_ticket,
        )

        GrievanceNotification.send_all_notifications(notifications)
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
    def mutate(
        cls,
        root: Any,
        info: Any,
        grievance_ticket_unicef_ids: List[str],
        assigned_to: str,
        business_area_slug: str,
        **kwargs: Any,
    ) -> "BulkUpdateGrievanceTicketsAssigneesMutation":
        cls.has_permission(info, Permissions.GRIEVANCES_UPDATE, business_area_slug)
        assigned_to_id = decode_id_string(assigned_to)
        assigned_to_obj: AbstractBaseUser = get_object_or_404(get_user_model(), id=assigned_to_id)
        grievance_tickets = GrievanceTicket.objects.filter(
            ~Q(status=GrievanceTicket.STATUS_CLOSED),
            ~Q(assigned_to__id=assigned_to_obj.id),
            unicef_id__in=grievance_ticket_unicef_ids,
        )
        grievance_tickets_ids = list(grievance_tickets.values_list("id", flat=True))

        if grievance_tickets.exists():
            grievance_tickets.update(assigned_to=assigned_to_obj)
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
    def mutate(cls, root: Any, info: Any, note_input: Dict, **kwargs: Any) -> "CreateTicketNoteMutation":
        user = info.context.user
        grievance_ticket_id = decode_id_string(note_input["ticket"])
        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), grievance_ticket)
        cls.has_creator_or_owner_permission(
            info,
            grievance_ticket.business_area,
            Permissions.GRIEVANCES_ADD_NOTE,
            grievance_ticket.created_by == user,
            Permissions.GRIEVANCES_ADD_NOTE_AS_CREATOR,
            grievance_ticket.assigned_to == user,
            Permissions.GRIEVANCES_ADD_NOTE_AS_OWNER,
        )

        description = note_input["description"]
        ticket_note = TicketNote.objects.create(ticket=grievance_ticket, description=description, created_by=user)
        notification = GrievanceNotification(
            grievance_ticket,
            GrievanceNotification.ACTION_NOTES_ADDED,
            created_by=user,
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
        root: Any,
        info: Any,
        grievance_ticket_id: Optional[str],
        individual_approve_data: Dict[str, Any],
        approved_documents_to_create: List,
        approved_documents_to_edit: List,
        approved_documents_to_remove: List,
        approved_identities_to_create: List,
        approved_identities_to_edit: List,
        approved_identities_to_remove: List,
        approved_payment_channels_to_create: List,
        approved_payment_channels_to_edit: List,
        approved_payment_channels_to_remove: List,
        flex_fields_approve_data: Dict,
        **kwargs: Any,
    ) -> "IndividualDataChangeApproveMutation":
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
        root: Any,
        info: Any,
        grievance_ticket_id: Optional[str],
        household_approve_data: Dict,
        flex_fields_approve_data: Dict,
        **kwargs: Any,
    ) -> "HouseholdDataChangeApproveMutation":
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
    def mutate(
        cls,
        root: Any,
        info: Any,
        grievance_ticket_id: Optional[str],
        approve_status: int,
        **kwargs: Any,
    ) -> "SimpleApproveMutation":
        grievance_ticket_id = decode_id_string(grievance_ticket_id)
        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), grievance_ticket)
        if grievance_ticket.category in (
            GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
            GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        ):
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


class DeleteHouseholdApproveMutation(PermissionMutation):
    grievance_ticket = graphene.Field(GrievanceTicketNode)

    class Arguments:
        grievance_ticket_id = graphene.Argument(graphene.ID, required=True)
        approve_status = graphene.Boolean(required=True)
        reason_hh_id = graphene.String(required=False)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls,
        root: Any,
        info: Any,
        grievance_ticket_id: Optional[str],
        approve_status: int,
        reason_hh_id: Optional[str] = None,
        **kwargs: Any,
    ) -> "DeleteHouseholdApproveMutation":
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

        ticket_details = grievance_ticket.ticket_details

        reason_hh_obj = None
        reason_hh_id = reason_hh_id.strip() if reason_hh_id else None
        if reason_hh_id:
            # validate reason HH id
            reason_hh_obj = get_object_or_404(Household, unicef_id=reason_hh_id)
            if reason_hh_obj.withdrawn:
                raise ValidationError(f"The provided household {reason_hh_obj.unicef_id} has to be active.")

        # update reason_household value
        ticket_details.reason_household = reason_hh_obj  # set HH or None
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
    def verify_role_choices(cls, role: str) -> None:
        if role not in (ROLE_PRIMARY, ROLE_ALTERNATE, HEAD):
            log_and_raise("Provided role is invalid! Please provide one of those: PRIMARY, ALTERNATE, HEAD")

    @classmethod
    def verify_if_role_exists(cls, household: Household, current_individual: Individual, role: str) -> None:
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

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls,
        root: Any,
        info: Any,
        household_id: Optional[str],
        individual_id: Optional[str],
        grievance_ticket_id: Optional[str],
        role: Any,
        **kwargs: Any,
    ) -> "ReassignRoleMutation":
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
    def mutate(
        cls, root: Any, info: Any, grievance_ticket_id: Optional[str], **kwargs: Any
    ) -> "NeedsAdjudicationApproveMutation":
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
            log_and_raise("Only one option for selected individuals is available")

        ticket_details = grievance_ticket.ticket_details

        if selected_individual_id:
            selected_individual = get_individual(selected_individual_id)

            if selected_individual not in (
                ticket_details.golden_records_individual,
                ticket_details.possible_duplicate,
            ):
                log_and_raise("The selected individual is not valid, must be one of those attached to the ticket")

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
    def mutate(
        cls, root: Any, info: Any, grievance_ticket_id: Optional[str], **kwargs: Any
    ) -> "PaymentDetailsApproveMutation":
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
            log_and_raise("Payment Details changes can approve only for Grievance Ticket in status For Approval")

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
    approve_delete_household = DeleteHouseholdApproveMutation.Field()
    approve_system_flagging = SimpleApproveMutation.Field()
    approve_needs_adjudication = NeedsAdjudicationApproveMutation.Field()
    approve_payment_details = PaymentDetailsApproveMutation.Field()
    reassign_role = ReassignRoleMutation.Field()
