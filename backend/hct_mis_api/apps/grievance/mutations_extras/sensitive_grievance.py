import graphene

from hct_mis_api.apps.core.utils import decode_and_get_object
from hct_mis_api.apps.grievance.models import TicketSensitiveDetails
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.household.schema import HouseholdNode, IndividualNode


class SensitiveGrievanceTicketExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=False)
    individual = graphene.GlobalID(node=IndividualNode, required=False)


def save_sensitive_grievance_extras(root, info, input, grievance_ticket, extras, **kwargs):
    sensitive_grievance_extras = extras.get("category", {})
    sensitive_grievance_complaint_category_extras = sensitive_grievance_extras.get(
        "sensitive_grievance_ticket_extras", {}
    )

    individual_encoded_id = sensitive_grievance_complaint_category_extras.get("individual")
    individual = decode_and_get_object(individual_encoded_id, Individual, False)

    household_encoded_id = sensitive_grievance_complaint_category_extras.get("household")
    household = decode_and_get_object(household_encoded_id, Household, False)

    TicketSensitiveDetails.objects.create(
        individual=individual,
        household=household,
        payment_record=None,
        ticket=grievance_ticket,
    )

    grievance_ticket.refresh_from_db()
    grievance_tickets_to_return = [grievance_ticket]
    grievance_ticket.refresh_from_db()

    return grievance_tickets_to_return
