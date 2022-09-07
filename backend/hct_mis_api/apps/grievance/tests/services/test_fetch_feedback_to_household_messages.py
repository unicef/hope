from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.grievance.fixtures import (
    FeedbackToHouseholdFactory,
    GrievanceComplaintTicketFactory,
)
from hct_mis_api.apps.grievance.models import FeedbackToHousehold, GrievanceTicket
from hct_mis_api.apps.grievance.services.fetch_feedback_to_household_messages import (
    fetch_feedback_to_household_messages,
)
from hct_mis_api.apps.grievance.services.sms_provider import Message, SmsProvider


class FakeSmsProvider(SmsProvider):
    def __init__(self):
        self._messages = [Message("+48500500500", "testing message")]

    def send(self, phone_number: str, message: str):
        pass

    def receive_messages(self) -> list[Message]:
        while len(self._messages):
            yield self._messages.pop(0)


class TestFetchFeedbackToHouseholdMessages(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_afghanistan()

    def test_fetch_feedback_to_household_messages(self):
        sms_provider = FakeSmsProvider()
        feedback_to_household = FeedbackToHouseholdFactory(
            kind=FeedbackToHousehold.MESSAGE,
        )
        grievance_ticket = feedback_to_household.ticket
        grievance_ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
        grievance_ticket.save(update_fields=("status",))
        individual = feedback_to_household.individual
        individual.phone_no = "+48500500500"
        individual.save(update_fields=("phone_no",))

        fetch_feedback_to_household_messages(sms_provider)

        self.assertEqual(FeedbackToHousehold.objects.filter(kind=FeedbackToHousehold.RESPONSE).count(), 1)
