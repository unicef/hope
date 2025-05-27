import logging
from typing import TYPE_CHECKING, Dict

from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.targeting.models import (
    TargetingCollectorBlockRuleFilter,
    TargetingCollectorRuleFilterBlock,
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)

if TYPE_CHECKING:  # pragma: no cover
    from hct_mis_api.apps.program.models import Program


logger = logging.getLogger(__name__)


def get_unicef_ids(ids_string: str, type_id: str, program: "Program") -> str:
    list_ids = []
    ids_list = ids_string.split(",")
    ids_list = [i.strip() for i in ids_list]
    if type_id == "household":
        hh_ids = [hh_id for hh_id in ids_list if hh_id.startswith("HH")]
        list_ids = list(
            Household.objects.filter(unicef_id__in=hh_ids, program=program)
            .order_by("unicef_id")
            .values_list("unicef_id", flat=True)
        )
    if type_id == "individual":
        ind_ids = [ind_id for ind_id in ids_list if ind_id.startswith("IND")]
        list_ids = list(
            Individual.objects.filter(unicef_id__in=ind_ids, program=program)
            .order_by("unicef_id")
            .values_list("unicef_id", flat=True)
        )

    return ", ".join(list_ids)


def from_input_to_targeting_criteria(targeting_criteria_input: Dict, program: "Program") -> TargetingCriteria:
    rules = targeting_criteria_input.pop("rules", [])

    targeting_criteria = TargetingCriteria(**targeting_criteria_input)
    targeting_criteria.save()

    for rule in rules:
        household_ids = rule.get("household_ids", "")
        individual_ids = rule.get("individual_ids", "")
        households_filters_blocks = rule.get("households_filters_blocks", [])
        individuals_filters_blocks = rule.get("individuals_filters_blocks", [])
        collectors_filters_blocks = rule.get("collectors_filters_blocks", [])
        if household_ids:
            household_ids = get_unicef_ids(household_ids, "household", program)
        if individual_ids:
            individual_ids = get_unicef_ids(individual_ids, "individual", program)

        tc_rule = TargetingCriteriaRule(
            targeting_criteria=targeting_criteria, household_ids=household_ids, individual_ids=individual_ids
        )
        tc_rule.save()
        for hh_filter in households_filters_blocks:
            tc_rule_filter = TargetingCriteriaRuleFilter(targeting_criteria_rule=tc_rule, **hh_filter)
            tc_rule_filter.save()

        for ind_filter_block in individuals_filters_blocks:
            ind_block = TargetingIndividualRuleFilterBlock(targeting_criteria_rule=tc_rule)
            ind_block.save()
            for ind_filter in ind_filter_block.get("individual_block_filters", []):
                individual_filter = TargetingIndividualBlockRuleFilter(
                    individuals_filters_block=ind_block, **ind_filter
                )
                individual_filter.save()

        for collector_filter_block in collectors_filters_blocks:
            collector_block = TargetingCollectorRuleFilterBlock(targeting_criteria_rule=tc_rule)
            collector_block.save()
            for collectors_filter in collector_filter_block.get("collector_block_filters", []):
                collector_block_filters = TargetingCollectorBlockRuleFilter(
                    collector_block_filters=collector_block, **collectors_filter
                )
                collector_block_filters.save()

    return targeting_criteria
