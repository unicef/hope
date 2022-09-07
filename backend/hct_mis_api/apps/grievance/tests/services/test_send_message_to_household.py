from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.grievance.fixtures import GrievanceComplaintTicketFactory
from hct_mis_api.apps.grievance.services.send_message_to_household import (
    send_message_to_household,
)
from hct_mis_api.apps.grievance.services.sms_provider import Message, SmsProvider


class FakeSmsProvider(SmsProvider):
    def __init__(self):
        self.sent = False

    def send(self, phone_number: str, message: str):
        self.sent = True

    def receive_messages(self) -> list[Message]:
        pass


class TestSendMessageToHousehold(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_afghanistan()

    def test_send_message_to_household(self):
        complaint_ticket = GrievanceComplaintTicketFactory()
        grievance_ticket = complaint_ticket.ticket
        message = "test"
        created_by = UserFactory()
        sms_provide = FakeSmsProvider()

        feedback_to_household = send_message_to_household(grievance_ticket, message, created_by, sms_provide)

        self.assertEqual(feedback_to_household.message, message)
        self.assertEqual(feedback_to_household.ticket, grievance_ticket)
        self.assertTrue(sms_provide.sent)
