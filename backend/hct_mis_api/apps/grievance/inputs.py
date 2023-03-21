import graphene

from hct_mis_api.apps.account.schema import UserNode
from hct_mis_api.apps.core.schema import BusinessAreaNode
from hct_mis_api.apps.grievance.mutations_extras.main import (
    CreateGrievanceTicketExtrasInput,
    UpdateGrievanceTicketExtrasInput,
)
from hct_mis_api.apps.grievance.schema import GrievanceTicketNode
from hct_mis_api.apps.household.schema import HouseholdNode, IndividualNode


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
    household = graphene.GlobalID(node=HouseholdNode, required=False)
    individual = graphene.GlobalID(node=IndividualNode, required=False)
    extras = UpdateGrievanceTicketExtrasInput()


class CreateTicketNoteInput(graphene.InputObjectType):
    description = graphene.String(required=True)
    ticket = graphene.GlobalID(node=GrievanceTicketNode, required=True)
