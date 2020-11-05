import graphene
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from graphql import GraphQLError

from account.schema import UserNode
from core.models import BusinessArea
from core.permissions import is_authenticated
from core.schema import BusinessAreaNode
from core.utils import nested_dict_get, decode_id_string
from grievance.mutations_extras.data_change import save_data_change_extras
from grievance.mutations_extras.main import CreateGrievanceTicketExtrasInput
from grievance.models import GrievanceTicket
from grievance.mutations_extras.payment_verification import save_payment_verification_extras
from grievance.schema import GrievanceTicketNode


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
            "required": ['extras.issue_type.add_individual_issue_type_extras'],
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
        linked_tickets = arg("linked_tickets", [])
        business_area_slug = arg("business_area")
        extras = arg("extras")
        cls._remove_parsed_data_fields(input, ("linked_tickets", "extras", "business_area", "assigned_to"))
        business_area = get_object_or_404(BusinessArea, slug=business_area_slug)
        assigned_to = get_object_or_404(get_user_model(), id=assigned_to_id)
        grievance_ticket = GrievanceTicket.objects.create(
            **input,
            business_area=business_area,
            created_by=user,
            user_modified=timezone.now(),
            assigned_to=assigned_to,
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


class Mutations(graphene.ObjectType):
    create_grievance_ticket = CreateGrievanceTicketMutation.Field()
