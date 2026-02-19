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


@pytest.fixture
def households(business_area, program):
    def _household(birth_date=None, size=1, residence_status="HOST", first_registration_date="1900-01-01"):
        hh = HouseholdFactory(
            business_area=business_area,
            program=program,
            size=size,
            residence_status=residence_status,
            first_registration_date=timezone.make_aware(datetime.strptime(first_registration_date, "%Y-%m-%d"), utc),
        )
        if birth_date:
            individual = hh.head_of_household
            individual.birth_date = birth_date
            individual.save()
        if size > 1:
            IndividualFactory.create_batch(
                size - 1,  # one Head of household are created in HouseholdFactory by default
                birth_date=birth_date,
                business_area=business_area,
                household=hh,
            )

        return hh

    hh_50 = _household("1970-09-29")
    _household("1991-11-18")
    _household("1991-11-18")
    hh_size_2 = _household("1991-11-18", size=2, residence_status="REFUGEE", first_registration_date="2001-01-01")
    return {
        "all": [hh_50, hh_size_2],
        "household_50_yo": hh_50,
        "household_size_2": hh_size_2,
        "household_refugee": hh_size_2,
    }


@pytest.fixture
def households_flex(business_area):
    # create flex attributes
    FlexibleAttributeFactory(
        name="total_households_h_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
        type=FlexibleAttribute.INTEGER,
    )
    FlexibleAttributeFactory(
        name="treatment_facility_h_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
        type=FlexibleAttribute.SELECT_MANY,
    )
    FlexibleAttributeFactory(
        name="other_treatment_facility_h_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
        type=FlexibleAttribute.STRING,
    )
    FlexibleAttributeFactory(
        name="muac_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        type=FlexibleAttribute.DECIMAL,
    )

    # create households with flex fields
    hh_2 = HouseholdFactory(
        size=1,
        business_area=business_area,
        flex_fields={
            "total_households_h_f": 2,
            "treatment_facility_h_f": ["government_health_center", "other_public", "private_doctor"],
            "other_treatment_facility_h_f": "testing other",
        },
    )

    hh_4 = HouseholdFactory(
        size=1,
        business_area=business_area,
        flex_fields={
            "total_households_h_f": 4,
            "treatment_facility_h_f": ["government_health_center", "other_public"],
        },
    )

    HouseholdFactory(
        size=1,
        business_area=business_area,
        flex_fields={"ddd": 3, "treatment_facility_h_f": []},
    )

    return {
        "household_total_households_2": hh_2,
        "household_total_households_4": hh_4,
        "other_treatment_facility": hh_2,
    }


@pytest.fixture
def households_pdu(user, business_area):
    program = ProgramFactory(
        name="Test Program for PDU Flex Rule Filter",
        business_area=business_area,
    )
    program_cycle = ProgramCycleFactory(program=program)

    # Create PDU flex fields
    pdu_string = FlexibleAttributeForPDUFactory(
        program=program,
        label="PDU Field STRING",
        pdu_data=PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.STRING, number_of_rounds=2, rounds_names=["Round 1", "Round 2"]
        ),
    )
    pdu_decimal = FlexibleAttributeForPDUFactory(
        program=program,
        label="PDU Field DECIMAL",
        pdu_data=PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL, number_of_rounds=1, rounds_names=["Round 1"]
        ),
    )
    pdu_date = FlexibleAttributeForPDUFactory(
        program=program,
        label="PDU Field DATE",
        pdu_data=PeriodicFieldDataFactory(subtype=PeriodicFieldData.DATE, number_of_rounds=1, rounds_names=["Round 1"]),
    )
    pdu_bool = FlexibleAttributeForPDUFactory(
        program=program,
        label="PDU Field BOOLEAN",
        pdu_data=PeriodicFieldDataFactory(subtype=PeriodicFieldData.BOOL, number_of_rounds=1, rounds_names=["Round 1"]),
    )

    # Create households with individuals
    def create_hh(flex_data):
        hh = HouseholdFactory(
            size=1,
            business_area=business_area,
            program=program,
        )
        ind = hh.head_of_household
        ind.flex_fields = flex_data
        ind.save()
        return hh, ind

    ind1_data = {
        pdu_string.name: {"1": {"value": None}, "2": {"value": None}},
        pdu_decimal.name: {"1": {"value": 2.5}},
        pdu_date.name: {"1": {"value": "2020-10-10"}},
        pdu_bool.name: {"1": {"value": True}},
    }
    hh1, ind1 = create_hh(ind1_data)

    ind2_data = {
        pdu_string.name: {"1": {"value": "some value", "collection_date": "2020-10-10"}, "2": {"value": None}},
        pdu_decimal.name: {"1": {"value": 3}},
        pdu_date.name: {"1": {"value": None}},
        pdu_bool.name: {"1": {"value": True}},
    }
    hh2, ind2 = create_hh(ind2_data)

    ind3_data = {
        pdu_string.name: {"1": {"value": "different value", "collection_date": "2020-10-10"}, "2": {"value": None}},
        pdu_decimal.name: {"1": {"value": 4}},
        pdu_date.name: {"1": {"value": "2020-02-10"}},
        pdu_bool.name: {"1": {"value": None}},
    }
    hh3, ind3 = create_hh(ind3_data)

    ind4_data = {
        pdu_string.name: {"1": {"value": "other value", "collection_date": "2020-10-10"}, "2": {"value": None}},
        pdu_decimal.name: {"1": {"value": None}},
        pdu_date.name: {"1": {"value": "2022-10-10"}},
        pdu_bool.name: {"1": {"value": False}},
    }
    hh4, ind4 = create_hh(ind4_data)

    return {
        "user": user,
        "program": program,
        "program_cycle": program_cycle,
        "individuals": [ind1, ind2, ind3, ind4],
        "pdu_string": pdu_string,
        "pdu_decimal": pdu_decimal,
        "pdu_date": pdu_date,
        "pdu_boolean": pdu_bool,
    }


