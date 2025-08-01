from django.test import TestCase
from rest_framework.test import APIRequestFactory

from extras.test_utils.factories.core import (
    create_afghanistan,
    PeriodicFieldDataFactory,
    FlexibleAttributeForPDUFactory,
)
from extras.test_utils.factories.payment import PaymentPlanFactory
from hct_mis_api.apps.core.models import PeriodicFieldData, FlexibleAttribute

from hct_mis_api.apps.targeting.api.serializers import TargetingCriteriaRuleSerializer
from hct_mis_api.apps.targeting.api.utils import filter_choices, get_field_by_name
from hct_mis_api.apps.targeting.models import (
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)
from test_utils.factories.program import ProgramFactory


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

        self.assertEqual(data["household_ids"], "")
        self.assertEqual(data["individual_ids"], "")
        self.assertEqual(data["individuals_filters_blocks"], [])
        self.assertEqual(data["collectors_filters_blocks"], [])
        self.assertEqual(data["households_filters_blocks"][0]["comparison_method"], "EQUALS")
        self.assertEqual(data["households_filters_blocks"][0]["flex_field_classification"], "NOT_FLEX_FIELD")
        self.assertEqual(data["households_filters_blocks"][0]["field_name"], "size")
        self.assertEqual(data["households_filters_blocks"][0]["arguments"], [2])
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
        self.assertEqual(field_attribute_data, expected_field_attribute_data)

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

        self.assertEqual(data["household_ids"], "")
        self.assertEqual(data["individual_ids"], "")
        self.assertEqual(data["households_filters_blocks"], [])
        self.assertEqual(data["collectors_filters_blocks"], [])
        self.assertEqual(data["individuals_filters_blocks"][0]["target_only_hoh"], False)
        self.assertEqual(
            data["individuals_filters_blocks"][0]["individual_block_filters"][0]["comparison_method"], "EQUALS"
        )
        self.assertEqual(
            data["individuals_filters_blocks"][0]["individual_block_filters"][0]["flex_field_classification"],
            "NOT_FLEX_FIELD",
        )
        self.assertEqual(data["individuals_filters_blocks"][0]["individual_block_filters"][0]["field_name"], "size")
        self.assertEqual(data["individuals_filters_blocks"][0]["individual_block_filters"][0]["arguments"], [2])
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
        self.assertEqual(field_attribute_data, expected_field_attribute_data)

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

        self.assertEqual(data["household_ids"], "")
        self.assertEqual(data["individual_ids"], "")
        self.assertEqual(data["individuals_filters_blocks"], [])
        self.assertEqual(data["collectors_filters_blocks"], [])
        self.assertEqual(data["households_filters_blocks"][0]["comparison_method"], "EQUALS")
        self.assertEqual(data["households_filters_blocks"][0]["flex_field_classification"], "FLEX_FIELD_BASIC")
        self.assertEqual(data["households_filters_blocks"][0]["field_name"], "flex_field")
        self.assertEqual(data["households_filters_blocks"][0]["arguments"], ["test_value"])
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
        self.assertEqual(field_attribute_data, expected_field_attribute_data)

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

        self.assertEqual(data["household_ids"], "")
        self.assertEqual(data["individual_ids"], "")
        self.assertEqual(data["households_filters_blocks"], [])
        self.assertEqual(data["collectors_filters_blocks"], [])
        self.assertEqual(data["individuals_filters_blocks"][0]["target_only_hoh"], False)
        self.assertEqual(
            data["individuals_filters_blocks"][0]["individual_block_filters"][0]["comparison_method"], "EQUALS"
        )
        self.assertEqual(
            data["individuals_filters_blocks"][0]["individual_block_filters"][0]["flex_field_classification"],
            "FLEX_FIELD_BASIC",
        )
        self.assertEqual(
            data["individuals_filters_blocks"][0]["individual_block_filters"][0]["field_name"], "flex_field"
        )
        self.assertEqual(
            data["individuals_filters_blocks"][0]["individual_block_filters"][0]["arguments"], ["test_value"]
        )
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
        self.assertEqual(field_attribute_data, expected_field_attribute_data)

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

        self.assertEqual(data["household_ids"], "")
        self.assertEqual(data["individual_ids"], "")
        self.assertEqual(data["households_filters_blocks"], [])
        self.assertEqual(data["collectors_filters_blocks"], [])
        self.assertEqual(
            data["individuals_filters_blocks"][0]["individual_block_filters"][0]["comparison_method"], "EQUALS"
        )
        self.assertEqual(
            data["individuals_filters_blocks"][0]["individual_block_filters"][0]["flex_field_classification"],
            "FLEX_FIELD_PDU",
        )
        self.assertEqual(
            data["individuals_filters_blocks"][0]["individual_block_filters"][0]["field_name"], "pdu_field"
        )
        self.assertEqual(
            data["individuals_filters_blocks"][0]["individual_block_filters"][0]["arguments"], ["test_value"]
        )
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
        self.assertEqual(field_attribute_data, expected_field_attribute_data)
