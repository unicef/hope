import graphene
from django.db import transaction
from graphql import GraphQLError

from core.permissions import is_authenticated
from grievance.models import GrievanceTicket
from grievance.schema import GrievanceTicketNode


class CreateGrievanceTicketInput(graphene.InputObjectType):
    pass


class CreateGrievanceTicketMutation(graphene.Mutation):
    cash_plan = graphene.Field(GrievanceTicketNode)

    class Arguments:
        input = CreateGrievanceTicketInput(required=True)

    @staticmethod
    def verify_required_arguments(input_data, field_name):
        options = {
            GrievanceTicket.CATEGORY_DATA_CHANGE: {
                "required": [],
                "not_allowed": [],
            },
        }

        for key, value in options.items():
            if key != input_data.get(field_name):
                continue
            for required in value.get("required"):
                if input_data.get(required) is None:
                    raise GraphQLError(f"You have to provide {required} in {key}")
            for not_allowed in value.get("not_allowed"):
                if input_data.get(not_allowed) is not None:
                    raise GraphQLError(f"You can't provide {not_allowed} in {key}")

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input_data, **kwargs):
        arg = lambda name: input.get(name)
        cls.verify_required_arguments(input_data, "type")


class Mutations(graphene.ObjectType):
    create_grievance_ticket = CreateGrievanceTicketMutation.Field()
