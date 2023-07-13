from parameterized import parameterized

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.grievance.fixtures import TicketNeedsAdjudicationDetailsFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household_and_individuals, IndividualFactory
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.targeting.fixtures import TargetingCriteriaFactory, TargetPopulationFactory
from hct_mis_api.apps.targeting.services.targeting_service import TargetingCriteriaQueryingBase


class TestTargetingCriteriaFlags(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()
        cls.household1, cls.individuals1 = create_household_and_individuals(
            household_data={
                "business_area": cls.business_area,
            },
            individuals_data=[
                {
                    "given_name": "OK1",
                },
                {
                    "given_name": "OK2",
                },
            ],
        )
        cls.representative1 = IndividualFactory(household=None)
        cls.household1.representatives.set([cls.representative1])

        cls.household2, cls.individuals2 = create_household_and_individuals(
            household_data={
                "business_area": cls.business_area,
            },
            individuals_data=[
                {
                    "given_name": "TEST1",
                },
                {
                    "given_name": "TEST2",
                },
            ],
        )
        targeting_criteria = TargetingCriteriaFactory(
            flag_exclude_if_active_adjudication_ticket=True,
            flag_exclude_if_on_sanction_list=True,
        )
        TargetPopulationFactory(
            targeting_criteria=targeting_criteria,
            business_area=cls.business_area,
            households=[cls.household1, cls.household2],
        )
        cls.representative2 = IndividualFactory(household=None)
        cls.household2.representatives.set([cls.representative2])

        golden_records_individual = IndividualFactory(household=None)
        cls.ticket_needs_adjudication_details_for_member = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=golden_records_individual,
        )
        cls.ticket_needs_adjudication_details_for_representative = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=golden_records_individual,
        )

    @parameterized.expand(
        [
            (True, False, GrievanceTicket.STATUS_IN_PROGRESS, 1),
            (True, False, GrievanceTicket.STATUS_CLOSED, 2),
            (False, True, GrievanceTicket.STATUS_IN_PROGRESS, 1),
            (False, True, GrievanceTicket.STATUS_CLOSED, 2),
            (True, True, GrievanceTicket.STATUS_IN_PROGRESS, 1),
            (True, True, GrievanceTicket.STATUS_CLOSED, 2),
        ]
    )
    def test_flag_exclude_if_active_adjudication_ticket_for_duplicate(
        self,
        member_has_adjudication_ticket_as_duplicate: bool,
        representative_has_adjudication_ticket_as_duplicate: bool,
        ticket_status: int,
        household_count: int,
    ) -> None:
        """
        household1 does not have any adjudication tickets so should not be excluded in any case.
        household2 should be excluded if any member or representative has an active adjudication ticket as a duplicate.
        Ticket is not considered active if its status is CLOSED.
        """
        if member_has_adjudication_ticket_as_duplicate:
            self.ticket_needs_adjudication_details_for_member.ticket.status = ticket_status
            self.ticket_needs_adjudication_details_for_member.ticket.save()
            self.ticket_needs_adjudication_details_for_member.possible_duplicates.set([self.individuals2[0]])
        if representative_has_adjudication_ticket_as_duplicate:
            self.ticket_needs_adjudication_details_for_representative.ticket.status = ticket_status
            self.ticket_needs_adjudication_details_for_representative.ticket.save()
            self.ticket_needs_adjudication_details_for_representative.possible_duplicates.set([self.representative2])
        self.assertEqual(Household.objects.count(), 2)
        targeting_criteria = TargetingCriteriaQueryingBase()
        targeting_criteria.flag_exclude_if_active_adjudication_ticket = True
        household_filtered = Household.objects.filter(
            targeting_criteria.apply_flag_exclude_if_active_adjudication_ticket()
        )
        self.assertEqual(household_filtered.count(), household_count)

    @parameterized.expand(
        [
            (True, False, GrievanceTicket.STATUS_IN_PROGRESS, 1),
            (True, False, GrievanceTicket.STATUS_CLOSED, 2),
            (False, True, GrievanceTicket.STATUS_IN_PROGRESS, 1),
            (False, True, GrievanceTicket.STATUS_CLOSED, 2),
            (True, True, GrievanceTicket.STATUS_IN_PROGRESS, 1),
            (True, True, GrievanceTicket.STATUS_CLOSED, 2),
        ]
    )
    def test_flag_exclude_if_active_adjudication_ticket_for_golden_record(
        self,
        member_has_adjudication_ticket_as_golden_record: bool,
        representative_has_adjudication_ticket_golden_record: bool,
        ticket_status: int,
        household_count: int,
    ) -> None:
        """
        household1 does not have any adjudication tickets so should not be excluded in any case.
        household2 should be excluded if any member or representative has an active adjudication ticket as a golden
        records individual.
        Ticket is not considered active if its status is CLOSED.
        """
        if member_has_adjudication_ticket_as_golden_record:
            self.ticket_needs_adjudication_details_for_member.ticket.status = ticket_status
            self.ticket_needs_adjudication_details_for_member.ticket.save()
            self.ticket_needs_adjudication_details_for_member.golden_records_individual = self.individuals2[0]
            self.ticket_needs_adjudication_details_for_member.save()
        if representative_has_adjudication_ticket_golden_record:
            self.ticket_needs_adjudication_details_for_representative.ticket.status = ticket_status
            self.ticket_needs_adjudication_details_for_representative.ticket.save()
            self.ticket_needs_adjudication_details_for_representative.golden_records_individual = self.representative2
            self.ticket_needs_adjudication_details_for_representative.save()
        self.assertEqual(Household.objects.count(), 2)
        targeting_criteria = TargetingCriteriaQueryingBase()
        targeting_criteria.flag_exclude_if_active_adjudication_ticket = True
        household_filtered = Household.objects.filter(
            targeting_criteria.apply_flag_exclude_if_active_adjudication_ticket()
        )
        self.assertEqual(household_filtered.count(), household_count)

    def test_flag_exclude_if_active_adjudication_ticket_no_ticket(self) -> None:
        self.assertEqual(Household.objects.count(), 2)
        targeting_criteria = TargetingCriteriaQueryingBase()
        targeting_criteria.flag_exclude_if_active_adjudication_ticket = True
        household_filtered = Household.objects.filter(
            targeting_criteria.apply_flag_exclude_if_active_adjudication_ticket()
        )
        self.assertEqual(household_filtered.count(), 2)

    @parameterized.expand(
        [
            (True, False, 1),
            (False, True, 1),
            (True, True, 1),
            (False, False, 2),
        ]
    )
    def test_flag_exclude_if_on_sanction_list(
        self,
        member_is_sanctioned: bool,
        representative_is_sanctioned: bool,
        household_count: int,
    ) -> None:
        if member_is_sanctioned:
            self.individuals2[0].sanction_list_confirmed_match = True
            self.individuals2[0].save()
        if representative_is_sanctioned:
            self.representative2.sanction_list_confirmed_match = True
            self.representative2.save()
        self.assertEqual(Household.objects.count(), 2)
        targeting_criteria = TargetingCriteriaQueryingBase()
        targeting_criteria.flag_exclude_if_on_sanction_list = True
        household_filtered = Household.objects.filter(targeting_criteria.apply_flag_exclude_if_on_sanction_list())
        self.assertEqual(household_filtered.count(), household_count)
