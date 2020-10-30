import graphene


class GrievanceComplaintTicketExtras(graphene.InputObjectType):
    household = graphene.ID()
    individual = graphene.ID()
    payment_record = graphene.ID()


def save_grievance_complaint_extras(root, info, input, grievance_ticket, extras, **kwargs):
    pass
