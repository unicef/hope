import datetime
from typing import Any, Dict, List

from dateutil.relativedelta import relativedelta
from django.core.management import call_command
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import (
    create_household,
    create_household_and_individuals,
)
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.targeting import TargetingCriteriaRuleFactory
from flaky import flaky

from hope.apps.core.base_test_case import BaseTestCase
from hope.models.business_area import BusinessArea
from hope.models.household import Household
from hope.models.individual import Individual
from hope.models.payment_plan import PaymentPlan
from hope.models.targeting_individual_block_rule_filter import TargetingIndividualBlockRuleFilter
from hope.models.targeting_criteria_rule_filter import TargetingCriteriaRuleFilter
from hope.models.targeting_individual_rule_filter_block import TargetingIndividualRuleFilterBlock
from hope.models.targeting_criteria_rule import TargetingCriteriaRule


class TestTargetingCriteriaQuery(BaseTestCase):
    @staticmethod
    def get_targeting_criteria_for_rule(rule_filter: Dict, payment_plan: PaymentPlan) -> PaymentPlan:
        rule = TargetingCriteriaRule(payment_plan=payment_plan)
        rule.save()
        rule_filter = TargetingCriteriaRuleFilter(**rule_filter, targeting_criteria_rule=rule)
        rule_filter.save()
        return payment_plan

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadflexfieldsattributes")
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.first()

        (household, individuals) = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": cls.business_area},
        )
        (household, individuals) = create_household(
            {
                "size": 2,
                "residence_status": "REFUGEE",
                "business_area": cls.business_area,
            },
        )

        assert Household.objects.all().distinct().count() == 2

    @classmethod
    def create_criteria(cls, *args: Any, **kwargs: Any) -> PaymentPlan:
        payment_plan = PaymentPlanFactory(
            name="tp",
            created_by=cls.user,
            business_area=cls.business_area,
        )
        return cls.get_targeting_criteria_for_rule(*args, payment_plan=payment_plan, **kwargs)

    def test_size(self) -> None:
        assert (
            Household.objects.filter(
                self.create_criteria(
                    {
                        "comparison_method": "EQUALS",
                        "arguments": [2],
                        "field_name": "size",
                        "flex_field_classification": "NOT_FLEX_FIELD",
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
                        "flex_field_classification": "NOT_FLEX_FIELD",
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
                        "flex_field_classification": "FLEX_FIELD_BASIC",
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
                        "flex_field_classification": "FLEX_FIELD_BASIC",
                    }
                ).get_query()
            )
            .distinct()
            .count()
            == 0
        )


class TestTargetingCriteriaIndividualRules(BaseTestCase):
    @staticmethod
    def get_targeting_criteria_for_filters(filters: List[Dict], payment_plan: PaymentPlan) -> PaymentPlan:
        rule = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        filter_block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=rule)
        for _filter in filters:
            block_filter = TargetingIndividualBlockRuleFilter(**_filter, individuals_filters_block=filter_block)
            block_filter.save()
        return payment_plan

    @classmethod
    def create_criteria(cls, filters: List[Dict]) -> PaymentPlan:
        payment_plan = PaymentPlanFactory(
            name="tp",
            created_by=cls.user,
            business_area=cls.business_area,
        )

        return cls.get_targeting_criteria_for_filters(filters, payment_plan)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
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
                    "observed_disability": [
                        "SEEING",
                        "HEARING",
                        "WALKING",
                        "MEMORY",
                        "SELF_CARE",
                        "COMMUNICATING",
                    ],
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
                            "flex_field_classification": "NOT_FLEX_FIELD",
                        },
                        {
                            "comparison_method": "EQUALS",
                            "arguments": ["MALE"],
                            "field_name": "sex",
                            "flex_field_classification": "NOT_FLEX_FIELD",
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
                            "arguments": [
                                "COMMUNICATING",
                                "HEARING",
                                "MEMORY",
                                "SEEING",
                                "WALKING",
                                "SELF_CARE",
                            ],
                            "field_name": "observed_disability",
                            "flex_field_classification": "NOT_FLEX_FIELD",
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
                            "flex_field_classification": "NOT_FLEX_FIELD",
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
                            "flex_field_classification": "NOT_FLEX_FIELD",
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
                            "flex_field_classification": "NOT_FLEX_FIELD",
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
                            "flex_field_classification": "NOT_FLEX_FIELD",
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
                            "flex_field_classification": "NOT_FLEX_FIELD",
                        },
                    ]
                ).get_query()
            )
            .distinct()
            .count()
            == 2
        )


class TestTargetingCriteriaByIdQuery(BaseTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.first()

        cls.hh_1, individuals = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": cls.business_area},
        )
        cls.hh_2, individuals = create_household(
            {
                "size": 2,
                "residence_status": "REFUGEE",
                "business_area": cls.business_area,
            },
        )
        cls.hh_3, individuals = create_household(
            {
                "size": 3,
                "residence_status": "REFUGEE",
                "business_area": cls.business_area,
            },
        )

        assert Household.objects.all().distinct().count() == 3

    def test_household_ids(self) -> None:
        payment_plan = PaymentPlanFactory(
            name="tp",
            created_by=self.user,
            business_area=self.business_area,
        )
        TargetingCriteriaRuleFactory(
            payment_plan=payment_plan,
            household_ids=f"{self.hh_1.unicef_id}",
            individual_ids="",
        )

        assert Household.objects.filter(payment_plan.get_query()).distinct().count() == 1
        payment_plan2 = PaymentPlanFactory(
            name="tp",
            created_by=self.user,
            business_area=self.business_area,
        )
        TargetingCriteriaRuleFactory(
            payment_plan=payment_plan2,
            household_ids=f"{self.hh_3.unicef_id}, {self.hh_2.unicef_id}",
            individual_ids="",
        )
        assert Household.objects.filter(payment_plan2.get_query()).distinct().count() == 2

    @flaky(max_runs=3, min_passes=1)
    def test_individual_ids(self) -> None:
        payment_plan = PaymentPlanFactory(
            name="tp",
            created_by=self.user,
            business_area=self.business_area,
        )
        TargetingCriteriaRuleFactory(
            payment_plan=payment_plan,
            household_ids="",
            individual_ids=f"{self.hh_1.individuals.first().unicef_id}",
        )
        assert Household.objects.filter(payment_plan.get_query()).distinct().count() == 1
        payment_plan2 = PaymentPlanFactory(
            name="tp",
            created_by=self.user,
            business_area=self.business_area,
        )
        TargetingCriteriaRuleFactory(
            payment_plan=payment_plan2,
            household_ids="",
            individual_ids=f"{self.hh_2.individuals.first().unicef_id}, {self.hh_1.individuals.first().unicef_id}",
        )

        assert Household.objects.filter(payment_plan2.get_query()).distinct().count() == 2

    @flaky(max_runs=3, min_passes=1)
    def test_household_and_individual_ids(self) -> None:
        payment_plan = PaymentPlanFactory(
            name="tp",
            created_by=self.user,
            business_area=self.business_area,
        )
        TargetingCriteriaRuleFactory(
            payment_plan=payment_plan,
            household_ids=f"{self.hh_1.unicef_id}, {self.hh_2.unicef_id}",
            individual_ids=f"{self.hh_3.individuals.first().unicef_id}",
        )

        assert Household.objects.filter(payment_plan.get_query()).distinct().count() == 3
