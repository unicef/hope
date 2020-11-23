import graphene
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from graphene.utils.str_converters import to_snake_case
from graphql import GraphQLError

from account.schema import UserNode
from core.models import BusinessArea
from core.permissions import is_authenticated
from core.schema import BusinessAreaNode
from core.utils import nested_dict_get, decode_id_string
from grievance.mutations_extras.data_change import save_data_change_extras
from grievance.mutations_extras.grievance_complaint import save_grievance_complaint_extras
from grievance.mutations_extras.main import CreateGrievanceTicketExtrasInput
from grievance.models import GrievanceTicket, TicketNote
from grievance.mutations_extras.payment_verification import save_payment_verification_extras
from grievance.mutations_extras.sensitive_grievance import save_sensitive_grievance_extras
from grievance.schema import GrievanceTicketNode, TicketNoteNode
from grievance.validators import DataChangeValidator


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


class CreateTicketNoteInput(graphene.InputObjectType):
    description = graphene.String(required=True)
    ticket = graphene.GlobalID(node=GrievanceTicketNode, required=True)


class CreateGrievanceTicketMutation(graphene.Mutation):
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
        GrievanceTicket.CATEGORY_DEDUPLICATION: {
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
        cls.verify_required_arguments(input, "category", cls.CATEGORY_OPTIONS)
        if arg("issue_type"):
            cls.verify_required_arguments(input, "issue_type", cls.ISSUE_TYPE_OPTIONS)
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
        cls._remove_parsed_data_fields(input, ("linked_tickets", "extras", "business_area", "assigned_to"))
        business_area = get_object_or_404(BusinessArea, slug=business_area_slug)
        assigned_to = get_object_or_404(get_user_model(), id=assigned_to_id)
        grievance_ticket = GrievanceTicket.objects.create(
            **input,
            business_area=business_area,
            created_by=user,
            user_modified=timezone.now(),
            assigned_to=assigned_to,
            status=GrievanceTicket.STATUS_ASSIGNED,
        )
        grievance_ticket.linked_tickets.set(linked_tickets)
        return grievance_ticket, extras

    @staticmethod
    def verify_required_arguments(input_data, field_name, options):
        for key, value in options.items():
            if key != input_data.get(field_name):
                continue
            for required in value.get("required"):
                if nested_dict_get(input_data, required) is None:
                    raise GraphQLError(f"You have to provide {required} in {key}")
            for not_allowed in value.get("not_allowed"):
                if nested_dict_get(input_data, not_allowed) is not None:
                    raise GraphQLError(f"You can't provide {not_allowed} in {key}")

    @staticmethod
    def _remove_parsed_data_fields(data_dict, fields_list):
        for field in fields_list:
            data_dict.pop(field, None)


POSSIBLE_STATUS_FLOW = {
    GrievanceTicket.STATUS_NEW: (GrievanceTicket.STATUS_ASSIGNED,),
    GrievanceTicket.STATUS_ASSIGNED: (GrievanceTicket.STATUS_IN_PROGRESS,),
    GrievanceTicket.STATUS_IN_PROGRESS: (GrievanceTicket.STATUS_ON_HOLD, GrievanceTicket.STATUS_FOR_APPROVAL),
    GrievanceTicket.STATUS_ON_HOLD: (GrievanceTicket.STATUS_IN_PROGRESS, GrievanceTicket.STATUS_FOR_APPROVAL),
    GrievanceTicket.STATUS_FOR_APPROVAL: (GrievanceTicket.STATUS_IN_PROGRESS, GrievanceTicket.STATUS_CLOSED),
    GrievanceTicket.STATUS_CLOSED: tuple(),
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
    GrievanceTicket.STATUS_CLOSED: tuple(),
}


class GrievanceStatusChangeMutation(graphene.Mutation):
    grievance_ticket = graphene.Field(GrievanceTicketNode)

    class Arguments:
        grievance_ticket_id = graphene.Argument(graphene.ID)
        status = graphene.Int()

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, grievance_ticket_id, status, **kwargs):
        grievance_ticket_id = decode_id_string(grievance_ticket_id)
        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        if grievance_ticket.status == status:
            return cls(grievance_ticket)
        status_flow = POSSIBLE_STATUS_FLOW
        if grievance_ticket.category in (
            GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
            GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        ):
            status_flow = POSSIBLE_FEEDBACK_STATUS_FLOW
        if status not in status_flow[grievance_ticket.status]:
            raise GraphQLError("New status is incorrect")
        grievance_ticket.status = status
        grievance_ticket.save()
        grievance_ticket.refresh_from_db()
        return cls(grievance_ticket=grievance_ticket)


