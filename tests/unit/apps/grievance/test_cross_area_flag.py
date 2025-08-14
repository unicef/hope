from django.test import TestCase

from extras.test_utils.factories.account import BusinessAreaFactory
from extras.test_utils.factories.geo import AreaFactory
from extras.test_utils.factories.grievance import TicketNeedsAdjudicationDetailsFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory


class TestCrossAreaTickets(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        admin_area1 = AreaFactory()
        admin_area2 = AreaFactory()
        business_area = BusinessAreaFactory()
        individual1_from_area1 = IndividualFactory(business_area=business_area, household=None)
        individual2_from_area1 = IndividualFactory(business_area=business_area, household=None)
        household1_from_area1 = HouseholdFactory(
            business_area=business_area, admin2=admin_area1, head_of_household=individual1_from_area1
        )
        individual1_from_area1.household = household1_from_area1
        individual1_from_area1.save()
        household2_from_area1 = HouseholdFactory(
            business_area=business_area, admin2=admin_area1, head_of_household=individual2_from_area1
        )
        individual2_from_area1.household = household2_from_area1
        individual2_from_area1.save()

        individual_from_area2 = IndividualFactory(business_area=business_area, household=None)
        household_from_area2 = HouseholdFactory(
            business_area=business_area, admin2=admin_area2, head_of_household=individual_from_area2
        )
        individual_from_area2.household = household_from_area2
        individual_from_area2.save()

        cls.needs_adjudication_ticket_cross_area = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=individual1_from_area1,
        )
        cls.needs_adjudication_ticket_cross_area.possible_duplicates.set([individual_from_area2])

        cls.needs_adjudication_ticket_same_area = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=individual1_from_area1,
        )
        cls.needs_adjudication_ticket_same_area.possible_duplicates.set([individual2_from_area1])

        individual_without_household = IndividualFactory(business_area=business_area, household=None)
        cls.needs_adjudication_ticket_ind_no_household = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=individual_without_household,
        )
        cls.needs_adjudication_ticket_ind_no_household.possible_duplicates.set([individual_from_area2])

    def test_cross_area_field(self) -> None:
        self.needs_adjudication_ticket_cross_area.populate_cross_area_flag()
        self.needs_adjudication_ticket_cross_area.refresh_from_db()
        self.assertEqual(self.needs_adjudication_ticket_cross_area.is_cross_area, True)

        self.needs_adjudication_ticket_same_area.populate_cross_area_flag()
        self.needs_adjudication_ticket_same_area.refresh_from_db()
        self.assertEqual(self.needs_adjudication_ticket_same_area.is_cross_area, False)

        self.needs_adjudication_ticket_ind_no_household.populate_cross_area_flag()
        self.needs_adjudication_ticket_ind_no_household.refresh_from_db()
        self.assertEqual(self.needs_adjudication_ticket_ind_no_household.is_cross_area, False)
