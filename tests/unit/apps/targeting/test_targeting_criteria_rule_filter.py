from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone
from freezegun import freeze_time
import pytest
from pytz import utc

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FlexibleAttributeFactory,
    FlexibleAttributeForPDUFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentPlanFactory,
    PeriodicFieldDataFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.targeting.choices import FlexFieldClassification
from hope.models import (
    FlexibleAttribute,
    Household,
    Individual,
    PeriodicFieldData,
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


@pytest.fixture
def age_test_data(business_area):
    def _household(birth_date: str):
        hh = HouseholdFactory(
            business_area=business_area,
            first_registration_date=timezone.make_aware(datetime.strptime("1900-01-01", "%Y-%m-%d"), utc),
        )
        ind = IndividualFactory(
            birth_date=birth_date,
            business_area=business_area,
        )
        hh.individuals.set([ind])
        return hh

    hh_50 = _household("1970-09-29")
    _household("1991-11-18")
    _household("1991-11-18")

    return hh_50


@pytest.fixture
def pdu_setup(business_area, user, program):
    program_cycle = program.cycles.first()
    pdu_data = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.STRING,
        number_of_rounds=1,
        rounds_names=["Round 1"],
    )
    pdu_field = FlexibleAttributeForPDUFactory(
        program=program,
        label={"English(EN)": "PDU STRING"},
        pdu_data=pdu_data,
        name="pdu_string",
    )
    ind1 = IndividualFactory(
        business_area=business_area,
        flex_fields={pdu_field.name: {"1": {"value": "some value"}}},
    )
    ind2 = IndividualFactory(
        business_area=business_area,
        flex_fields={pdu_field.name: {"1": {"value": None}}},
    )

    return program_cycle, user, pdu_field, [ind1, ind2]


def test_wrong_arguments_count_validation():
    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="EQUALS",
        field_name="size",
        arguments=[2, 1],
    )
    with pytest.raises(ValidationError):
        rule_filter.get_query()

    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="EQUALS",
        field_name="size",
        arguments=[],
    )
    with pytest.raises(ValidationError):
        rule_filter.get_query()

    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="EQUALS",
        field_name="size",
    )
    with pytest.raises(ValidationError):
        rule_filter.get_query()


@freeze_time("2020-10-10")
def test_rule_filter_age_equals(age_test_data):
    rule_filter = TargetingIndividualBlockRuleFilter(
        comparison_method="EQUALS",
        field_name="age",
        arguments=[50],
    )
    queryset = Individual.objects.filter(rule_filter.get_query())
    assert queryset.count() == 1
    assert queryset.first().household == age_test_data


def test_rule_filter_size_equals():
    business_area = BusinessAreaFactory()
    HouseholdFactory(size=1, business_area=business_area)
    hh2 = HouseholdFactory(size=2, business_area=business_area)

    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="EQUALS",
        field_name="size",
        arguments=[2],
    )
    queryset = Household.objects.filter(rule_filter.get_query())

    assert queryset.count() == 1
    assert hh2 in queryset


def test_flex_field_integer_equals():
    FlexibleAttributeFactory(
        name="total_households_h_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
        type=FlexibleAttribute.INTEGER,
    )

    business_area = BusinessAreaFactory()
    hh = HouseholdFactory(
        business_area=business_area,
        flex_fields={"total_households_h_f": 4},
    )

    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="EQUALS",
        field_name="total_households_h_f",
        arguments=[4],
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
    )

    queryset = Household.objects.filter(rule_filter.get_query())
    assert queryset.count() == 1
    assert hh in queryset


def test_pdu_string_contains(pdu_setup):
    program_cycle, user, pdu_field, individuals = pdu_setup

    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, created_by=user)
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(
        targeting_criteria_rule=tcr,
        target_only_hoh=False,
    )
    rule_filter = TargetingIndividualBlockRuleFilter(
        individuals_filters_block=block,
        comparison_method="CONTAINS",
        field_name=pdu_field.name,
        arguments=["some"],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    queryset = Individual.objects.filter(rule_filter.get_query())
    assert queryset.count() == 1
    assert individuals[0] in queryset
