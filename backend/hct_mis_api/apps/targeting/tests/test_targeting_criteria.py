import datetime
from typing import Any, Dict, List

from django.core.management import call_command

from dateutil.relativedelta import relativedelta
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.fixtures import TicketNeedsAdjudicationDetailsFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import (
    IndividualFactory,
    create_household,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
    TargetPopulation,
)
from hct_mis_api.apps.targeting.services.targeting_service import (
    TargetingCriteriaQueryingBase,
)


class TestTargetingCriteriaQuery(APITestCase):
    @staticmethod
    def get_targeting_criteria_for_rule(rule_filter: Dict) -> TargetingCriteria:
        targeting_criteria = TargetingCriteria()
        targeting_criteria.save()
        rule = TargetingCriteriaRule(targeting_criteria=targeting_criteria)
        rule.save()
        rule_filter = TargetingCriteriaRuleFilter(**rule_filter, targeting_criteria_rule=rule)
        rule_filter.save()
        return targeting_criteria

    @classmethod
    def setUpTestData(cls) -> None:
        call_command("loadflexfieldsattributes")
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.first()

        (household, individuals) = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": cls.business_area},
        )
        (household, individuals) = create_household(
            {"size": 2, "residence_status": "REFUGEE", "business_area": cls.business_area},
        )

        assert Household.objects.all().distinct().count() == 2

    @classmethod
    def create_criteria(cls, *args: Any, **kwargs: Any) -> TargetingCriteria:
        criteria = cls.get_targeting_criteria_for_rule(*args, **kwargs)
        TargetPopulation(
            name="tp",
            created_by=cls.user,
            business_area=cls.business_area,
            targeting_criteria=criteria,
        )
        criteria.save()
        return criteria

    def test_size(self) -> None:
        assert (
            Household.objects.filter(
                self.create_criteria(
                    {
                        "comparison_method": "EQUALS",
                        "arguments": [2],
                        "field_name": "size",
                        "is_flex_field": False,
                    }
                ).get_query()
            )
            .distinct()
            .count()
            == 1
        )

    def test_residence_status(self) -> None:
        assert (
            Household.objects.filter(
                self.create_criteria(
                    {
                        "comparison_method": "EQUALS",
                        "arguments": ["REFUGEE"],
                        "field_name": "residence_status",
                        "is_flex_field": False,
                    }
                ).get_query()
            )
            .distinct()
            .count()
            == 1
        )

    def test_flex_field_variables(self) -> None:
        assert (
            Household.objects.filter(
                self.create_criteria(
                    {
                        "comparison_method": "EQUALS",
                        "arguments": ["0"],
                        "field_name": "unaccompanied_child_h_f",
                        "is_flex_field": True,
                    }
                ).get_query()
            )
            .distinct()
            .count()
            == 0
        )

    def test_select_many_variables(self) -> None:
        assert (
            Household.objects.filter(
                self.create_criteria(
                    {
                        "comparison_method": "CONTAINS",
                        "arguments": ["other_public", "pharmacy", "other_private"],
                        "field_name": "treatment_facility_h_f",
                        "is_flex_field": True,
                    }
                ).get_query()
            )
            .distinct()
            .count()
            == 0
        )