def get_individuals_queryset(individuals):
    return Individual.objects.filter(pk__in=[ind.pk for ind in individuals])


def test_wrong_arguments_count_validation():
    for args in ([2, 1], [], None):
        rule_filter = TargetingCriteriaRuleFilter(
            comparison_method="EQUALS",
            field_name="size",
            arguments=args,
        )
        with pytest.raises(ValidationError):
            rule_filter.get_query()


@freeze_time("2020-10-10")
def test_rule_filter_age_equal(households):
    rule_filter = TargetingIndividualBlockRuleFilter(
        comparison_method="EQUALS",
        field_name="age",
        arguments=[50],
    )
    queryset = Individual.objects.filter(rule_filter.get_query())
    assert queryset.count() == 1
    assert households["household_50_yo"].pk == queryset.first().household.pk


@freeze_time("2020-10-10")
def test_rule_filter_age_not_equal(households):
    rule_filter = TargetingIndividualBlockRuleFilter(
        comparison_method="NOT_EQUALS",
        field_name="age",
        arguments=[50],
    )
    queryset = Individual.objects.filter(rule_filter.get_query())
    assert queryset.count() == 4
    assert households["household_50_yo"].pk not in [h.household.pk for h in queryset]


@freeze_time("2020-10-10")
def test_rule_filter_age_range_1_49(households):
    rule_filter = TargetingIndividualBlockRuleFilter(
        comparison_method="RANGE",
        field_name="age",
        arguments=[1, 49],
    )
    queryset = Individual.objects.filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 4
    assert households["household_50_yo"].pk not in [h.household.pk for h in queryset]


@freeze_time("2020-10-10")
def test_rule_filter_age_range_1_50(households):
    rule_filter = TargetingIndividualBlockRuleFilter(
        comparison_method="RANGE",
        field_name="age",
        arguments=[1, 50],
    )
    queryset = Individual.objects.filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 5
    assert households["household_50_yo"].pk in [h.household.pk for h in queryset]


@freeze_time("2020-10-10")
def test_rule_filter_age_gt_40(households):
    rule_filter = TargetingIndividualBlockRuleFilter(
        comparison_method="GREATER_THAN",
        field_name="age",
        arguments=[40],
    )
    queryset = Individual.objects.filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 1
    assert households["household_50_yo"].pk in [h.household.pk for h in queryset]


@freeze_time("2020-10-10")
def test_rule_filter_age_lt_40(households):
    rule_filter = TargetingIndividualBlockRuleFilter(
        comparison_method="LESS_THAN",
        field_name="age",
        arguments=[40],
    )
    queryset = Individual.objects.filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 4
    assert households["household_50_yo"].pk not in [h.household.pk for h in queryset]


@freeze_time("2020-09-28")
def test_rule_filter_age_lt_49_should_contains_person_born_in_proper_year_before_birthday(households):
    rule_filter = TargetingIndividualBlockRuleFilter(
        comparison_method="LESS_THAN",
        field_name="age",
        arguments=[49],
    )

    queryset = Individual.objects.filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 5
    assert households["household_50_yo"].pk in [h.household.pk for h in queryset]


