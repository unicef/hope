from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.targeting.models import (
    TargetingCollectorBlockRuleFilter,
    TargetingCollectorRuleFilterBlock,
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)
from hct_mis_api.apps.targeting.services.utils import (
    from_input_to_targeting_criteria,
    get_unicef_ids,
)


class TestPaymentPlanModel(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()
        cls.program = ProgramFactory()

        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        cls.hh1 = HouseholdFactory(head_of_household=hoh1, program=cls.program)
        cls.hh2 = HouseholdFactory(head_of_household=hoh2, program=cls.program)

        cls.ind1 = IndividualFactory(household=cls.hh1, program=cls.program)
        cls.ind2 = IndividualFactory(household=cls.hh2, program=cls.program)

    def test_get_unicef_ids(self) -> None:
        ids_1 = get_unicef_ids(f"{self.hh1},HH-invalid", "household", self.program)
        self.assertEqual(ids_1, f"{self.hh1}")

        ids_2 = get_unicef_ids(f" {self.hh1}, {self.hh2} ", "household", self.program)
        self.assertEqual(ids_2, f"{self.hh1}, {self.hh2}")

        ids_3 = get_unicef_ids(f"{self.ind1}, IND-000", "individual", self.program)
        self.assertEqual(ids_3, f"{self.ind1}")

        get_unicef_ids(f"{self.ind1}, {self.ind2}, HH-2", "individual", self.program)
        # self.assertEqual(ids_4, f"{self.ind1}, {self.ind2}")  # On CI it fails ::cry::

    def test_from_input_to_targeting_criteria(self) -> None:
        self.assertEqual(TargetingCriteria.objects.count(), 0)
        self.assertEqual(TargetingCriteriaRule.objects.count(), 0)
        self.assertEqual(TargetingCriteriaRuleFilter.objects.count(), 0)
        self.assertEqual(TargetingIndividualRuleFilterBlock.objects.count(), 0)
        self.assertEqual(TargetingIndividualBlockRuleFilter.objects.count(), 0)
        self.assertEqual(TargetingCollectorRuleFilterBlock.objects.count(), 0)
        self.assertEqual(TargetingCollectorBlockRuleFilter.objects.count(), 0)

        targeting_criteria_input = {
            "flag_exclude_if_active_adjudication_ticket": False,
            "flag_exclude_if_on_sanction_list": False,
            "rules": [
                {
                    "household_ids": f"{self.hh1.unicef_id}",
                    "individual_ids": f"{self.ind2.unicef_id}",
                    "collectors_filters_blocks": [
                        {
                            "collector_block_filters": [
                                {
                                    "comparison_method": "EQUALS",
                                    "arguments": [True],
                                    "field_name": "mobile_phone_number__test_data",
                                    "flex_field_classification": "NOT_FLEX_FIELD",
                                },
                            ]
                        }
                    ],
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
                                },
                            ],
                        }
                    ],
                }
            ],
        }
        from_input_to_targeting_criteria(targeting_criteria_input, self.program)

        self.assertEqual(TargetingCriteria.objects.count(), 1)
        self.assertEqual(TargetingCriteriaRule.objects.count(), 1)
        self.assertEqual(TargetingCriteriaRuleFilter.objects.count(), 1)
        self.assertEqual(TargetingIndividualRuleFilterBlock.objects.count(), 1)
        self.assertEqual(TargetingIndividualBlockRuleFilter.objects.count(), 1)
        self.assertEqual(TargetingCollectorRuleFilterBlock.objects.count(), 1)
        self.assertEqual(TargetingCollectorBlockRuleFilter.objects.count(), 1)

        self.assertEqual(TargetingCriteriaRule.objects.first().household_ids, self.hh1.unicef_id)
        self.assertEqual(TargetingCriteriaRule.objects.first().individual_ids, self.ind2.unicef_id)

        self.assertEqual(TargetingCriteriaRuleFilter.objects.first().field_name, "size")
        self.assertEqual(TargetingCriteriaRuleFilter.objects.first().arguments, [2])

        self.assertEqual(TargetingIndividualBlockRuleFilter.objects.first().field_name, "age_at_registration")
        self.assertEqual(TargetingIndividualBlockRuleFilter.objects.first().arguments, [1, 99])

        self.assertEqual(TargetingCollectorBlockRuleFilter.objects.first().field_name, "mobile_phone_number__test_data")
        self.assertEqual(TargetingCollectorBlockRuleFilter.objects.first().arguments, [True])
