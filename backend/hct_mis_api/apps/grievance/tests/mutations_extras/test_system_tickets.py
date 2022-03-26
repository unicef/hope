from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketSystemFlaggingDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.mutations_extras.system_tickets import (
    close_system_flagging_ticket,
)
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.sanction_list.fixtures import SanctionListIndividualFactory


class TestSystemTickets(APITestCase):
    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.user = UserFactory.create()
        _, individuals = create_household({"size": 1})
        cls.individual = individuals[0]

        cls.grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
            category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        cls.sanction_list_individual = SanctionListIndividualFactory.create()

    def test_close_system_flagging_ticket_with_approve_status(self):
        ticket_details = TicketSystemFlaggingDetailsFactory(
            ticket=self.grievance_ticket,
            golden_records_individual=self.individual,
            sanction_list_individual=self.sanction_list_individual,
            approve_status=True,
        )

        close_system_flagging_ticket(ticket_details.ticket, None, False)
        individual = Individual.objects.get(pk=self.individual.pk)
        self.assertTrue(individual.sanction_list_confirmed_match)

    def test_close_system_flagging_ticket_without_approve_status(self):
        ticket_details = TicketSystemFlaggingDetailsFactory(
            ticket=self.grievance_ticket,
            golden_records_individual=self.individual,
            sanction_list_individual=self.sanction_list_individual,
            approve_status=False,
        )

        close_system_flagging_ticket(ticket_details.ticket, None, False)
        individual = Individual.objects.get(pk=self.individual.pk)
        self.assertFalse(individual.sanction_list_confirmed_match)
