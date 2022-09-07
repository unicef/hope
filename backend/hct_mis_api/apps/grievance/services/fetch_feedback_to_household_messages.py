from django.db.models import Q

from hct_mis_api.apps.grievance.models import FeedbackToHousehold, GrievanceTicket
from hct_mis_api.apps.grievance.services.sms_provider import SmsProvider


def fetch_feedback_to_household_messages(sms_provide: SmsProvider):
    for message in sms_provide.receive_messages():
        feedback = (
            FeedbackToHousehold.objects.filter(
                Q(individual__phone_no=message.number) | Q(individual__phone_no_alternative=message.number)
            )
            .filter(ticket__status=GrievanceTicket.STATUS_FOR_APPROVAL)
            .distinct()
            .first()
        )

        if feedback:
            FeedbackToHousehold.objects.create(
                ticket=feedback.ticket,
                individual=feedback.individual,
                message=message.message,
                created_by=feedback.created_by,
                kind=FeedbackToHousehold.RESPONSE,
            )
