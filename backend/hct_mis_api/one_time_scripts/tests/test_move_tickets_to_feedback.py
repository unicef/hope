from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.accountability.models import Feedback, FeedbackMessage
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    NegativeFeedbackTicketWithoutExtrasFactory,
    PositiveFeedbackTicketWithoutExtrasFactory,
    TicketNoteFactory,
)
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNegativeFeedbackDetails,
    TicketPositiveFeedbackDetails,
)
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.one_time_scripts.move_tickets_to_feedback import (
    move_tickets_to_feedback,
)


class TestMigrationFosterChild(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()

        cls.business_area = BusinessArea.objects.first()
        cls.user = UserFactory()

        cls.program_1 = ProgramFactory()
        cls.program_2 = ProgramFactory()

        cls.admin2_1 = AreaFactory()
        cls.admin2_2 = AreaFactory()

        cls.individual_1 = IndividualFactory(household=None)
        cls.household_1 = HouseholdFactory(head_of_household=cls.individual_1)

        cls.individual_2 = IndividualFactory(household=None)
        cls.household_2 = HouseholdFactory(head_of_household=cls.individual_2)

        cls.ticket_1 = GrievanceTicketFactory(description="grievance_ticket_1_description", programme=cls.program_1)
        cls.ticket_positive_1 = PositiveFeedbackTicketWithoutExtrasFactory(ticket=cls.ticket_1)

        cls.ticket_note_1 = TicketNoteFactory(ticket=cls.ticket_1, description="test ticket note")

        cls.ticket_2 = GrievanceTicketFactory(language="grievance_ticket_2_language")
        cls.ticket_positive_2 = PositiveFeedbackTicketWithoutExtrasFactory(
            ticket=cls.ticket_2, household=cls.household_1
        )

        cls.ticket_3 = GrievanceTicketFactory(programme=cls.program_2, consent=False)
        cls.ticket_positive_3 = PositiveFeedbackTicketWithoutExtrasFactory(
            ticket=cls.ticket_3, household=cls.household_1, individual=cls.individual_1
        )

        cls.ticket_4 = GrievanceTicketFactory(comments="grievance_ticket_4_comments", admin2=cls.admin2_1)
        cls.ticket_negative_1 = NegativeFeedbackTicketWithoutExtrasFactory(ticket=cls.ticket_4)

        cls.ticket_5 = GrievanceTicketFactory(area="grievance_ticket_5_area")
        cls.ticket_negative_2 = NegativeFeedbackTicketWithoutExtrasFactory(
            ticket=cls.ticket_5, household=cls.household_2
        )

        cls.ticket_6 = GrievanceTicketFactory(admin2=cls.admin2_2, consent=True)
        cls.ticket_negative_3 = NegativeFeedbackTicketWithoutExtrasFactory(
            ticket=cls.ticket_6, household=cls.household_2, individual=cls.individual_2
        )

        cls.ticket_1_created_at = cls.ticket_positive_1.created_at
        cls.ticket_2_created_at = cls.ticket_positive_2.created_at
        cls.ticket_3_created_at = cls.ticket_positive_3.created_at
        cls.ticket_4_created_at = cls.ticket_negative_1.created_at
        cls.ticket_5_created_at = cls.ticket_negative_2.created_at
        cls.ticket_6_created_at = cls.ticket_negative_3.created_at

    def test_ticket_migration(self) -> None:
        self.assertEqual(TicketPositiveFeedbackDetails.objects.count(), 3)
        self.assertEqual(TicketNegativeFeedbackDetails.objects.count(), 3)
        self.assertEqual(GrievanceTicket.objects.count(), 6)
        self.assertEqual(Feedback.objects.count(), 0)

        move_tickets_to_feedback()

        self.assertEqual(TicketPositiveFeedbackDetails.objects.count(), 0)
        self.assertEqual(TicketNegativeFeedbackDetails.objects.count(), 0)
        self.assertEqual(GrievanceTicket.objects.count(), 0)
        self.assertEqual(Feedback.objects.count(), 6)

        feedbacks = Feedback.objects.all()

        # General values

        self.assertEqual(feedbacks[0].issue_type, Feedback.POSITIVE_FEEDBACK)
        self.assertEqual(feedbacks[1].issue_type, Feedback.POSITIVE_FEEDBACK)
        self.assertEqual(feedbacks[2].issue_type, Feedback.POSITIVE_FEEDBACK)
        self.assertEqual(feedbacks[3].issue_type, Feedback.NEGATIVE_FEEDBACK)
        self.assertEqual(feedbacks[4].issue_type, Feedback.NEGATIVE_FEEDBACK)
        self.assertEqual(feedbacks[5].issue_type, Feedback.NEGATIVE_FEEDBACK)

        self.assertEqual(feedbacks[0].created_at, self.ticket_1_created_at)
        self.assertEqual(feedbacks[1].created_at, self.ticket_2_created_at)
        self.assertEqual(feedbacks[2].created_at, self.ticket_3_created_at)
        self.assertEqual(feedbacks[3].created_at, self.ticket_4_created_at)
        self.assertEqual(feedbacks[4].created_at, self.ticket_5_created_at)
        self.assertEqual(feedbacks[5].created_at, self.ticket_6_created_at)

        # Specific values

        self.assertEqual(feedbacks[0].description, "grievance_ticket_1_description")
        self.assertEqual(feedbacks[0].program, self.program_1)
        self.assertEqual(FeedbackMessage.objects.count(), 1)

        self.assertEqual(feedbacks[1].language, "grievance_ticket_2_language")
        self.assertEqual(feedbacks[1].household_lookup, self.household_1)

        self.assertIs(feedbacks[2].consent, False)
        self.assertEqual(feedbacks[2].program, self.program_2)
        self.assertEqual(feedbacks[2].household_lookup, self.household_1)
        self.assertEqual(feedbacks[2].individual_lookup, self.individual_1)

        self.assertEqual(feedbacks[3].comments, "grievance_ticket_4_comments")
        self.assertEqual(feedbacks[3].admin2, self.admin2_1)

        self.assertEqual(feedbacks[4].area, "grievance_ticket_5_area")
        self.assertEqual(feedbacks[4].household_lookup, self.household_2)

        self.assertIs(feedbacks[5].consent, True)
        self.assertEqual(feedbacks[5].admin2, self.admin2_2)
        self.assertEqual(feedbacks[5].household_lookup, self.household_2)
        self.assertEqual(feedbacks[5].individual_lookup, self.individual_2)

        self.assertIs(Feedback._meta.get_field("created_at").auto_now_add, True)

        feedback_tickets_count = GrievanceTicket.objects.filter(
            category__in=[GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK, GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK]
        ).count()
        self.assertEqual(feedback_tickets_count, 0)
