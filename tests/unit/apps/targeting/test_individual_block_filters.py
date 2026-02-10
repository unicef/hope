import pytest

from extras.test_utils.old_factories.account import UserFactory
from extras.test_utils.old_factories.core import (
    FlexibleAttributeFactory,
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
)
from extras.test_utils.old_factories.household import create_household_and_individuals
from extras.test_utils.old_factories.payment import PaymentPlanFactory, generate_delivery_mechanisms
from extras.test_utils.old_factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.household.const import FEMALE, MALE
from hope.apps.targeting.choices import FlexFieldClassification
from hope.models import (
    DataCollectingType,
    FlexibleAttribute,
    Household,
    PeriodicFieldData,
    TargetingCriteriaRule,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return create_afghanistan()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def program(business_area):
    program = ProgramFactory(business_area=business_area, name="Test Program")
    ProgramCycleFactory(program=program)
    return program


@pytest.fixture
def program_cycle(program):
    return program.cycles.first()


@pytest.fixture
def households_individuals(business_area, program):
    # HH 1: 1 individual
    hh1, inds1 = create_household_and_individuals(
        {"business_area": business_area, "program": program},
        [{"sex": MALE, "marital_status": "MARRIED"}],
    )
    # HH 2: 2 individuals
    hh2, inds2 = create_household_and_individuals(
        {"business_area": business_area, "program": program},
        [
            {"sex": MALE, "marital_status": "SINGLE"},
            {"sex": FEMALE, "marital_status": "MARRIED"},
        ],
    )

    return {"hh1": hh1, "hh2": hh2, "ind1": inds1[0], "ind2": inds2[0]}


@pytest.fixture(autouse=True)
def flex_attrs():
    FlexibleAttributeFactory(
        name="muac_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        type=FlexibleAttribute.DECIMAL,
    )
    generate_delivery_mechanisms()


def test_all_individuals_male_filter(user, program_cycle, households_individuals):
    queryset = Household.objects.all()
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, created_by=user)
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)
    TargetingIndividualBlockRuleFilter.objects.create(
        individuals_filters_block=block,
        comparison_method="EQUALS",
        field_name="marital_status",
        arguments=["MARRIED"],
    )
    TargetingIndividualBlockRuleFilter.objects.create(
        individuals_filters_block=block,
        comparison_method="EQUALS",
        field_name="sex",
        arguments=[MALE],
    )
    queryset = queryset.filter(payment_plan.get_query())
    assert queryset.count() == 1
    assert queryset.first().id == households_individuals["hh1"].id


def test_all_individuals_filter_on_mixins(user, program_cycle, households_individuals):
    queryset = Household.objects.all()
    pp = PaymentPlanFactory()
    tcr = TargetingCriteriaRule.objects.create(payment_plan=pp)
    pp.rules.set([tcr])
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)
    TargetingIndividualBlockRuleFilter.objects.create(
        comparison_method="EQUALS",
        field_name="marital_status",
        arguments=["MARRIED"],
        individuals_filters_block=block,
    )
    TargetingIndividualBlockRuleFilter.objects.create(
        comparison_method="EQUALS",
        field_name="sex",
        arguments=[MALE],
        individuals_filters_block=block,
    )

    queryset = queryset.filter(pp.get_query())
    assert queryset.count() == 1
    assert queryset.first().id == households_individuals["hh1"].id
    assert pp.get_individual_queryset().count() == 3
    assert pp.get_household_queryset().count() == 2


def test_two_separate_blocks_on_mixins(user, program_cycle, households_individuals):
    queryset = Household.objects.all()
    pp = PaymentPlanFactory()
    tcr = TargetingCriteriaRule.objects.create(payment_plan=pp)
    pp.rules.set([tcr])

    block1 = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)
    TargetingIndividualBlockRuleFilter.objects.create(
        individuals_filters_block=block1,
        comparison_method="EQUALS",
        field_name="marital_status",
        arguments=["MARRIED"],
    )
    TargetingIndividualBlockRuleFilter.objects.create(
        individuals_filters_block=block1,
        comparison_method="EQUALS",
        field_name="sex",
        arguments=[FEMALE],
    )

    block2 = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)
    TargetingIndividualBlockRuleFilter.objects.create(
        individuals_filters_block=block2,
        comparison_method="EQUALS",
        field_name="marital_status",
        arguments=["SINGLE"],
    )
    TargetingIndividualBlockRuleFilter.objects.create(
        individuals_filters_block=block2,
        comparison_method="EQUALS",
        field_name="sex",
        arguments=[MALE],
    )

    pp.refresh_from_db()
    queryset = queryset.filter(pp.get_query())
    assert queryset.count() == 1
    assert queryset.first().id == households_individuals["hh2"].id


def test_filter_on_flex_field_not_exist(user, program_cycle):
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, created_by=user)
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)
    queryset = Household.objects.all()

    TargetingIndividualBlockRuleFilter.objects.create(
        individuals_filters_block=block,
        comparison_method="CONTAINS",
        field_name="flex_field_2",
        arguments=["Average"],
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
    )

    with pytest.raises(
        Exception,
        match="There is no Flex Field Attributes associated with this fieldName flex_field_2",
    ):
        queryset.filter(payment_plan.get_query())


