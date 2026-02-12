import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.targeting.services.utils import (
    from_input_to_targeting_criteria,
    get_existing_unicef_ids,
)
from hope.models import (
    Household,
    Individual,
    Program,
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
def program(business_area):
    program = ProgramFactory(
        business_area=business_area,
        name="Program Active",
        status=Program.ACTIVE,
    )
    ProgramCycleFactory(program=program)
    return program


def test_get_existing_unicef_ids(user, business_area, program) -> None:
    hoh1 = IndividualFactory(household=None, program=program)
    hoh2 = IndividualFactory(household=None, program=program)

    hh1 = HouseholdFactory(head_of_household=hoh1, program=program)
    hh2 = HouseholdFactory(head_of_household=hoh2, program=program)

    ind1 = IndividualFactory(household=hh1, program=program)
    ind2 = IndividualFactory(household=hh2, program=program)

    ids_1 = get_existing_unicef_ids(f"{hh1},HH-invalid", Household, program)
    assert ids_1 == f"{hh1}"

    ids_2 = get_existing_unicef_ids(f" {hh1}, {hh2} ", Household, program)
    assert sorted(ids_2.split(", ")) == sorted([str(hh1), str(hh2)])

    ids_3 = get_existing_unicef_ids(f"{ind1}, IND-000", Individual, program)
    assert ids_3 == f"{ind1}"

    ids_4 = get_existing_unicef_ids(f"{ind1}, {ind2}, HH-2", Individual, program)
    assert sorted(ids_4.split(", ")) == sorted([str(ind1), str(ind2)])


def test_from_input_to_targeting_criteria_creates_expected_objects(user, business_area, program) -> None:
    hoh1 = IndividualFactory(household=None, program=program)
    hoh2 = IndividualFactory(household=None, program=program)

    hh1 = HouseholdFactory(head_of_household=hoh1, program=program)
    hh2 = HouseholdFactory(head_of_household=hoh2, program=program)

    IndividualFactory(household=hh1, program=program)
    ind2 = IndividualFactory(household=hh2, program=program)
    payment_plan = PaymentPlanFactory(program_cycle=program.cycles.first())

    assert TargetingCriteriaRule.objects.count() == 0
    assert TargetingCriteriaRuleFilter.objects.count() == 0
    assert TargetingIndividualRuleFilterBlock.objects.count() == 0
    assert TargetingIndividualBlockRuleFilter.objects.count() == 0

    targeting_criteria_input = {
        "flag_exclude_if_active_adjudication_ticket": False,
        "flag_exclude_if_on_sanction_list": False,
        "rules": [
            {
                "household_ids": hh1.unicef_id,
                "individual_ids": ind2.unicef_id,
                "households_filters_blocks": [
                    {
                        "comparison_method": "EQUALS",
                        "arguments": [2],
                        "field_name": "size",
                        "flex_field_classification": "NOT_FLEX_FIELD",
                    }
                ],
                "individuals_filters_blocks": [
                    {
                        "individual_block_filters": [
                            {
                                "comparison_method": "RANGE",
                                "arguments": [1, 99],
                                "field_name": "age_at_registration",
                                "flex_field_classification": "NOT_FLEX_FIELD",
                            }
                        ]
                    }
                ],
            }
        ],
    }

    from_input_to_targeting_criteria(targeting_criteria_input, program, payment_plan)

    assert TargetingCriteriaRule.objects.count() == 1
    assert TargetingCriteriaRuleFilter.objects.count() == 1
    assert TargetingIndividualRuleFilterBlock.objects.count() == 1
    assert TargetingIndividualBlockRuleFilter.objects.count() == 1

    rule = TargetingCriteriaRule.objects.first()
    assert rule.household_ids == hh1.unicef_id
    assert rule.individual_ids == ind2.unicef_id

    hh_filter = TargetingCriteriaRuleFilter.objects.first()
    assert hh_filter.field_name == "size"
    assert hh_filter.arguments == [2]

    ind_filter = TargetingIndividualBlockRuleFilter.objects.first()
    assert ind_filter.field_name == "age_at_registration"
    assert ind_filter.arguments == [1, 99]
