import datetime

from dateutil.relativedelta import relativedelta
from flaky import flaky
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FlexibleAttributeFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentPlanFactory,
    UserFactory,
)
from hope.models import (
    Household,
    PaymentPlan,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def payment_plan(user, business_area):
    return PaymentPlanFactory(
        name="tp", created_by=user, business_area=business_area, status=PaymentPlan.Status.TP_OPEN
    )


@pytest.fixture
def base_households(business_area):
    HouseholdFactory(size=1, residence_status="HOST", business_area=business_area)
    HouseholdFactory(size=2, residence_status="REFUGEE", business_area=business_area)
    return Household.objects.all()


@pytest.fixture
def household_flex_fields():
    from hope.models import FlexibleAttribute

    FlexibleAttributeFactory(
        name="unaccompanied_child_h_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
        type=FlexibleAttribute.STRING,
    )
    FlexibleAttributeFactory(
        name="treatment_facility_h_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
        type=FlexibleAttribute.SELECT_MANY,
    )


@pytest.fixture
def apply_household_rule(payment_plan):
    def _apply(rule_filter: dict):
        rule = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
        TargetingCriteriaRuleFilter.objects.create(
            targeting_criteria_rule=rule,
            **rule_filter,
        )
        return payment_plan

    return _apply


@pytest.fixture
def households_with_individuals(business_area):
    ind_1 = IndividualFactory(
        household=None,
        sex="MALE",
        marital_status="MARRIED",
        birth_date=datetime.date.today() - relativedelta(years=20, days=5),
        observed_disability=[
            "SEEING",
            "HEARING",
            "WALKING",
            "MEMORY",
            "SELF_CARE",
            "COMMUNICATING",
        ],
    )
    hh1 = HouseholdFactory(business_area=business_area, head_of_household=ind_1, size=1)
    ind_1.household = hh1
    ind_1.save()

    ind_2 = IndividualFactory(
        household=None,
        sex="MALE",
        marital_status="SINGLE",
        birth_date=datetime.date.today() - relativedelta(years=24, days=5),
        observed_disability=["NONE"],
    )
    hh2 = HouseholdFactory(business_area=business_area, head_of_household=ind_2, size=2)
    ind_2.household = hh2
    ind_2.save()
    IndividualFactory(
        household=hh2,
        sex="FEMALE",
        marital_status="MARRIED",
        birth_date=datetime.date.today() - relativedelta(years=26, days=-5),
        observed_disability=["NONE"],
    )

    return Household.objects.all()


@pytest.fixture
def apply_individual_rules(payment_plan):
    def _apply(filters: list[dict]):
        rule = TargetingCriteriaRule.objects.create(payment_plan=payment_plan, household_ids="", individual_ids="")
        block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=rule)
        for f in filters:
            TargetingIndividualBlockRuleFilter.objects.create(
                individuals_filters_block=block,
                **f,
            )
        return payment_plan

    return _apply


@pytest.fixture
def three_households(business_area):
    hh1 = HouseholdFactory(size=1, residence_status="HOST", business_area=business_area)
    hh2 = HouseholdFactory(size=2, residence_status="REFUGEE", business_area=business_area)
    hh3 = HouseholdFactory(size=3, residence_status="REFUGEE", business_area=business_area)
    return hh1, hh2, hh3


def test_size(base_households, apply_household_rule):
    plan = apply_household_rule(
        {
            "comparison_method": "EQUALS",
            "arguments": [2],
            "field_name": "size",
            "flex_field_classification": "NOT_FLEX_FIELD",
        }
    )
    assert Household.objects.filter(plan.get_query()).distinct().count() == 1


def test_residence_status(base_households, apply_household_rule):
    plan = apply_household_rule(
        {
            "comparison_method": "EQUALS",
            "arguments": ["REFUGEE"],
            "field_name": "residence_status",
            "flex_field_classification": "NOT_FLEX_FIELD",
        }
    )
    assert Household.objects.filter(plan.get_query()).distinct().count() == 1


def test_flex_field_variables(base_households, household_flex_fields, apply_household_rule):
    plan = apply_household_rule(
        {
            "comparison_method": "EQUALS",
            "arguments": ["0"],
            "field_name": "unaccompanied_child_h_f",
            "flex_field_classification": "FLEX_FIELD_BASIC",
        }
    )
    assert Household.objects.filter(plan.get_query()).distinct().count() == 0


def test_select_many_variables(base_households, household_flex_fields, apply_household_rule):
    plan = apply_household_rule(
        {
            "comparison_method": "CONTAINS",
            "arguments": ["other_public", "pharmacy", "other_private"],
            "field_name": "treatment_facility_h_f",
            "flex_field_classification": "FLEX_FIELD_BASIC",
        }
    )
    assert Household.objects.filter(plan.get_query()).distinct().count() == 0


def test_marital_status(households_with_individuals, apply_individual_rules):
    plan = apply_individual_rules(
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
    )
    assert Household.objects.filter(plan.get_query()).distinct().count() == 1


# def test_observed_disability(households_with_individuals, apply_individual_rules):
#     plan = apply_individual_rules(
#         [
#             {
#                 "comparison_method": "CONTAINS",
#                 "arguments": ["SEEING"],
#                 "field_name": "observed_disability",
#                 "flex_field_classification": "NOT_FLEX_FIELD",
#             }
#         ]
#     )
#     assert Household.objects.filter(plan.get_query()).distinct().count() == 1


@pytest.mark.parametrize(
    ("comparison_method", "arguments", "expected_count"),
    [
        ("GREATER_THAN", [18], 2),
        ("LESS_THAN", [25], 2),
        ("RANGE", [18, 30], 2),
        ("EQUALS", [20], 1),
        ("NOT_EQUALS", [20], 1),
    ],
)
def test_range(
    households_with_individuals,
    apply_individual_rules,
    comparison_method,
    arguments,
    expected_count,
):
    plan = apply_individual_rules(
        [
            {
                "comparison_method": comparison_method,
                "arguments": arguments,
                "field_name": "age",
                "flex_field_classification": "NOT_FLEX_FIELD",
            }
        ]
    )
    assert Household.objects.filter(plan.get_query()).distinct().count() == expected_count


def test_household_ids(user, business_area, three_households):
    hh1, _, _ = three_households
    plan = PaymentPlanFactory(created_by=user, business_area=business_area)
    TargetingCriteriaRule.objects.create(
        payment_plan=plan,
        household_ids=str(hh1.unicef_id),
        individual_ids="",
    )
    assert Household.objects.filter(plan.get_query()).distinct().count() == 1


@flaky
def test_individual_ids(user, business_area, three_households):
    hh1, _, _ = three_households
    individual = IndividualFactory(household=hh1)

    plan = PaymentPlanFactory(created_by=user, business_area=business_area)
    TargetingCriteriaRule.objects.create(
        payment_plan=plan,
        household_ids="",
        individual_ids=str(individual.unicef_id),
    )
    assert Household.objects.filter(plan.get_query()).distinct().count() == 1


def test_household_and_individual_ids(user, business_area, three_households):
    hh1, _, _ = three_households
    individual = IndividualFactory(household=hh1)

    plan = PaymentPlanFactory(created_by=user, business_area=business_area)
    TargetingCriteriaRule.objects.create(
        payment_plan=plan,
        household_ids=str(hh1.unicef_id),
        individual_ids=str(individual.unicef_id),
    )
    assert Household.objects.filter(plan.get_query()).distinct().count() == 1
