import logging

from models.household import Household, Individual
from hope.apps.payment.models import PaymentPlan
from models.program import Program
from models.targeting import (
    TargetingCollectorBlockRuleFilter,
    TargetingCollectorRuleFilterBlock,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)

logger = logging.getLogger(__name__)


def get_existing_unicef_ids(ids_string: str, model: type[Household] | type[Individual], program: Program) -> str:
    ids_list = [i.strip() for i in ids_string.split(",")]
    return ", ".join(
        model.objects.filter(unicef_id__in=ids_list, program=program)
        .order_by("unicef_id")
        .values_list("unicef_id", flat=True)
    )


def from_input_to_targeting_criteria(
    targeting_criteria_input: dict, program: "Program", payment_plan: PaymentPlan
) -> None:
    # TODO: FIX ME PLEASE ["rules"] ????
    for rule in targeting_criteria_input.pop("rules", []):
        household_ids = rule.get("household_ids", "")
        individual_ids = rule.get("individual_ids", "")
        households_filters_blocks = rule.get("households_filters_blocks", [])
        individuals_filters_blocks = rule.get("individuals_filters_blocks", [])
        collectors_filters_blocks = rule.get("collectors_filters_blocks", [])
        if household_ids:
            household_ids = get_existing_unicef_ids(household_ids, Household, program)
        if individual_ids:
            individual_ids = get_existing_unicef_ids(individual_ids, Individual, program)

        tc_rule = TargetingCriteriaRule(
            payment_plan=payment_plan,
            household_ids=household_ids,
            individual_ids=individual_ids,
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