class TestTargetingCriteriaIndividualRules(APITestCase):
    @staticmethod
    def get_targeting_criteria_for_filters(filters: List[Dict]) -> TargetingCriteria:
        targeting_criteria = TargetingCriteria()
        targeting_criteria.save()
        rule = TargetingCriteriaRule(targeting_criteria=targeting_criteria)
        rule.save()
        filter_block = TargetingIndividualRuleFilterBlock(targeting_criteria_rule=rule)
        filter_block.save()
        for filter in filters:
            block_filter = TargetingIndividualBlockRuleFilter(**filter, individuals_filters_block=filter_block)
            block_filter.save()
        return targeting_criteria

    @classmethod
    def create_criteria(cls, *args: Any, **kwargs: Any) -> TargetPopulation:
        criteria = cls.get_targeting_criteria_for_filters(*args, **kwargs)
        TargetPopulation(
            name="tp",
            created_by=cls.user,
            business_area=cls.business_area,
            targeting_criteria=criteria,
        )
        criteria.save()
        return criteria

    @classmethod
    def setUpTestData(cls) -> None:
        call_command("loadflexfieldsattributes")
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.first()

        (household, individuals1) = create_household_and_individuals(
            {"business_area": cls.business_area},
            [
                {
                    "sex": "MALE",
                    "marital_status": "MARRIED",
                    "observed_disability": ["SEEING", "HEARING", "WALKING", "MEMORY", "SELF_CARE", "COMMUNICATING"],
                    "seeing_disability": "LOT_DIFFICULTY",
                    "hearing_disability": "SOME_DIFFICULTY",
                    "physical_disability": "SOME_DIFFICULTY",
                    "memory_disability": "LOT_DIFFICULTY",
                    "selfcare_disability": "CANNOT_DO",
                    "comms_disability": "SOME_DIFFICULTY",
                    "business_area": cls.business_area,
                },
            ],
        )
        (household, individuals2) = create_household_and_individuals(
            {"business_area": cls.business_area},
            [
                {
                    "sex": "MALE",
                    "marital_status": "SINGLE",
                    "business_area": cls.business_area,
                },
                {
                    "sex": "FEMALE",
                    "marital_status": "MARRIED",
                    "business_area": cls.business_area,
                },
            ],
        )

        individuals1[0].birth_date = datetime.date.today() - relativedelta(years=+20, days=+5)  # age 20
        individuals2[0].birth_date = datetime.date.today() - relativedelta(years=+24, days=+5)  # age 24
        individuals2[1].birth_date = datetime.date.today() - relativedelta(years=+26, days=-5)  # age 25
        Individual.objects.bulk_update(individuals1 + individuals2, ["birth_date"])

        assert Household.objects.all().distinct().count() == 2

    def test_marital_status(self) -> None:
        assert (
            Household.objects.filter(
                self.create_criteria(
                    [
                        {
                            "comparison_method": "EQUALS",
                            "arguments": ["MARRIED"],
                            "field_name": "marital_status",
                            "is_flex_field": False,
                        },
                        {
                            "comparison_method": "EQUALS",
                            "arguments": ["MALE"],
                            "field_name": "sex",
                            "is_flex_field": False,
                        },
                    ]
                ).get_query()
            )
            .distinct()
            .count()
            == 1
        )

    def test_observed_disability(self) -> None:
        assert (
            Household.objects.filter(
                self.create_criteria(
                    [
                        {
                            "comparison_method": "CONTAINS",
                            "arguments": ["COMMUNICATING", "HEARING", "MEMORY", "SEEING", "WALKING", "SELF_CARE"],
                            "field_name": "observed_disability",
                            "is_flex_field": False,
                        },
                    ]
                ).get_query()
            )
            .distinct()
            .count()
            == 2
        )

    def test_ranges(self) -> None:
        assert (
            Household.objects.filter(
                self.create_criteria(
                    [
                        {
                            "comparison_method": "RANGE",
                            "arguments": [20, 25],
                            "field_name": "age",
                            "is_flex_field": False,
                        },
                    ]
                ).get_query()
            )
            .distinct()
            .count()
            == 2
        )

        assert (
            Household.objects.filter(
                self.create_criteria(
                    [
                        {
                            "comparison_method": "RANGE",
                            "arguments": [22, 26],
                            "field_name": "age",
                            "is_flex_field": False,
                        },
                    ]
                ).get_query()
            )
            .distinct()
            .count()
            == 1
        )

        assert (
            Household.objects.filter(
                self.create_criteria(
                    [
                        {
                            "comparison_method": "LESS_THAN",
                            "arguments": [20],
                            "field_name": "age",
                            "is_flex_field": False,
                        },
                    ]
                ).get_query()
            )
            .distinct()
            .count()
            == 1
        )

        assert (
            Household.objects.filter(
                self.create_criteria(
                    [
                        {
                            "comparison_method": "LESS_THAN",
                            "arguments": [24],
                            "field_name": "age",
                            "is_flex_field": False,
                        },
                    ]
                ).get_query()
            )
            .distinct()
            .count()
            == 2
        )

        assert (
            Household.objects.filter(
                self.create_criteria(
                    [
                        {
                            "comparison_method": "GREATER_THAN",
                            "arguments": [20],
                            "field_name": "age",
                            "is_flex_field": False,
                        },
                    ]
                ).get_query()
            )
            .distinct()
            .count()
            == 2
        )


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
        household_filtered = Household.objects.filter(
            TargetingCriteriaQueryingBase.apply_flag_exclude_if_active_adjudication_ticket()
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
        household_filtered = Household.objects.filter(
            TargetingCriteriaQueryingBase.apply_flag_exclude_if_active_adjudication_ticket()
        )
        self.assertEqual(household_filtered.count(), household_count)

    def test_flag_exclude_if_active_adjudication_ticket_no_ticket(self) -> None:
        self.assertEqual(Household.objects.count(), 2)
        household_filtered = Household.objects.filter(
            TargetingCriteriaQueryingBase.apply_flag_exclude_if_active_adjudication_ticket()
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
        household_filtered = Household.objects.filter(
            TargetingCriteriaQueryingBase.apply_flag_exclude_if_on_sanction_list()
        )
        self.assertEqual(household_filtered.count(), household_count)
