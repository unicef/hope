import graphene

from household.schema import HouseholdNode, IndividualNode


class GrievanceComplaintTicketExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode)
    individual = graphene.GlobalID(node=IndividualNode)
    payment_record = graphene.GlobalID()


def save_grievance_complaint_extras(root, info, input, grievance_ticket, extras, **kwargs):
    pass
