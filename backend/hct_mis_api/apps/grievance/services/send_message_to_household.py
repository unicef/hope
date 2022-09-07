from django.contrib.auth import get_user_model

from hct_mis_api.apps.grievance.models import FeedbackToHousehold, GrievanceTicket
from hct_mis_api.apps.grievance.services.sms_provider import SmsProvider
from hct_mis_api.apps.household.models import Individual

User = get_user_model()


class InvalidPhoneNumberException(Exception):
    pass


def send_message_to_household(
    ticket: GrievanceTicket, message: str, created_by: User, sms_provider: SmsProvider
) -> FeedbackToHousehold:
    individual = ticket.ticket_details.individual
    household = ticket.ticket_details.household
    recipient: Individual = individual or household.head_of_household

    feedback_to_household = FeedbackToHousehold.objects.create(
        ticket=ticket,
        individual=recipient,
        message=message,
        created_by=created_by,
        kind=FeedbackToHousehold.MESSAGE,
    )

    phone_number = None

    if recipient.phone_no_valid:
        phone_number = str(recipient.phone_no)
    elif recipient.phone_no_alternative_valid:
        phone_number = str(recipient.phone_no_alternative)

    if not phone_number:
        raise InvalidPhoneNumberException("Invalid phone number")

    sms_provider.send(phone_number, message)

    return feedback_to_household
