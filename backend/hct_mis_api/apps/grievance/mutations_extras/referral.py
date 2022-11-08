from typing import List, Optional, Tuple

import graphene

from hct_mis_api.apps.core.utils import decode_and_get_object
from hct_mis_api.apps.grievance.models import GrievanceTicket, TicketReferralDetails
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.household.schema import HouseholdNode, IndividualNode


class ReferralTicketExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=False)
    individual = graphene.GlobalID(node=IndividualNode, required=False)


def save_referral_extras(root, info, input, grievance_ticket, extras, **kwargs) -> List[GrievanceTicket]:
    household, individual = fetch_household_and_individual(extras)
    create_new_ticket(grievance_ticket, household, individual)
    grievance_ticket.refresh_from_db()
    return [grievance_ticket]


def update_referral_extras(root, info, input, grievance_ticket, extras, **kwargs) -> GrievanceTicket:
    household, individual = fetch_household_and_individual(extras)

    update_ticket(grievance_ticket, household, individual)
    grievance_ticket.refresh_from_db()
    return grievance_ticket


def create_new_ticket(grievance_ticket, household, individual) -> None:
    TicketReferralDetails.objects.create(
        individual=individual,
        household=household,
        ticket=grievance_ticket,
    )


def fetch_household_and_individual(extras) -> Tuple[Optional[Household], Optional[Individual]]:
    category_extras = extras.get("category", {})
    feedback_ticket_extras = category_extras.get("referral_ticket_extras", {})
    individual_encoded_id = feedback_ticket_extras.get("individual")
    individual = decode_and_get_object(individual_encoded_id, Individual, False)
    household_encoded_id = feedback_ticket_extras.get("household")
    household = decode_and_get_object(household_encoded_id, Household, False)
    return household, individual


def update_ticket(grievance_ticket, household, individual) -> None:
    ticket_details = grievance_ticket.referral_ticket_details
    if individual:
        ticket_details.individual = individual
    if household:
        ticket_details.household = household
    ticket_details.save()
