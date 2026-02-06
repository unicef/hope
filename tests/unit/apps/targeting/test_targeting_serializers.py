from typing import Any

import pytest
from rest_framework.test import APIRequestFactory

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FlexibleAttributeFactory,
    FlexibleAttributeForPDUFactory,
    PaymentPlanFactory,
    PeriodicFieldDataFactory,
    ProgramFactory,
)
from hope.apps.targeting.api.serializers import TargetingCriteriaRuleSerializer
from hope.apps.targeting.api.utils import filter_choices, get_field_by_name
from hope.models import (
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db: Any) -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def payment_plan(db: Any) -> Any:
    return PaymentPlanFactory()


@pytest.fixture
def rule(payment_plan: Any) -> TargetingCriteriaRule:
    return TargetingCriteriaRule.objects.create(payment_plan=payment_plan)


@pytest.fixture
def serializer_data(rule: TargetingCriteriaRule) -> dict:
    return TargetingCriteriaRuleSerializer(instance=rule).data


@pytest.fixture
def api_request_factory() -> APIRequestFactory:
    return APIRequestFactory()


def test_serialize_not_flex_field_household_filter_arrange_act_assert(
    rule: TargetingCriteriaRule,
    payment_plan: Any,
) -> None:
    filter_data = {
        "comparison_method": "EQUALS",
        "arguments": [2],
        "field_name": "size",
        "flex_field_classification": "NOT_FLEX_FIELD",
    }
    rule_filter = TargetingCriteriaRuleFilter.objects.create(**filter_data, targeting_criteria_rule=rule)
    data = TargetingCriteriaRuleSerializer(instance=rule).data

    assert data["household_ids"] == ""
    assert data["individual_ids"] == ""
    assert data["individuals_filters_blocks"] == []

    hh_block = data["households_filters_blocks"][0]
    assert hh_block["comparison_method"] == "EQUALS"
    assert hh_block["flex_field_classification"] == "NOT_FLEX_FIELD"
    assert hh_block["field_name"] == "size"
    assert hh_block["arguments"] == [2]

    field_attribute = hh_block["field_attribute"]
    expected = filter_choices(
        get_field_by_name(rule_filter.field_name, payment_plan),
        rule_filter.arguments,
    )

    field_attribute.pop("id")
    assert field_attribute == {
        "type": expected["type"],
        "name": expected["name"],
        "labels": [{"language": k, "label": v} for k, v in expected["label"].items()],
        "label_en": expected["label"]["English(EN)"],
        "hint": expected["hint"],
        "choices": expected["choices"],
        "associated_with": expected["associated_with"],
        "is_flex_field": False,
        "pdu_data": None,
    }


def test_serialize_not_flex_field_individual_filter_arrange_act_assert(
    rule: TargetingCriteriaRule,
    payment_plan: Any,
) -> None:
    filter_data = {
        "comparison_method": "EQUALS",
        "arguments": [2],
        "field_name": "size",
        "flex_field_classification": "NOT_FLEX_FIELD",
    }
    ind_block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=rule)
    rule_filter = TargetingIndividualBlockRuleFilter.objects.create(**filter_data, individuals_filters_block=ind_block)
    data = TargetingCriteriaRuleSerializer(instance=rule).data

    assert data["household_ids"] == ""
    assert data["individual_ids"] == ""
    assert data["households_filters_blocks"] == []

    block = data["individuals_filters_blocks"][0]
    assert block["target_only_hoh"] is False

    ind_filter = block["individual_block_filters"][0]
    assert ind_filter["comparison_method"] == "EQUALS"
    assert ind_filter["flex_field_classification"] == "NOT_FLEX_FIELD"
    assert ind_filter["field_name"] == "size"
    assert ind_filter["arguments"] == [2]

    field_attribute = ind_filter["field_attribute"]
    expected = filter_choices(
        get_field_by_name(rule_filter.field_name, payment_plan),
        rule_filter.arguments,
    )

    field_attribute.pop("id")
    assert field_attribute == {
        "type": expected["type"],
        "name": expected["name"],
        "labels": [{"language": k, "label": v} for k, v in expected["label"].items()],
        "label_en": expected["label"]["English(EN)"],
        "hint": expected["hint"],
        "choices": expected["choices"],
        "associated_with": expected["associated_with"],
        "is_flex_field": False,
        "pdu_data": None,
    }