def test_filter_on_flex_field(user, program_cycle, households_individuals):
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, created_by=user)
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)
    FlexibleAttribute.objects.create(
        name="flex_field_1",
        type=FlexibleAttribute.STRING,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        label={"English(EN)": "value"},
    )
    queryset = Household.objects.all()
    TargetingIndividualBlockRuleFilter.objects.create(
        individuals_filters_block=block,
        comparison_method="CONTAINS",
        field_name="flex_field_1",
        arguments=["Average"],
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
    )

    # Before value
    queryset_before = queryset.filter(payment_plan.get_query())
    assert queryset_before.count() == 0
    # After setting flex field
    households_individuals["ind1"].flex_fields["flex_field_1"] = "Average value"
    households_individuals["ind1"].save()

    queryset_after = queryset.filter(payment_plan.get_query())
    assert queryset_after.count() == 1
    assert queryset_after.first().id == households_individuals["hh1"].id


def test_filter_on_pdu_flex_field_not_exist(user, program_cycle):
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, created_by=user)
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)
    queryset = Household.objects.all()

    TargetingIndividualBlockRuleFilter.objects.create(
        individuals_filters_block=block,
        comparison_method="RANGE",
        field_name="pdu_field_1",
        arguments=["2", "3"],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )
    with pytest.raises(
        Exception,
        match="There is no PDU Flex Field Attribute associated with this fieldName pdu_field_1 in program Test Program",
    ):
        queryset.filter(payment_plan.get_query())


def test_filter_on_pdu_flex_field_no_round_number(user, program_cycle, program):
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, created_by=user)
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)
    pdu_data = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.DECIMAL, number_of_rounds=2, rounds_names=["Round 1", "Round 2"]
    )
    FlexibleAttributeForPDUFactory(program=program, label="PDU Field 1", pdu_data=pdu_data)
    queryset = Household.objects.all()
    TargetingIndividualBlockRuleFilter.objects.create(
        individuals_filters_block=block,
        comparison_method="RANGE",
        field_name="pdu_field_1",
        arguments=["2", "3"],
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )
    with pytest.raises(Exception, match="Round number is missing for PDU Flex Field Attribute pdu_field_1"):
        queryset.filter(payment_plan.get_query())


def test_filter_on_pdu_flex_field_incorrect_round_number(user, program_cycle, program):
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, created_by=user)
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)
    pdu_data = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.DECIMAL, number_of_rounds=2, rounds_names=["Round 1", "Round 2"]
    )
    FlexibleAttributeForPDUFactory(program=program, label="PDU Field 1", pdu_data=pdu_data)

    queryset = Household.objects.all()
    TargetingIndividualBlockRuleFilter.objects.create(
        individuals_filters_block=block,
        comparison_method="RANGE",
        field_name="pdu_field_1",
        arguments=["2", "3"],
        round_number=3,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    with pytest.raises(
        Exception,
        match="Round number 3 is greater than the number of rounds for PDU Flex Field Attribute pdu_field_1",
    ):
        queryset.filter(payment_plan.get_query())


def test_filter_on_pdu_flex_field(user, program_cycle, households_individuals, program):
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, created_by=user)
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)
    pdu_data = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.DECIMAL, number_of_rounds=2, rounds_names=["Round 1", "Round 2"]
    )
    FlexibleAttributeForPDUFactory(program=program, label="PDU Field 1", pdu_data=pdu_data)
    queryset = Household.objects.all()
    TargetingIndividualBlockRuleFilter.objects.create(
        individuals_filters_block=block,
        comparison_method="RANGE",
        field_name="pdu_field_1",
        arguments=["2", "3"],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    households_individuals["ind1"].flex_fields = {"pdu_field_1": {"1": {"value": None}, "2": {"value": None}}}
    households_individuals["ind1"].save()
    households_individuals["ind2"].flex_fields = {
        "pdu_field_1": {"1": {"value": 1, "collection_date": "2021-01-01"}, "2": {"value": None}}
    }
    households_individuals["ind2"].save()

    # Before value
    queryset_before = queryset.filter(payment_plan.get_query())
    assert queryset_before.count() == 0

    households_individuals["ind1"].flex_fields["pdu_field_1"]["1"] = {"value": 2.5, "collection_date": "2021-01-01"}
    households_individuals["ind1"].save()

    queryset_after = queryset.filter(payment_plan.get_query())
    assert queryset_after.count() == 1
    assert queryset_after.first().id == households_individuals["hh1"].id


def test_exclude_by_ids(user, program_cycle, program, households_individuals):
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, created_by=user)

    empty_basic_query = payment_plan.get_basic_query()
    assert str(empty_basic_query) == "(AND: ('withdrawn', False), (NOT (AND: ('unicef_id__in', []))))"
    payment_plan.excluded_ids = f"{households_individuals['hh1'].unicef_id}, {households_individuals['hh2'].unicef_id}"
    payment_plan.save()
    payment_plan.refresh_from_db()

    basic_query_1 = payment_plan.get_basic_query()
    assert not payment_plan.is_social_worker_program
    assert str(basic_query_1) == (
        f"(AND: ('withdrawn', False), (NOT (AND: ('unicef_id__in', "
        f"['{households_individuals['hh1'].unicef_id}', "
        f"'{households_individuals['hh2'].unicef_id}']))))"
    )
    # Test social worker program
    program.data_collecting_type.type = DataCollectingType.Type.SOCIAL
    program.data_collecting_type.save()
    payment_plan.excluded_ids = f"{households_individuals['hh1'].unicef_id}, {households_individuals['hh2'].unicef_id}"
    payment_plan.save()
    payment_plan.refresh_from_db()

    assert payment_plan.is_social_worker_program
    basic_query_2 = payment_plan.get_basic_query()
    assert (
        str(basic_query_2) == f"(AND: ('withdrawn', False), (NOT (AND: ('individuals__unicef_id__in', "
        f"['{households_individuals['hh1'].unicef_id}', '{households_individuals['hh2'].unicef_id}']))))"
    )
