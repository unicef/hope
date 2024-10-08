from django.test import TestCase

from hct_mis_api.apps.accountability.fixtures import FeedbackFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory
from hct_mis_api.apps.grievance.models import (
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
    assign_program_to_feedback,
    assign_program_to_grievance_tickets,
)


class TestAssignProgramToGrievanceTickets(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
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

        cls.program2 = ProgramFactory(business_area=business_area)
        grievance_with_program = GrievanceTicketFactory()
        grievance_with_program.programs.add(cls.program2)
        cls.ticket_complaint_details_with_program = TicketComplaintDetails.objects.create(
            ticket=grievance_with_program,
            household=cls.household,
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

        self.assertEqual(self.ticket_complaint_details_with_program.ticket.programs.first(), self.program2)
        self.assertEqual(self.ticket_complaint_details_with_program.ticket.programs.count(), 1)


class TestAssignProgramToFeedback(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        business_area = create_afghanistan()
        cls.program = ProgramFactory(business_area=business_area)
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "business_area": business_area,
                "program": cls.program,
            },
            individuals_data=[{}],
        )

        cls.feedback = FeedbackFactory(
            household_lookup=cls.household,
            individual_lookup=cls.individuals[0],
        )

        cls.feedback_individual_only = FeedbackFactory(
            individual_lookup=cls.individuals[0],
        )

        cls.feedback_household_only = FeedbackFactory(
            household_lookup=cls.household,
        )

        cls.feedback_no_program = FeedbackFactory()

        cls.program2 = ProgramFactory(business_area=business_area)
        cls.feedback_with_program = FeedbackFactory(
            program=cls.program2, household_lookup=cls.household, individual_lookup=cls.individuals[0]
        )

    def test_fill_empty_programs(self) -> None:
        assign_program_to_feedback()

        self.feedback.refresh_from_db()
        self.feedback_individual_only.refresh_from_db()
        self.feedback_household_only.refresh_from_db()
        self.feedback_no_program.refresh_from_db()
        self.feedback_with_program.refresh_from_db()

        self.assertEqual(self.feedback.program, self.program)
        self.assertEqual(self.feedback_individual_only.program, self.program)
        self.assertEqual(self.feedback_household_only.program, self.program)
        self.assertEqual(self.feedback_no_program.program, None)
        self.assertEqual(self.feedback_with_program.program, self.program2)
