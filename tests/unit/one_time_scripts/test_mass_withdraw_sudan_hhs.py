from django.test import TestCase

from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketIndividualDataUpdateDetails,
)
from hct_mis_api.apps.household.models import Document
from hct_mis_api.one_time_scripts.mass_withdraw_sudan_hhs import mass_withdraw_sudan_hhs
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.grievance import GrievanceTicketFactory
from tests.extras.test_utils.factories.household import (
    DocumentFactory,
    create_household_and_individuals,
)
from tests.extras.test_utils.factories.program import ProgramFactory


class TestMassWithdrawSudanHhs(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        business_area = create_afghanistan()
        cls.program = ProgramFactory(business_area=business_area)
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "business_area": business_area,
                "program": cls.program,
                "unicef_id": "HH-20-0192.6628",
            },
            individuals_data=[{}],
        )
        cls.document = DocumentFactory(
            individual=cls.individuals[0],
            program=cls.program,
        )

        cls.grievance_ticket = GrievanceTicketFactory(status=GrievanceTicket.STATUS_IN_PROGRESS)
        cls.ticket_complaint_details = TicketComplaintDetails.objects.create(
            ticket=cls.grievance_ticket,
            household=cls.household,
        )
        cls.grievance_ticket2 = GrievanceTicketFactory(status=GrievanceTicket.STATUS_IN_PROGRESS)
        cls.ticket_individual_data_update = TicketIndividualDataUpdateDetails.objects.create(
            ticket=cls.grievance_ticket2,
            individual=cls.individuals[0],
        )

    def test_mass_withdraw_sudan_hhs(self) -> None:
        mass_withdraw_sudan_hhs()

        self.household.refresh_from_db()
        self.individuals[0].refresh_from_db()
        self.document.refresh_from_db()
        self.grievance_ticket.refresh_from_db()
        self.grievance_ticket2.refresh_from_db()

        self.assertEqual(
            self.household.withdrawn,
            True,
        )
        self.assertEqual(
            self.household.internal_data["withdrawn_tag"],
            "Received Full entitlements",
        )
        self.assertEqual(
            self.individuals[0].withdrawn,
            True,
        )
        self.assertEqual(
            self.document.status,
            Document.STATUS_INVALID,
        )
        self.assertEqual(
            self.grievance_ticket.status,
            GrievanceTicket.STATUS_CLOSED,
        )
        self.assertEqual(
            self.grievance_ticket2.status,
            GrievanceTicket.STATUS_CLOSED,
        )
