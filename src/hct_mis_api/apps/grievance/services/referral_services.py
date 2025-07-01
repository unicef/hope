from typing import Dict, List, Optional, Tuple

from hct_mis_api.apps.grievance.models import GrievanceTicket, TicketReferralDetails
from hct_mis_api.apps.household.models import Household, Individual


def save_referral_service(grievance_ticket: GrievanceTicket, extras: Dict) -> List[GrievanceTicket]:
    household, individual = fetch_household_and_individual(extras)

    create_new_ticket(grievance_ticket, household, individual)
    grievance_ticket.refresh_from_db()
    return [grievance_ticket]


def create_new_ticket(
    grievance_ticket: GrievanceTicket, household: Optional[Household], individual: Optional[Individual]
) -> GrievanceTicket:
    TicketReferralDetails.objects.create(
        individual=individual,
        household=household,
        ticket=grievance_ticket,
    )
    grievance_ticket.refresh_from_db()
    return grievance_ticket


def update_referral_service(grievance_ticket: GrievanceTicket, extras: Dict, input_data: Dict) -> GrievanceTicket:
    household, individual = fetch_household_and_individual(extras)

    ticket_details = grievance_ticket.referral_ticket_details
    if individual:
        ticket_details.individual = individual
    if household:
        ticket_details.household = household
    ticket_details.save()
    grievance_ticket.refresh_from_db()
    return grievance_ticket


def fetch_household_and_individual(extras: Dict) -> Tuple[Optional[Household], Optional[Individual]]:
    category_extras = extras.get("category", {})
    feedback_ticket_extras = category_extras.get("referral_ticket_extras", {})
    individual = feedback_ticket_extras.get("individual")
    household = feedback_ticket_extras.get("household")
    return household, individual


def update_ticket(
    grievance_ticket: GrievanceTicket, household: Optional[Household], individual: Optional[Individual]
) -> None:
    ticket_details = grievance_ticket.referral_ticket_details
    if individual:
        ticket_details.individual = individual
    if household:
        ticket_details.household = household
    ticket_details.save()
