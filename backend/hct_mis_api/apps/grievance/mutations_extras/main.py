import graphene

from grievance.mutations_extras.data_change import (
    HouseholdDataUpdateIssueTypeExtras,
    IndividualDataUpdateIssueTypeExtras,
    IndividualDeleteIssueTypeExtras,
)
from grievance.mutations_extras.grievance_complaint import GrievanceComplaintTicketExtras
from grievance.mutations_extras.sensitive_grievance import SensitiveGrievanceTicketExtras


class IssueTypeExtrasInput(graphene.InputObjectType):
    household_data_update_issue_type_extras = HouseholdDataUpdateIssueTypeExtras()
    individual_data_update_issue_type_extras = IndividualDataUpdateIssueTypeExtras()
    individual_delete_issue_type_extras = IndividualDeleteIssueTypeExtras()


class CategoryExtrasInput(graphene.InputObjectType):
    sensitive_grievance_ticket_extras = SensitiveGrievanceTicketExtras()
    grievance_complaint_ticket_extras = GrievanceComplaintTicketExtras()


class CreateGrievanceTicketExtrasInput(graphene.InputObjectType):
    category = CategoryExtrasInput()
    issue_type = IssueTypeExtrasInput()
