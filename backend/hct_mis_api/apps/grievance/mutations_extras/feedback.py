from typing import List, Optional, Tuple
import graphene
from backend.hct_mis_api.apps.grievance.models import GrievanceTicket

from hct_mis_api.apps.core.utils import decode_and_get_object
from hct_mis_api.apps.grievance.models import (
    TicketNegativeFeedbackDetails,
    TicketPositiveFeedbackDetails,
)
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.household.schema import HouseholdNode, IndividualNode


class PositiveFeedbackTicketExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=False)
    individual = graphene.GlobalID(node=IndividualNode, required=False)


class NegativeFeedbackTicketExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=False)
    individual = graphene.GlobalID(node=IndividualNode, required=False)


def save_positive_feedback_extras(root, info, input, grievance_ticket, extras, **kwargs) -> List[GrievanceTicket]:
    household, individual = fetch_household_and_individual(extras, "positive_feedback_ticket_extras")
    create_new_positive_feedback_ticket(grievance_ticket, household, individual)
    grievance_ticket.refresh_from_db()
    return [grievance_ticket]


def update_positive_feedback_extras(root, info, input, grievance_ticket, extras, **kwargs) -> GrievanceTicket:
    household, individual = fetch_household_and_individual(extras, "positive_feedback_ticket_extras")

    update_ticket(grievance_ticket.positive_feedback_ticket_details, household, individual)
    grievance_ticket.refresh_from_db()
    return grievance_ticket


def save_negative_feedback_extras(root, info, input, grievance_ticket, extras, **kwargs) -> List[GrievanceTicket]:
    household, individual = fetch_household_and_individual(extras, "negative_feedback_ticket_extras")

    create_new_negative_feedback_ticket(grievance_ticket, household, individual)
    grievance_ticket.refresh_from_db()
    return [grievance_ticket]


def update_negative_feedback_extras(root, info, input, grievance_ticket, extras, **kwargs) -> GrievanceTicket:
    household, individual = fetch_household_and_individual(extras, "negative_feedback_ticket_extras")

    update_ticket(grievance_ticket.negative_feedback_ticket_details, household, individual)
    grievance_ticket.refresh_from_db()
    return grievance_ticket


def fetch_household_and_individual(extras, ticket_type) -> Tuple[Optional[Household], Optional[Individual]]:
    category_extras = extras.get("category", {})
    feedback_ticket_extras = category_extras.get(ticket_type, {})
    individual_encoded_id = feedback_ticket_extras.get("individual")
    individual = decode_and_get_object(individual_encoded_id, Individual, False)
    household_encoded_id = feedback_ticket_extras.get("household")
    household = decode_and_get_object(household_encoded_id, Household, False)
    return household, individual


def create_new_positive_feedback_ticket(grievance_ticket, household, individual) -> None:
    TicketPositiveFeedbackDetails.objects.create(
        individual=individual,
        household=household,
        ticket=grievance_ticket,
    )


def update_ticket(ticket_details, household, individual) -> None:
    if individual:
        ticket_details.individual = individual
    if household:
        ticket_details.household = household
    ticket_details.save()


def create_new_negative_feedback_ticket(grievance_ticket, household, individual) -> None:
    TicketNegativeFeedbackDetails.objects.create(
        individual=individual,
        household=household,
        ticket=grievance_ticket,
    )