@freeze_time("2020-09-29")
def test_rule_filter_age_lt_49_shouldn_t_contains_person_born_in_proper_year_after_and_during_birthday(households):
    rule_filter = TargetingIndividualBlockRuleFilter(
        comparison_method="LESS_THAN",
        field_name="age",
        arguments=[49],
    )
    queryset = Individual.objects.filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 4
    assert households["household_50_yo"].pk not in [h.household.pk for h in queryset]


def test_rule_filter_size_equals(households):
    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="EQUALS",
        field_name="size",
        arguments=[2],
    )
    queryset = (
        Household.objects.filter(pk__in=[h.pk for h in households["all"]]).filter(rule_filter.get_query()).distinct()
    )
    assert queryset.count() == 1
    assert households["household_size_2"].pk in [h.pk for h in queryset]


def test_rule_filter_size_not_equals(households):
    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="NOT_EQUALS",
        field_name="size",
        arguments=[2],
    )
    queryset = (
        Household.objects.filter(pk__in=[h.pk for h in households["all"]]).filter(rule_filter.get_query()).distinct()
    )
    assert queryset.count() == 1
    assert households["household_size_2"].pk not in [h.pk for h in queryset]


def test_rule_filter_size_in_range_0_1(households):
    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="RANGE",
        field_name="size",
        arguments=[0, 1],
    )
    queryset = (
        Household.objects.filter(pk__in=[h.pk for h in households["all"]]).filter(rule_filter.get_query()).distinct()
    )
    assert queryset.count() == 1
    assert households["household_size_2"].pk not in [h.pk for h in queryset]


def test_rule_filter_size_not_in_range_0_1(households):
    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="NOT_IN_RANGE",
        field_name="size",
        arguments=[0, 1],
    )
    queryset = (
        Household.objects.filter(pk__in=[h.pk for h in households["all"]]).filter(rule_filter.get_query()).distinct()
    )
    assert queryset.count() == 1
    assert households["household_size_2"].pk in [h.pk for h in queryset]


def test_rule_filter_size_gte_2(households):
    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="GREATER_THAN",
        field_name="size",
        arguments=[2],
    )
    queryset = (
        Household.objects.filter(pk__in=[h.pk for h in households["all"]]).filter(rule_filter.get_query()).distinct()
    )
    assert queryset.count() == 1
    assert households["household_size_2"].pk in [h.pk for h in queryset]


def test_rule_filter_size_lte_1(households):
    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="LESS_THAN",
        field_name="size",
        arguments=[1],
    )
    queryset = (
        Household.objects.filter(pk__in=[h.pk for h in households["all"]]).filter(rule_filter.get_query()).distinct()
    )
    assert queryset.count() == 1
    assert households["household_size_2"].pk not in [h.pk for h in queryset]


def test_rule_filter_residence_status_equals(households):
    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="EQUALS",
        field_name="residence_status",
        arguments=["REFUGEE"],
    )
    queryset = (
        Household.objects.filter(pk__in=[h.pk for h in households["all"]]).filter(rule_filter.get_query()).distinct()
    )
    assert queryset.count() == 1
    assert households["household_refugee"].pk in [h.pk for h in queryset]


def test_rule_filter_residence_status_not_equals(households):
    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="NOT_EQUALS",
        field_name="residence_status",
        arguments=["REFUGEE"],
    )
    queryset = (
        Household.objects.filter(pk__in=[h.pk for h in households["all"]]).filter(rule_filter.get_query()).distinct()
    )
    assert queryset.count() == 1
    assert households["household_refugee"].pk not in [h.pk for h in queryset]


def test_rule_filter_registration_date_gte(households):
    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="GREATER_THAN",
        field_name="first_registration_date",
        arguments=["2000-01-01T00:00:00Z"],
    )
    queryset = (
        Household.objects.filter(pk__in=[h.pk for h in households["all"]]).filter(rule_filter.get_query()).distinct()
    )
    assert queryset.count() == 1
    assert households["household_size_2"].pk in [h.pk for h in queryset]


def test_rule_filter_household_total_households_4(households_flex):
    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="EQUALS",
        field_name="total_households_h_f",
        arguments=[4],
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
    )
    queryset = Household.objects.filter(rule_filter.get_query())
    assert queryset.count() == 1
    assert households_flex["household_total_households_4"].pk == queryset.first().pk


