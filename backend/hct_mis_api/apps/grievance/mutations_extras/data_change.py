import graphene

from household.schema import HouseholdNode, IndividualNode


class HouseholdDataUpdateIssueTypeExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=True)
    individual = graphene.GlobalID(node=IndividualNode)


class IndividualDataUpdateIssueTypeExtras(graphene.InputObjectType):
    individual = graphene.GlobalID(node=IndividualNode, required=True)
    household = graphene.GlobalID(node=HouseholdNode)


class IndividualDeleteIssueTypeExtras(graphene.InputObjectType):
    individual = graphene.GlobalID(node=IndividualNode, required=True)
    household = graphene.GlobalID(node=HouseholdNode)


class AddIndividualIssueTypeExtras(graphene.InputObjectType):
    pass


def save_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs):
    pass


def save_individual_delete_extras(root, info, input, grievance_ticket, extras, **kwargs):
    pass


def save_add_individual_extras(root, info, input, grievance_ticket, extras, **kwargs):
    pass
