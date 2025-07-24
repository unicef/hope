from django.test import TestCase

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import PaymentPlanFactory

from hct_mis_api.apps.targeting.api.serializers import TargetingCriteriaRuleSerializer
from hct_mis_api.apps.targeting.models import (
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
)


class TargetingCriteriaSerializerTest(TestCase):
    def test_targeting_criteria_serializer(self) -> None:
        create_afghanistan()
        rule = TargetingCriteriaRule.objects.create(payment_plan=PaymentPlanFactory())
        hh_rule_data = {
            "comparison_method": "EQUALS",
            "arguments": [2],
            "field_name": "size",
            "flex_field_classification": "NOT_FLEX_FIELD",
        }
        # households_filters_blocks
        TargetingCriteriaRuleFilter.objects.create(**hh_rule_data, targeting_criteria_rule=rule)

        data = TargetingCriteriaRuleSerializer(instance=rule).data

        self.assertEqual(data["household_ids"], "")
        self.assertEqual(data["individual_ids"], "")
        self.assertEqual(data["individuals_filters_blocks"], [])
        self.assertEqual(data["collectors_filters_blocks"], [])
        self.assertEqual(data["households_filters_blocks"][0]["comparison_method"], "EQUALS")
        self.assertEqual(data["households_filters_blocks"][0]["flex_field_classification"], "NOT_FLEX_FIELD")
        self.assertEqual(data["households_filters_blocks"][0]["field_name"], "size")
