from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketReferralDetails,
    TicketSensitiveDetails,
)
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.one_time_scripts.assign_program_to_grievance_tickets import (
    assign_program_to_grievance_tickets,
)


class TestAssignProgramToGrievanceTickets(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        GrievanceTicket.objects.all().delete()
        business_area = create_afghanistan()
        cls.program = ProgramFactory(business_area=business_area)
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "business_area": business_area,
                "program": cls.program,
            },
            individuals_data=[{}],
        )

        cls.ticket_complaint_details = TicketComplaintDetails.objects.create(
            ticket=GrievanceTicketFactory(),
            household=cls.household,
            individual=cls.individuals[0],
        )
        cls.ticket_complaint_details_household_only = TicketComplaintDetails.objects.create(
            ticket=GrievanceTicketFactory(),
            household=cls.household,
        )
        cls.ticket_complaint_details_individual_only = TicketComplaintDetails.objects.create(
            ticket=GrievanceTicketFactory(),
            individual=cls.individuals[0],
        )

        cls.ticket_sensitive_details_individual_only = TicketSensitiveDetails.objects.create(
            ticket=GrievanceTicketFactory(),
            individual=cls.individuals[0],
        )
        cls.ticket_sensitive_details_household_only = TicketSensitiveDetails.objects.create(
            ticket=GrievanceTicketFactory(),
            household=cls.household,
        )

        cls.ticket_household_data_update_details = TicketHouseholdDataUpdateDetails.objects.create(
            ticket=GrievanceTicketFactory(),
            household=cls.household,
        )

        cls.ticket_add_individual_details = TicketAddIndividualDetails.objects.create(
            ticket=GrievanceTicketFactory(),
            household=cls.household,
        )

        cls.ticket_delete_household_ticket_details = TicketDeleteHouseholdDetails.objects.create(
            ticket=GrievanceTicketFactory(),
            household=cls.household,
        )

        cls.ticket_individual_data_update_ticket_details = TicketIndividualDataUpdateDetails.objects.create(
            ticket=GrievanceTicketFactory(),
            individual=cls.individuals[0],
        )

        cls.ticket_delete_individual_ticket_details = TicketDeleteIndividualDetails.objects.create(
            ticket=GrievanceTicketFactory(),
            individual=cls.individuals[0],
        )

        cls.ticket_referral_details_household = TicketReferralDetails.objects.create(
            ticket=GrievanceTicketFactory(),
            household=cls.household,
        )

        cls.ticket_referral_details_individual = TicketReferralDetails.objects.create(
            ticket=GrievanceTicketFactory(),
            individual=cls.individuals[0],
        )

        cls.ticket_complaint_details_no_program = TicketComplaintDetails.objects.create(
            ticket=GrievanceTicketFactory(),
        )

    def test_fill_empty_programs(self) -> None:
        assign_program_to_grievance_tickets()

        self.assertEqual(self.ticket_complaint_details.ticket.programs.first(), self.program)
        self.assertEqual(self.ticket_complaint_details_household_only.ticket.programs.first(), self.program)
        self.assertEqual(self.ticket_complaint_details_individual_only.ticket.programs.first(), self.program)
        self.assertEqual(self.ticket_sensitive_details_individual_only.ticket.programs.first(), self.program)
        self.assertEqual(self.ticket_sensitive_details_household_only.ticket.programs.first(), self.program)
        self.assertEqual(self.ticket_household_data_update_details.ticket.programs.first(), self.program)
        self.assertEqual(self.ticket_add_individual_details.ticket.programs.first(), self.program)
        self.assertEqual(self.ticket_delete_household_ticket_details.ticket.programs.first(), self.program)
        self.assertEqual(self.ticket_individual_data_update_ticket_details.ticket.programs.first(), self.program)
        self.assertEqual(self.ticket_delete_individual_ticket_details.ticket.programs.first(), self.program)
        self.assertEqual(self.ticket_referral_details_household.ticket.programs.first(), self.program)
        self.assertEqual(self.ticket_referral_details_individual.ticket.programs.first(), self.program)

        self.assertEqual(self.ticket_complaint_details_no_program.ticket.programs.count(), 0)
