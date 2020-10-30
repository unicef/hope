import graphene


class SensitiveGrievanceTicketExtras(graphene.InputObjectType):
    household = graphene.ID()
    individual = graphene.ID()
    payment_record = graphene.ID()


def save_sensitive_grievance_extras(root, info, input, grievance_ticket, extras, **kwargs):
    pass