class CreateTicketNoteMutation(graphene.Mutation):
    grievance_ticket_note = graphene.Field(TicketNoteNode)

    class Arguments:
        note_input = CreateTicketNoteInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, note_input, **kwargs):
        grievance_ticket_id = decode_id_string(note_input["ticket"])
        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        description = note_input["description"]
        created_by = info.context.user

        ticket_note = TicketNote.objects.create(ticket=grievance_ticket, description=description, created_by=created_by)

        return cls(grievance_ticket_note=ticket_note)


class IndividualDataChangeApproveMutation(DataChangeValidator, graphene.Mutation):
    grievance_ticket = graphene.Field(GrievanceTicketNode)

    class Arguments:
        grievance_ticket_id = graphene.Argument(graphene.ID, required=True)
        """
        individual_approve_data have to be a dictionary with field name as key and boolean as a value,
        indicating whether field change is approved or not.
        """
        individual_approve_data = graphene.JSONString()

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, grievance_ticket_id, individual_approve_data, **kwargs):
        grievance_ticket_id = decode_id_string(grievance_ticket_id)
        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        cls.verify_approve_data(individual_approve_data)
        individual_approve_data = {to_snake_case(key): value for key, value in individual_approve_data.items()}
        individual_data_details = grievance_ticket.individual_data_update_ticket_details
        individual_data = individual_data_details.individual_data
        cls.verify_approve_data_against_object_data(individual_data, individual_approve_data)
        for field_name, item in individual_data.items():
            if individual_approve_data.get(field_name):
                individual_data[field_name]["approve_status"] = True
            else:
                individual_data[field_name]["approve_status"] = False

        individual_data_details.individual_data = individual_data
        individual_data_details.save()
        grievance_ticket.refresh_from_db()

        return cls(grievance_ticket=grievance_ticket)


class HouseholdDataChangeApproveMutation(DataChangeValidator, graphene.Mutation):
    grievance_ticket = graphene.Field(GrievanceTicketNode)

    class Arguments:
        grievance_ticket_id = graphene.Argument(graphene.ID, required=True)
        """
        household_approve_data have to be a dictionary with field name as key and boolean as a value,
        indicating whether field change is approved or not.
        """
        household_approve_data = graphene.JSONString()

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, grievance_ticket_id, household_approve_data, **kwargs):
        grievance_ticket_id = decode_id_string(grievance_ticket_id)
        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        cls.verify_approve_data(household_approve_data)
        household_approve_data = {to_snake_case(key): value for key, value in household_approve_data.items()}
        household_data_details = grievance_ticket.household_data_update_ticket_details
        household_data = household_data_details.household_data
        cls.verify_approve_data_against_object_data(household_data, household_approve_data)

        for field_name, item in household_data.items():
            if household_approve_data.get(field_name):
                household_data[field_name]["approve_status"] = True
            else:
                household_data[field_name]["approve_status"] = False

        household_data_details.household_data = household_data
        household_data_details.save()
        grievance_ticket.refresh_from_db()

        return cls(grievance_ticket=grievance_ticket)


class AddIndividualApproveMutation(graphene.Mutation):
    grievance_ticket = graphene.Field(GrievanceTicketNode)

    class Arguments:
        grievance_ticket_id = graphene.Argument(graphene.ID, required=True)
        approve_status = graphene.Boolean(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, grievance_ticket_id, approve_status, **kwargs):
        grievance_ticket_id = decode_id_string(grievance_ticket_id)
        grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket_id)
        individual_details = grievance_ticket.add_individual_ticket_details
        individual_details.approve_status = approve_status
        individual_details.save()
        grievance_ticket.refresh_from_db()

        return cls(grievance_ticket=grievance_ticket)


class Mutations(graphene.ObjectType):
    create_grievance_ticket = CreateGrievanceTicketMutation.Field()
    grievance_status_change = GrievanceStatusChangeMutation.Field()
    create_ticket_note = CreateTicketNoteMutation.Field()
    approve_individual_data_change = IndividualDataChangeApproveMutation.Field()
    approve_household_data_change = HouseholdDataChangeApproveMutation.Field()
    approve_add_individual = AddIndividualApproveMutation.Field()
