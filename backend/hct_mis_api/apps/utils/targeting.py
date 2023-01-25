from typing import Type, TypeVar

from hct_mis_api.apps.targeting.criteria.models import TargetingCriteria
from hct_mis_api.apps.targeting.models import (
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)

T = TypeVar("T", bound=TargetingCriteria)


class TargetingCriteriaProxy:
    @staticmethod
    def from_dict(data: dict, type: Type[T], target_only_hoh: bool) -> T:
        criteria_obj = type()
        criteria_obj.save()
        for rule_data in data.get("rules", []):
            rule_obj = TargetingCriteriaRule(targeting_criteria=criteria_obj)
            rule_obj.save()
            for filter_data in rule_data.get("filters", []):
                rule_filter_obj = TargetingCriteriaRuleFilter(targeting_criteria_rule=rule_obj, **filter_data)
                rule_filter_obj.save()
            for block_data in rule_data.get("individuals_filters_blocks", []):
                block_obj = TargetingIndividualRuleFilterBlock(
                    targeting_criteria_rule=rule_obj, target_only_hoh=target_only_hoh
                )
                block_obj.save()
                for individual_block_filters_data in block_data.get("individual_block_filters"):
                    individual_block_filters_obj = TargetingIndividualBlockRuleFilter(
                        individuals_filters_block=block_obj, **individual_block_filters_data
                    )
                    individual_block_filters_obj.save()
        return criteria_obj
