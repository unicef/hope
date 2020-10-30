import graphene


class HouseholdDataUpdateIssueTypeExtras(graphene.InputObjectType):
    household = graphene.ID(required=True)
    individual = graphene.ID()


class IndividualDataUpdateIssueTypeExtras(graphene.InputObjectType):
    individual = graphene.ID(required=True)
    household = graphene.ID()


class IndividualDeleteIssueTypeExtras(graphene.InputObjectType):
    individual = graphene.ID(required=True)
    household = graphene.ID()


class AddIndividualIssueTypeExtras(graphene.InputObjectType):
    pass


def save_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs):
    pass


def save_individual_delete_extras(root, info, input, grievance_ticket, extras, **kwargs):
    pass


def save_add_individual_extras(root, info, input, grievance_ticket, extras, **kwargs):
    pass
