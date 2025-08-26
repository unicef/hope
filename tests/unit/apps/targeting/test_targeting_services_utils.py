from django.test import TestCase
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory

from hope.models.household import Household
from hope.models.individual import Individual
from hope.models.targeting_collector_block_rule_filter import (
    TargetingCollectorBlockRuleFilter,
)
from hope.models.targeting_collector_rule_filter_block import TargetingCollectorRuleFilterBlock
from hope.models.targeting_individual_block_rule_filter import TargetingIndividualBlockRuleFilter
from hope.models.targeting_criteria_rule_filter import TargetingCriteriaRuleFilter
from hope.models.targeting_individual_rule_filter_block import TargetingIndividualRuleFilterBlock
from hope.models.targeting_criteria_rule import TargetingCriteriaRule
from hope.apps.targeting.services.utils import (
    from_input_to_targeting_criteria,
    get_existing_unicef_ids,
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

        cls.pp = PaymentPlanFactory()

    def test_get_unicef_ids(self) -> None:
        ids_1 = get_existing_unicef_ids(f"{self.hh1},HH-invalid", Household, self.program)
        assert ids_1 == f"{self.hh1}"

        ids_2 = get_existing_unicef_ids(f" {self.hh1}, {self.hh2} ", Household, self.program)
        assert ids_2 == f"{self.hh1}, {self.hh2}"

        ids_3 = get_existing_unicef_ids(f"{self.ind1}, IND-000", Individual, self.program)
        assert ids_3 == f"{self.ind1}"

        ids_4 = get_existing_unicef_ids(f"{self.ind1}, {self.ind2}, HH-2", Individual, self.program)
        assert ids_4 == f"{self.ind1}, {self.ind2}"

    def test_from_input_to_targeting_criteria(self) -> None:
        assert TargetingCriteriaRule.objects.count() == 0
        assert TargetingCriteriaRuleFilter.objects.count() == 0
        assert TargetingIndividualRuleFilterBlock.objects.count() == 0
        assert TargetingIndividualBlockRuleFilter.objects.count() == 0
        assert TargetingCollectorRuleFilterBlock.objects.count() == 0
        assert TargetingCollectorBlockRuleFilter.objects.count() == 0

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
        from_input_to_targeting_criteria(targeting_criteria_input, self.program, self.pp)

        assert TargetingCriteriaRule.objects.count() == 1
        assert TargetingCriteriaRuleFilter.objects.count() == 1
        assert TargetingIndividualRuleFilterBlock.objects.count() == 1
        assert TargetingIndividualBlockRuleFilter.objects.count() == 1
        assert TargetingCollectorRuleFilterBlock.objects.count() == 1
        assert TargetingCollectorBlockRuleFilter.objects.count() == 1

        assert TargetingCriteriaRule.objects.first().household_ids == self.hh1.unicef_id
        assert TargetingCriteriaRule.objects.first().individual_ids == self.ind2.unicef_id

        assert TargetingCriteriaRuleFilter.objects.first().field_name == "size"
        assert TargetingCriteriaRuleFilter.objects.first().arguments == [2]

        assert TargetingIndividualBlockRuleFilter.objects.first().field_name == "age_at_registration"
        assert TargetingIndividualBlockRuleFilter.objects.first().arguments == [1, 99]

        assert TargetingCollectorBlockRuleFilter.objects.first().field_name == "mobile_phone_number__test_data"
        assert TargetingCollectorBlockRuleFilter.objects.first().arguments == [True]
