import graphene
from django.shortcuts import get_object_or_404

from core.utils import decode_id_string
from grievance.models import GrievanceTicket, TicketIndividualDataUpdateDetails
from household.models import Individual
from household.schema import HouseholdNode, IndividualNode


class IndividualUpdateDataObjectType(graphene.InputObjectType):
    status = graphene.String()
    full_name = graphene.String()
    given_name = graphene.String()
    middle_name = graphene.String()
    family_name = graphene.String()
    sex = graphene.String()
    birth_date = graphene.Date()
    estimated_birth_date = graphene.Boolean()
    marital_status = graphene.String()
    phone_no = graphene.String()
    phone_no_alternative = graphene.String()
    relationship = graphene.String()
    disability = graphene.Boolean()
    work_status = graphene.String()
    enrolled_in_nutrition_programme = graphene.Boolean()
    administration_of_rutf = graphene.Boolean()
    pregnant = graphene.Boolean()
    observed_disability = graphene.List(graphene.String)
    seeing_disability = graphene.String()
    hearing_disability = graphene.String()
    physical_disability = graphene.String()
    memory_disability = graphene.String()
    selfcare_disability = graphene.String()
    comms_disability = graphene.String()
    who_answers_phone = graphene.String()
    who_answers_alt_phone = graphene.String()


class HouseholdDataUpdateIssueTypeExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=True)
    individual = graphene.GlobalID(node=IndividualNode)


class IndividualDataUpdateIssueTypeExtras(graphene.InputObjectType):
    individual = graphene.GlobalID(node=IndividualNode, required=True)
    individual_data = IndividualUpdateDataObjectType(required=True)


class IndividualDeleteIssueTypeExtras(graphene.InputObjectType):
    individual = graphene.GlobalID(node=IndividualNode, required=True)
    household = graphene.GlobalID(node=HouseholdNode)


class AddIndividualIssueTypeExtras(graphene.InputObjectType):
    pass


def save_data_change_extras(root, info, input, grievance_ticket, extras, **kwargs):
    issue_type = input.get("issue_type")
    if issue_type == GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE:
        return save_individual_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs)


def save_individual_data_update_extras(root, info, input, grievance_ticket, extras, **kwargs):
    data_change_extras = extras.get("issue_type")
    individual_data_update_issue_type_extras = data_change_extras.get("individual_data_update_issue_type_extras")

    individual_encoded_id = individual_data_update_issue_type_extras.get("individual")
    individual_id = decode_id_string(individual_encoded_id)
    individual = get_object_or_404(Individual, id=individual_id)
    individual_data = individual_data_update_issue_type_extras.get("individual_data")
    ticket_individual_data_update_details = TicketIndividualDataUpdateDetails(
        individual_data=individual_data,
        individual=individual,
        ticket=grievance_ticket,
    )
    ticket_individual_data_update_details.save()
    grievance_ticket.refresh_from_db()
    return [grievance_ticket]


def save_individual_delete_extras(root, info, input, grievance_ticket, extras, **kwargs):
    pass


def save_add_individual_extras(root, info, input, grievance_ticket, extras, **kwargs):
    pass
