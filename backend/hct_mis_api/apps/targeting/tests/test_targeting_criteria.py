import datetime
from typing import Any, Dict, List

from dateutil.relativedelta import relativedelta
from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import (
    create_household,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
    TargetPopulation,
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
