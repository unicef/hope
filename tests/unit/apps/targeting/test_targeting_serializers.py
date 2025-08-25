from django.test import TestCase
from extras.test_utils.factories.core import (
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
)
from extras.test_utils.factories.payment import PaymentPlanFactory
from rest_framework.test import APIRequestFactory
from test_utils.factories.program import ProgramFactory

from models.core import FlexibleAttribute, PeriodicFieldData
from hope.apps.targeting.api.serializers import TargetingCriteriaRuleSerializer
from hope.apps.targeting.api.utils import filter_choices, get_field_by_name
from models.targeting import (
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)


class TargetingCriteriaSerializerTest(TestCase):
    def test_targeting_criteria_serializer_for_not_flex_field_on_hh(self) -> None:
        create_afghanistan()
        rule = TargetingCriteriaRule.objects.create(payment_plan=PaymentPlanFactory())
        # households_filters_blocks
        hh_rule_data = {
            "comparison_method": "EQUALS",
            "arguments": [2],
            "field_name": "size",
            "flex_field_classification": "NOT_FLEX_FIELD",
        }
        targeting_criteria_rule_filter = TargetingCriteriaRuleFilter.objects.create(
            **hh_rule_data,
            targeting_criteria_rule=rule,
        )

        data = TargetingCriteriaRuleSerializer(instance=rule).data

        assert data["household_ids"] == ""
        assert data["individual_ids"] == ""
        assert data["individuals_filters_blocks"] == []
        assert data["collectors_filters_blocks"] == []
        assert data["households_filters_blocks"][0]["comparison_method"] == "EQUALS"
        assert data["households_filters_blocks"][0]["flex_field_classification"] == "NOT_FLEX_FIELD"
        assert data["households_filters_blocks"][0]["field_name"] == "size"
        assert data["households_filters_blocks"][0]["arguments"] == [2]
        field_attribute_data = data["households_filters_blocks"][0]["field_attribute"]
        expected_result = filter_choices(
            get_field_by_name(targeting_criteria_rule_filter.field_name, rule.payment_plan),
            targeting_criteria_rule_filter.arguments,
        )
        expected_field_attribute_data = {
            "type": expected_result["type"],
            "name": expected_result["name"],
            "labels": [{"language": k, "label": v} for k, v in expected_result["label"].items()],
            "label_en": expected_result["label"]["English(EN)"],
            "hint": expected_result["hint"],
            "choices": expected_result["choices"],
            "associated_with": expected_result["associated_with"],
            "is_flex_field": False,
            "pdu_data": None,
        }
        field_attribute_data.pop("id")
        assert field_attribute_data == expected_field_attribute_data

    def test_targeting_criteria_serializer_for_not_flex_field_on_ind(self) -> None:
        create_afghanistan()
        rule = TargetingCriteriaRule.objects.create(payment_plan=PaymentPlanFactory())
        ind_rule_data = {
            "comparison_method": "EQUALS",
            "arguments": [2],
            "field_name": "size",
            "flex_field_classification": "NOT_FLEX_FIELD",
        }
        ind_block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=rule)
        targeting_criteria_rule_filter = TargetingIndividualBlockRuleFilter.objects.create(
            **ind_rule_data,
            individuals_filters_block=ind_block,
        )

        data = TargetingCriteriaRuleSerializer(instance=rule).data

        assert data["household_ids"] == ""
        assert data["individual_ids"] == ""
        assert data["households_filters_blocks"] == []
        assert data["collectors_filters_blocks"] == []
        assert not data["individuals_filters_blocks"][0]["target_only_hoh"]
        assert data["individuals_filters_blocks"][0]["individual_block_filters"][0]["comparison_method"] == "EQUALS"
        assert (
            data["individuals_filters_blocks"][0]["individual_block_filters"][0]["flex_field_classification"]
            == "NOT_FLEX_FIELD"
        )
        assert data["individuals_filters_blocks"][0]["individual_block_filters"][0]["field_name"] == "size"
        assert data["individuals_filters_blocks"][0]["individual_block_filters"][0]["arguments"] == [2]
        field_attribute_data = data["individuals_filters_blocks"][0]["individual_block_filters"][0]["field_attribute"]
        expected_result = filter_choices(
            get_field_by_name(targeting_criteria_rule_filter.field_name, rule.payment_plan),
            targeting_criteria_rule_filter.arguments,
        )
        expected_field_attribute_data = {
            "type": expected_result["type"],
            "name": expected_result["name"],
            "labels": [{"language": k, "label": v} for k, v in expected_result["label"].items()],
            "label_en": expected_result["label"]["English(EN)"],
            "hint": expected_result["hint"],
            "choices": expected_result["choices"],
            "associated_with": expected_result["associated_with"],
            "is_flex_field": False,
            "pdu_data": None,
        }
        field_attribute_data.pop("id")
        assert field_attribute_data == expected_field_attribute_data

    def test_targeting_criteria_serializer_for_flex_field_on_hh(self) -> None:
        create_afghanistan()
        rule = TargetingCriteriaRule.objects.create(payment_plan=PaymentPlanFactory())
        flex_field = FlexibleAttribute.objects.create(
            name="flex_field",
            type=FlexibleAttribute.STRING,
            label={"English(EN)": "Test Flex"},
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
        )
        # households_filters_blocks
        hh_rule_data = {
            "comparison_method": "EQUALS",
            "arguments": ["test_value"],
            "field_name": "flex_field",
            "flex_field_classification": "FLEX_FIELD_BASIC",
        }
        TargetingCriteriaRuleFilter.objects.create(**hh_rule_data, targeting_criteria_rule=rule)

        data = TargetingCriteriaRuleSerializer(instance=rule).data

        assert data["household_ids"] == ""
        assert data["individual_ids"] == ""
        assert data["individuals_filters_blocks"] == []
        assert data["collectors_filters_blocks"] == []
        assert data["households_filters_blocks"][0]["comparison_method"] == "EQUALS"
        assert data["households_filters_blocks"][0]["flex_field_classification"] == "FLEX_FIELD_BASIC"
        assert data["households_filters_blocks"][0]["field_name"] == "flex_field"
        assert data["households_filters_blocks"][0]["arguments"] == ["test_value"]
        field_attribute_data = data["households_filters_blocks"][0]["field_attribute"]
        expected_field_attribute_data = {
            "id": str(flex_field.id),
            "type": flex_field.type,
            "name": flex_field.name,
            "labels": [{"language": "English(EN)", "label": "Test Flex"}],
            "label_en": flex_field.label.get("English(EN)", ""),
            "hint": "{}",
            "choices": [],
            "associated_with": "Household",
            "is_flex_field": True,
            "pdu_data": None,
        }
        assert field_attribute_data == expected_field_attribute_data

    def test_targeting_criteria_serializer_for_flex_field_on_ind(self) -> None:
        create_afghanistan()
        rule = TargetingCriteriaRule.objects.create(payment_plan=PaymentPlanFactory())
        flex_field = FlexibleAttribute.objects.create(
            name="flex_field",
            type=FlexibleAttribute.STRING,
            label={"English(EN)": "Test Flex"},
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        )
        # individual_filters_blocks
        ind_rule_data = {
            "comparison_method": "EQUALS",
            "arguments": ["test_value"],
            "field_name": "flex_field",
            "flex_field_classification": "FLEX_FIELD_BASIC",
        }
        ind_block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=rule)
        TargetingIndividualBlockRuleFilter.objects.create(**ind_rule_data, individuals_filters_block=ind_block)

        data = TargetingCriteriaRuleSerializer(instance=rule).data

        assert data["household_ids"] == ""
        assert data["individual_ids"] == ""
        assert data["households_filters_blocks"] == []
        assert data["collectors_filters_blocks"] == []
        assert not data["individuals_filters_blocks"][0]["target_only_hoh"]
        assert data["individuals_filters_blocks"][0]["individual_block_filters"][0]["comparison_method"] == "EQUALS"
        assert (
            data["individuals_filters_blocks"][0]["individual_block_filters"][0]["flex_field_classification"]
            == "FLEX_FIELD_BASIC"
        )
        assert data["individuals_filters_blocks"][0]["individual_block_filters"][0]["field_name"] == "flex_field"
        assert data["individuals_filters_blocks"][0]["individual_block_filters"][0]["arguments"] == ["test_value"]
        field_attribute_data = data["individuals_filters_blocks"][0]["individual_block_filters"][0]["field_attribute"]
        expected_field_attribute_data = {
            "id": str(flex_field.id),
            "type": flex_field.type,
            "name": flex_field.name,
            "labels": [{"language": "English(EN)", "label": "Test Flex"}],
            "label_en": flex_field.label.get("English(EN)", ""),
            "hint": "{}",
            "choices": [],
            "associated_with": "Individual",
            "is_flex_field": True,
            "pdu_data": None,
        }
        assert field_attribute_data == expected_field_attribute_data

    def test_targeting_criteria_serializer_for_pdu_flex_field(self) -> None:
        afghanistan = create_afghanistan()
        rule = TargetingCriteriaRule.objects.create(payment_plan=PaymentPlanFactory())
        program = ProgramFactory(business_area=afghanistan)
        pdu_data = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=2,
            rounds_names=["January", "February"],
        )
        pdu_field = FlexibleAttributeForPDUFactory(
            name="pdu_field",
            program=program,
            label="PDU Field",
            pdu_data=pdu_data,
        )
        # individual_filters_blocks
        ind_rule_data = {
            "comparison_method": "EQUALS",
            "arguments": ["test_value"],
            "field_name": "pdu_field",
            "flex_field_classification": "FLEX_FIELD_PDU",
            "round_number": 2,
        }
        ind_block = TargetingIndividualRuleFilterBlock.objects.create(targeting_criteria_rule=rule)
        TargetingIndividualBlockRuleFilter.objects.create(**ind_rule_data, individuals_filters_block=ind_block)

        factory = APIRequestFactory()
        request = factory.get("/")
        request.parser_context = {
            "kwargs": {
                "business_area_slug": afghanistan.slug,
                "program_slug": program.slug,
            }
        }
        data = TargetingCriteriaRuleSerializer(instance=rule, context={"request": request}).data

        assert data["household_ids"] == ""
        assert data["individual_ids"] == ""
        assert data["households_filters_blocks"] == []
        assert data["collectors_filters_blocks"] == []
        assert data["individuals_filters_blocks"][0]["individual_block_filters"][0]["comparison_method"] == "EQUALS"
        assert (
            data["individuals_filters_blocks"][0]["individual_block_filters"][0]["flex_field_classification"]
            == "FLEX_FIELD_PDU"
        )
        assert data["individuals_filters_blocks"][0]["individual_block_filters"][0]["field_name"] == "pdu_field"
        assert data["individuals_filters_blocks"][0]["individual_block_filters"][0]["arguments"] == ["test_value"]
        field_attribute_data = data["individuals_filters_blocks"][0]["individual_block_filters"][0]["field_attribute"]
        expected_field_attribute_data = {
            "id": str(pdu_field.id),
            "type": pdu_field.type,
            "name": pdu_field.name,
            "labels": [{"language": "English(EN)", "label": "PDU Field"}],
            "label_en": pdu_field.label.get("English(EN)", ""),
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
        assert field_attribute_data == expected_field_attribute_data