def test_serialize_flex_field_household_arrange_act_assert(
    rule: TargetingCriteriaRule,
) -> None:
    flex_field = FlexibleAttributeFactory(
        name="flex_field",
        label={"English(EN)": "Test Flex"},
        associated_with=0,  # "Household"
    )
    TargetingCriteriaRuleFilter.objects.create(
        comparison_method="EQUALS",
        arguments=["test_value"],
        field_name="flex_field",
        flex_field_classification="FLEX_FIELD_BASIC",
        targeting_criteria_rule=rule,
    )

    data = TargetingCriteriaRuleSerializer(instance=rule).data

    hh_block = data["households_filters_blocks"][0]
    field_attribute = hh_block["field_attribute"]

    assert field_attribute == {
        "id": str(flex_field.id),
        "type": flex_field.type,
        "name": flex_field.name,
        "labels": [{"language": "English(EN)", "label": "Test Flex"}],
        "label_en": "Test Flex",
        "hint": "{}",
        "choices": [],
        "associated_with": "Household",
        "is_flex_field": True,
        "pdu_data": None,
    }


def test_serialize_flex_field_individual_arrange_act_assert(
    rule: TargetingCriteriaRule,
) -> None:
    flex_field = FlexibleAttributeFactory(
        name="flex_field",
        label={"English(EN)": "Test Flex"},
        associated_with=1,  # "Individual"
    )
    ind_block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=rule)
    TargetingIndividualBlockRuleFilter.objects.create(
        comparison_method="EQUALS",
        arguments=["test_value"],
        field_name="flex_field",
        flex_field_classification="FLEX_FIELD_BASIC",
        individuals_filters_block=ind_block,
    )
    data = TargetingCriteriaRuleSerializer(instance=rule).data

    ind_filter = data["individuals_filters_blocks"][0]["individual_block_filters"][0]
    field_attribute = ind_filter["field_attribute"]

    assert field_attribute == {
        "id": str(flex_field.id),
        "type": flex_field.type,
        "name": flex_field.name,
        "labels": [{"language": "English(EN)", "label": "Test Flex"}],
        "label_en": "Test Flex",
        "hint": "{}",
        "choices": [],
        "associated_with": "Individual",
        "is_flex_field": True,
        "pdu_data": None,
    }


def test_serialize_pdu_flex_field_arrange_act_assert(
    rule: TargetingCriteriaRule,
    business_area: Any,
    api_request_factory: APIRequestFactory,
) -> None:
    program = ProgramFactory(business_area=business_area)
    pdu_data = PeriodicFieldDataFactory(
        subtype="STRING",
        number_of_rounds=2,
        rounds_names=["January", "February"],
    )
    pdu_field = FlexibleAttributeForPDUFactory(
        name="pdu_field",
        program=program,
        label={"English(EN)": "PDU Field"},
        pdu_data=pdu_data,
    )
    ind_block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=rule)
    TargetingIndividualBlockRuleFilter.objects.create(
        comparison_method="EQUALS",
        arguments=["test_value"],
        field_name="pdu_field",
        flex_field_classification="FLEX_FIELD_PDU",
        round_number=2,
        individuals_filters_block=ind_block,
    )

    request = api_request_factory.get("/")
    request.parser_context = {
        "kwargs": {
            "business_area_slug": business_area.slug,
            "program_slug": program.slug,
        }
    }

    data = TargetingCriteriaRuleSerializer(instance=rule, context={"request": request}).data
    field_attribute = data["individuals_filters_blocks"][0]["individual_block_filters"][0]["field_attribute"]

    assert field_attribute == {
        "id": str(pdu_field.id),
        "type": pdu_field.type,
        "name": pdu_field.name,
        "labels": [{"language": "English(EN)", "label": "PDU Field"}],
        "label_en": "PDU Field",
        "hint": "{}",
        "choices": [],
        "associated_with": "Individual",
        "is_flex_field": True,
        "pdu_data": {
            "subtype": pdu_data.subtype,
            "number_of_rounds": pdu_data.number_of_rounds,
            "rounds_names": pdu_data.rounds_names,
        },
    }