def test_rule_filter_select_multiple_treatment_facility(households_flex):
    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="CONTAINS",
        field_name="treatment_facility_h_f",
        arguments=["other_public", "private_doctor"],
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
    )
    queryset = Household.objects.filter(rule_filter.get_query())
    assert queryset.count() == 1


def test_rule_filter_select_multiple_treatment_facility_2(households_flex):
    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="CONTAINS",
        field_name="treatment_facility_h_f",
        arguments=["other_public", "government_health_center"],
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
    )
    queryset = Household.objects.filter(rule_filter.get_query())
    assert queryset.count() == 2


def test_rule_filter_select_multiple_treatment_facility_not_contains(households_flex):
    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="NOT_CONTAINS",
        field_name="treatment_facility_h_f",
        arguments=["other_public", "government_health_center"],
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
    )
    queryset = Household.objects.filter(rule_filter.get_query())
    assert queryset.count() == 1


def test_rule_filter_string_contains(households_flex):
    rule_filter = TargetingCriteriaRuleFilter(
        comparison_method="CONTAINS",
        field_name="other_treatment_facility_h_f",
        arguments=["other"],
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_BASIC,
    )
    queryset = Household.objects.filter(rule_filter.get_query())
    assert queryset.count() == 1


def test_rule_filter_pdu_string_contains(households_pdu):
    payment_plan = PaymentPlanFactory(program_cycle=households_pdu["program_cycle"], created_by=households_pdu["user"])
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)

    rule_filter = TargetingIndividualBlockRuleFilter(
        individuals_filters_block=block,
        comparison_method="CONTAINS",
        field_name=households_pdu["pdu_string"].name,
        arguments=["some"],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    queryset = get_individuals_queryset(households_pdu["individuals"]).filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 1
    assert households_pdu["individuals"][1] in queryset


def test_rule_filter_pdu_string_is_null(households_pdu):
    payment_plan = PaymentPlanFactory(program_cycle=households_pdu["program_cycle"], created_by=households_pdu["user"])
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)

    rule_filter = TargetingIndividualBlockRuleFilter(
        individuals_filters_block=block,
        comparison_method="IS_NULL",
        field_name=households_pdu["pdu_string"].name,
        arguments=[None],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    queryset = get_individuals_queryset(households_pdu["individuals"]).filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 1
    assert households_pdu["individuals"][0] in queryset


def test_rule_filter_pdu_decimal_range(households_pdu):
    payment_plan = PaymentPlanFactory(program_cycle=households_pdu["program_cycle"], created_by=households_pdu["user"])
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)

    rule_filter = TargetingIndividualBlockRuleFilter(
        individuals_filters_block=block,
        comparison_method="RANGE",
        field_name=households_pdu["pdu_decimal"].name,
        arguments=["2", "3"],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    queryset = get_individuals_queryset(households_pdu["individuals"]).filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 2
    assert households_pdu["individuals"][0] in queryset
    assert households_pdu["individuals"][1] in queryset


def test_rule_filter_pdu_decimal_greater_than(households_pdu):
    payment_plan = PaymentPlanFactory(program_cycle=households_pdu["program_cycle"], created_by=households_pdu["user"])
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)

    rule_filter = TargetingIndividualBlockRuleFilter(
        individuals_filters_block=block,
        comparison_method="GREATER_THAN",
        field_name=households_pdu["pdu_decimal"].name,
        arguments=["2.5"],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    queryset = get_individuals_queryset(households_pdu["individuals"]).filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 3
    assert households_pdu["individuals"][0] in queryset
    assert households_pdu["individuals"][1] in queryset
    assert households_pdu["individuals"][2] in queryset


def test_rule_filter_pdu_decimal_less_than(households_pdu):
    payment_plan = PaymentPlanFactory(program_cycle=households_pdu["program_cycle"], created_by=households_pdu["user"])
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)

    rule_filter = TargetingIndividualBlockRuleFilter(
        individuals_filters_block=block,
        comparison_method="LESS_THAN",
        field_name=households_pdu["pdu_decimal"].name,
        arguments=["2.5"],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    queryset = get_individuals_queryset(households_pdu["individuals"]).filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 1
    assert households_pdu["individuals"][0] in queryset


def test_rule_filter_pdu_decimal_is_null(households_pdu):
    payment_plan = PaymentPlanFactory(program_cycle=households_pdu["program_cycle"], created_by=households_pdu["user"])
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)

    rule_filter = TargetingIndividualBlockRuleFilter(
        individuals_filters_block=block,
        comparison_method="IS_NULL",
        field_name=households_pdu["pdu_decimal"].name,
        arguments=[None],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    queryset = get_individuals_queryset(households_pdu["individuals"]).filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 1
    assert households_pdu["individuals"][3] in queryset


def test_rule_filter_pdu_date_range(households_pdu):
    payment_plan = PaymentPlanFactory(program_cycle=households_pdu["program_cycle"], created_by=households_pdu["user"])
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)

    rule_filter = TargetingIndividualBlockRuleFilter(
        individuals_filters_block=block,
        comparison_method="RANGE",
        field_name=households_pdu["pdu_date"].name,
        arguments=["2020-02-10", "2020-10-10"],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    queryset = get_individuals_queryset(households_pdu["individuals"]).filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 2
    assert households_pdu["individuals"][0] in queryset
    assert households_pdu["individuals"][2] in queryset


def test_rule_filter_pdu_date_greater_than(households_pdu):
    payment_plan = PaymentPlanFactory(program_cycle=households_pdu["program_cycle"], created_by=households_pdu["user"])
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)

    rule_filter = TargetingIndividualBlockRuleFilter(
        individuals_filters_block=block,
        comparison_method="GREATER_THAN",
        field_name=households_pdu["pdu_date"].name,
        arguments=["2020-10-11"],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    queryset = get_individuals_queryset(households_pdu["individuals"]).filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 1
    assert households_pdu["individuals"][3] in queryset


def test_rule_filter_pdu_date_less_than(households_pdu):
    payment_plan = PaymentPlanFactory(program_cycle=households_pdu["program_cycle"], created_by=households_pdu["user"])
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)

    rule_filter = TargetingIndividualBlockRuleFilter(
        individuals_filters_block=block,
        comparison_method="LESS_THAN",
        field_name=households_pdu["pdu_date"].name,
        arguments=["2020-10-11"],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    queryset = get_individuals_queryset(households_pdu["individuals"]).filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 2
    assert households_pdu["individuals"][0] in queryset
    assert households_pdu["individuals"][2] in queryset


def test_rule_filter_pdu_date_is_null(households_pdu):
    payment_plan = PaymentPlanFactory(program_cycle=households_pdu["program_cycle"], created_by=households_pdu["user"])
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)

    rule_filter = TargetingIndividualBlockRuleFilter(
        individuals_filters_block=block,
        comparison_method="IS_NULL",
        field_name=households_pdu["pdu_date"].name,
        arguments=[None],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    queryset = get_individuals_queryset(households_pdu["individuals"]).filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 1
    assert households_pdu["individuals"][1] in queryset


def test_rule_filter_pdu_boolean_true(households_pdu):
    payment_plan = PaymentPlanFactory(program_cycle=households_pdu["program_cycle"], created_by=households_pdu["user"])
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)

    rule_filter = TargetingIndividualBlockRuleFilter(
        individuals_filters_block=block,
        comparison_method="EQUALS",
        field_name=households_pdu["pdu_boolean"].name,
        arguments=[True],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    queryset = get_individuals_queryset(households_pdu["individuals"]).filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 2
    assert households_pdu["individuals"][0] in queryset
    assert households_pdu["individuals"][1] in queryset


def test_rule_filter_pdu_boolean_false(households_pdu):
    payment_plan = PaymentPlanFactory(program_cycle=households_pdu["program_cycle"], created_by=households_pdu["user"])
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)

    rule_filter = TargetingIndividualBlockRuleFilter(
        individuals_filters_block=block,
        comparison_method="EQUALS",
        field_name=households_pdu["pdu_boolean"].name,
        arguments=[False],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    queryset = get_individuals_queryset(households_pdu["individuals"]).filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 1
    assert households_pdu["individuals"][3] in queryset


def test_rule_filter_pdu_boolean_is_null(households_pdu):
    payment_plan = PaymentPlanFactory(program_cycle=households_pdu["program_cycle"], created_by=households_pdu["user"])
    tcr = TargetingCriteriaRule.objects.create(payment_plan=payment_plan)
    block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=tcr, target_only_hoh=False)

    rule_filter = TargetingIndividualBlockRuleFilter(
        individuals_filters_block=block,
        comparison_method="IS_NULL",
        field_name=households_pdu["pdu_boolean"].name,
        arguments=[None],
        round_number=1,
        flex_field_classification=FlexFieldClassification.FLEX_FIELD_PDU,
    )

    queryset = get_individuals_queryset(households_pdu["individuals"]).filter(rule_filter.get_query()).distinct()
    assert queryset.count() == 1
    assert households_pdu["individuals"][2] in queryset
