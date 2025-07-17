from django.test import TestCase

from hct_mis_api.apps.targeting.api.serializers import TargetingCriteriaRuleSerializer
from hct_mis_api.apps.targeting.models import (
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
)


class TargetingCriteriaSerializerTest(TestCase):
    def test_targeting_criteria_serializer(self) -> None:
        rule = TargetingCriteriaRule.objects.create()
        hh_rule_data = {
            "comparison_method": "EQUALS",
            "arguments": [2],
            "field_name": "size",
            "flex_field_classification": "NOT_FLEX_FIELD",
        }
        # households_filters_blocks
        TargetingCriteriaRuleFilter.objects.create(**hh_rule_data, targeting_criteria_rule=rule)

        data = TargetingCriteriaRuleSerializer(instance=rule).data

        self.assertFalse(data["flag_exclude_if_active_adjudication_ticket"])
        self.assertFalse(data["flag_exclude_if_on_sanction_list"])
        rule = data["rules"][0]
        self.assertEqual(rule["household_ids"], "")
        self.assertEqual(rule["individual_ids"], "")
        self.assertEqual(rule["individuals_filters_blocks"], [])
        self.assertEqual(rule["collectors_filters_blocks"], [])
        self.assertEqual(rule["households_filters_blocks"][0]["comparison_method"], "EQUALS")
        self.assertEqual(rule["households_filters_blocks"][0]["flex_field_classification"], "NOT_FLEX_FIELD")
        self.assertEqual(rule["households_filters_blocks"][0]["field_name"], "size")
