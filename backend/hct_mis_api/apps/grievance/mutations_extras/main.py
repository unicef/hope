import graphene

from grievance.mutations_extras.data_change import (
    HouseholdDataUpdateIssueTypeExtras,
    IndividualDataUpdateIssueTypeExtras,
    IndividualDeleteIssueTypeExtras,
    AddIndividualIssueTypeExtras,
)
from grievance.mutations_extras.grievance_complaint import GrievanceComplaintTicketExtras
from grievance.mutations_extras.sensitive_grievance import SensitiveGrievanceTicketExtras


class IssueTypeExtrasInput(graphene.InputObjectType):
    household_data_update_issue_type_extras = HouseholdDataUpdateIssueTypeExtras()
    individual_data_update_issue_type_extras = IndividualDataUpdateIssueTypeExtras()
    individual_delete_issue_type_extras = IndividualDeleteIssueTypeExtras()
    add_individual_issue_type_extras = AddIndividualIssueTypeExtras()


class CategoryExtrasInput(graphene.InputObjectType):
    sensitive_grievance_ticket_extras = SensitiveGrievanceTicketExtras()
    grievance_complaint_ticket_extras = GrievanceComplaintTicketExtras()


class CreateGrievanceTicketExtrasInput(graphene.InputObjectType):
    category = CategoryExtrasInput()
    issue_type = IssueTypeExtrasInput()


# TODO: Remove it when all methods for closing tickets are implemented
def _not_implemented_close_method(*args, **kwargs):
    raise NotImplementedError

def _no_operation_close_method(*args, **kwargs):
    pass
