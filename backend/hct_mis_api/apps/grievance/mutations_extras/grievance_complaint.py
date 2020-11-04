import graphene

from core.utils import decode_and_get_object
from grievance.models import TicketComplaintDetails
from household.models import Household, Individual
from household.schema import HouseholdNode, IndividualNode
from payment.models import PaymentRecord
from payment.schema import PaymentRecordNode


class GrievanceComplaintTicketExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=False)
    individual = graphene.GlobalID(node=IndividualNode, required=False)
    payment_record = graphene.GlobalID(node=PaymentRecordNode, required=False)


def save_grievance_complaint_extras(root, info, input, grievance_ticket, extras, **kwargs):
    grievance_complaint_extras = extras.get("category", {})
    grievance_complaint_category_extras = grievance_complaint_extras.get("grievance_complaint_ticket_extras", {})

    individual_encoded_id = grievance_complaint_category_extras.get("individual")
    individual = decode_and_get_object(individual_encoded_id, Individual, False)

    household_encoded_id = grievance_complaint_category_extras.get("household")
    household = decode_and_get_object(household_encoded_id, Household, False)

    payment_record_encoded_id = grievance_complaint_category_extras.get("payment_record")
    payment_record = decode_and_get_object(payment_record_encoded_id, PaymentRecord, False)

    TicketComplaintDetails.objects.create(
        individual=individual, household=household, payment_record=payment_record, ticket=grievance_ticket,
    )

    grievance_ticket.refresh_from_db()

    return [grievance_ticket]
