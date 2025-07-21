from tests.extras.test_utils.factories.account import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketSystemFlaggingDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.services.system_ticket_service import (
    close_system_flagging_ticket_service,
)
from tests.extras.test_utils.factories.household import create_household
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.sanction_list.fixtures import SanctionListIndividualFactory


class TestSystemTickets(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
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

    def test_close_system_flagging_ticket_with_approve_status(self) -> None:
        ticket_details = TicketSystemFlaggingDetailsFactory(
            ticket=self.grievance_ticket,
            golden_records_individual=self.individual,
            sanction_list_individual=self.sanction_list_individual,
            approve_status=True,
        )

        close_system_flagging_ticket_service(ticket_details.ticket, self.user)
        individual = Individual.objects.get(pk=self.individual.pk)
        self.assertTrue(individual.sanction_list_confirmed_match)

    def test_close_system_flagging_ticket_without_approve_status(self) -> None:
        ticket_details = TicketSystemFlaggingDetailsFactory(
            ticket=self.grievance_ticket,
            golden_records_individual=self.individual,
            sanction_list_individual=self.sanction_list_individual,
            approve_status=False,
        )

        close_system_flagging_ticket_service(ticket_details.ticket, self.user)
        individual = Individual.objects.get(pk=self.individual.pk)
        self.assertFalse(individual.sanction_list_confirmed_match)
