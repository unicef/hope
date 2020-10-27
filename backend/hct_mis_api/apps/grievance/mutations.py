import graphene
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from graphql import GraphQLError

from account.schema import UserNode
from core.models import BusinessArea
from core.permissions import is_authenticated
from core.utils import nested_dict_get
from grievance.models import GrievanceTicket
from grievance.schema import GrievanceTicketNode


class CreateGrievanceTicketExtrasInput(graphene.InputObjectType):
    pass


class CreateGrievanceTicketInput(graphene.InputObjectType):
    description = graphene.String(required=True)
    assigned_to = graphene.GlobalID(node=UserNode, required=True)
    category = graphene.Int(required=True)
    issue_type = graphene.Int(required=True)
    admin = graphene.String()
    area = graphene.String()
    language = graphene.String(required=True)
    consent = graphene.Boolean(required=True)
    business_area = graphene.String(required=True)
    linked_tickets = graphene.List(graphene.GlobalID(node=GrievanceTicketNode))
    extras = CreateGrievanceTicketExtrasInput()


class CreateGrievanceTicketMutation(graphene.Mutation):
    grievance_tickets = graphene.List(GrievanceTicketNode)

    CATEGORY_OPTIONS = {
        GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK: {
            "required": [],
            "not_allowed": ["extras"],
        },
    }

    # (CATEGORY_PAYMENT_VERIFICATION, _("Payment Verification")),
    # (CATEGORY_DATA_CHANGE, _("Data Change")),
    # (CATEGORY_SENSITIVE_GRIEVANCE, _("Sensitive Grievance")),
    # (CATEGORY_GRIEVANCE_COMPLAINT, _("Grievance Complaint")),
    # (CATEGORY_NEGATIVE_FEEDBACK, _("Negative Feedback")),
    # (CATEGORY_REFERRAL, _("Referral")),
    # (CATEGORY_POSITIVE_FEEDBACK, _("Positive Feedback")),
    # (CATEGORY_DEDUPLICATION, _("Deduplication")),

    class Arguments:
        input = CreateGrievanceTicketInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input, **kwargs):
        arg = lambda name, default=None: input.get(name, default)
        cls.verify_required_arguments(input, "category", cls.CATEGORY_OPTIONS)
        category = arg("category")
        (grievance_ticket, extras) = cls.save_basic_data(root, info, input, **kwargs)
        save_extra_methods = {GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION: cls.save_payment_verification_extras}
        save_extra_method = save_extra_methods.get(category)
        grievances = [grievance_ticket]
        if save_extra_method:
            grievances = save_extra_method(cls, root, info, input, grievance_ticket, extras, **kwargs)
        return cls(grievance_tickets=grievances)

    @classmethod
    def save_basic_data(cls, root, info, input, **kwargs):
        arg = lambda name, default=None: input.get(name, default)
        user = info.context.user
        linked_tickets = arg("linked_tickets", [])
        business_area_slug = arg("business_area")
        extras = arg("extras")
        del input["linked_tickets"]
        del input["business_area"]
        del input["extras"]
        business_area = get_object_or_404(BusinessArea, slug=business_area_slug)
        grievance_ticket = GrievanceTicket(
            **input, business_area=business_area, created_by=user, user_modified=timezone.now()
        )
        grievance_ticket.linked_tickets.set(linked_tickets)
        return grievance_ticket, extras

    @classmethod
    def save_payment_verification_extras(cls, root, info, input, grievance_ticket, extras, **kwargs):
        pass

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


class Mutations(graphene.ObjectType):
    create_grievance_ticket = CreateGrievanceTicketMutation.Field()
