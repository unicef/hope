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
    def from_dict(data: dict, criteria_type: Type[T], target_only_hoh: bool) -> T:
        criteria_obj = criteria_type()
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

    @staticmethod
    def copy(criteria: T) -> T:
        copied = type(criteria)()
        copied.save()
        for rule in criteria.rules.all():
            rule_copy = TargetingCriteriaRule(targeting_criteria=copied)
            rule_copy.save()
            for hh_filter in rule.filters.all():
                hh_filter.pk = None
                hh_filter.targeting_criteria_rule = rule_copy
                hh_filter.save()
            for ind_filter_block in rule.individuals_filters_blocks.all():
                ind_filter_block_copy = TargetingIndividualRuleFilterBlock(
                    targeting_criteria_rule=rule_copy, target_only_hoh=ind_filter_block.target_only_hoh
                )
                ind_filter_block_copy.save()
                for ind_filter in ind_filter_block.individual_block_filters.all():
                    ind_filter.pk = None
                    ind_filter.individuals_filters_block = ind_filter_block_copy
                    ind_filter.save()
        return copied
