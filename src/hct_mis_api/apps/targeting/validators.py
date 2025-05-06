import logging
from typing import Any

from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hct_mis_api.apps.core.field_attributes.fields_types import Scope
from hct_mis_api.apps.core.models import DataCollectingType, FlexibleAttribute
from hct_mis_api.apps.core.utils import get_attr_value
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.choices import FlexFieldClassification
from hct_mis_api.apps.targeting.models import TargetingCriteriaRuleFilter

logger = logging.getLogger(__name__)


class TargetingCriteriaRuleFilterInputValidator:
    @staticmethod
    def validate(rule_filter: Any, program: Program) -> None:
        flex_field_classification = rule_filter.flex_field_classification
        if flex_field_classification == FlexFieldClassification.NOT_FLEX_FIELD:
            attributes = FieldFactory.from_scope(Scope.TARGETING).to_dict_by("name")
            attribute = attributes.get(rule_filter.field_name)
            if attribute is None:
                logger.warning(
                    f"Can't find any core field attribute associated with {rule_filter.field_name} field name"
                )
                raise ValidationError(
                    f"Can't find any core field attribute associated with {rule_filter.field_name} field name"
                )
        elif flex_field_classification == FlexFieldClassification.FLEX_FIELD_BASIC:
            try:
                attribute = FlexibleAttribute.objects.get(name=rule_filter.field_name, program=None)
            except FlexibleAttribute.DoesNotExist:
                logger.warning(
                    f"Can't find any flex field attribute associated with {rule_filter.field_name} field name",
                )
                raise ValidationError(
                    f"Can't find any flex field attribute associated with {rule_filter.field_name} field name"
                )
        else:
            try:
                attribute = FlexibleAttribute.objects.get(name=rule_filter.field_name, program=program)
            except FlexibleAttribute.DoesNotExist:  # pragma: no cover
                logger.warning(
                    f"Can't find PDU flex field attribute associated with {rule_filter.field_name} field name in program {program.name}",
                )
                raise ValidationError(
                    f"Can't find PDU flex field attribute associated with {rule_filter.field_name} field name in program {program.name}",
                )
        comparison_attribute = TargetingCriteriaRuleFilter.COMPARISON_ATTRIBUTES.get(rule_filter.comparison_method)
        if comparison_attribute is None:
            logger.warning(f"Unknown comparison method - {rule_filter.comparison_method}")
            raise ValidationError(f"Unknown comparison method - {rule_filter.comparison_method}")
        args_count = comparison_attribute.get("arguments")
        given_args_count = len(rule_filter.arguments)
        select_many = get_attr_value("type", attribute) == "SELECT_MANY"
        if select_many:
            if given_args_count < 1:
                raise ValidationError("SELECT_MANY expects at least 1 argument")
        elif given_args_count != args_count:
            raise ValidationError(
                f"Comparison method '{rule_filter.comparison_method}' "
                f"expected {args_count} arguments, {given_args_count} given"
            )
        type = get_attr_value("type", attribute, None)
        if type == FlexibleAttribute.PDU:
            type = attribute.pdu_data.subtype
        if type not in comparison_attribute.get("supported_types"):
            raise ValidationError(
                f"{rule_filter.field_name} is '{get_attr_value('type', attribute)}' type filter "
                f"and does not accept '{rule_filter.comparison_method}' comparison method"
            )


class TargetingCriteriaRuleInputValidator:
    @staticmethod
    def validate(rule: "dict", program: "Program") -> None:
        households_filters_blocks = rule.get("households_filters_blocks", [])
        individuals_filters_blocks = rule.get("individuals_filters_blocks", [])

        for households_block_filter in households_filters_blocks:
            TargetingCriteriaRuleFilterInputValidator.validate(rule_filter=households_block_filter, program=program)

        for individuals_filters_block in individuals_filters_blocks:
            for individuals_filter in individuals_filters_block.get("individual_block_filters", []):
                TargetingCriteriaRuleFilterInputValidator.validate(rule_filter=individuals_filter, program=program)


class TargetingCriteriaInputValidator:
    @staticmethod
    def validate(targeting_criteria: dict, program: Program) -> None:
        program_dct = program.data_collecting_type
        rules: list = targeting_criteria.get("rules", [])

        if len(rules) < 1:
            raise ValidationError("There should be at least 1 rule in target criteria")

        for rule in rules:
            household_ids = rule.get("household_ids")
            individual_ids = rule.get("individual_ids")

            if household_ids and not (
                program_dct.household_filters_available or program_dct.type == DataCollectingType.Type.SOCIAL
            ):
                logger.warning("Target criteria can only have individual ids")
                raise ValidationError("Target criteria can only have individual ids")
            if individual_ids and not program_dct.individual_filters_available:
                raise ValidationError("Target criteria can only have household ids")

            if household_ids:
                ids_list = household_ids.split(",")
                ids_list = [i.strip() for i in ids_list]
                ids_list = [i for i in ids_list if i.startswith("HH")]
                if not Household.objects.filter(unicef_id__in=ids_list, program=program).exists():
                    raise ValidationError("The given households do not exist in the current program")

            if individual_ids:
                ids_list = individual_ids.split(",")
                ids_list = [i.strip() for i in ids_list]
                ids_list = [i for i in ids_list if i.startswith("IND")]
                if not Individual.objects.filter(unicef_id__in=ids_list, program=program).exists():
                    raise ValidationError("The given individuals do not exist in the current program")

            is_empty_rules = all(
                len(rule.get(key, [])) == 0
                for key in ["households_filters_blocks", "individuals_filters_blocks", "collectors_filters_blocks"]
            )

            if is_empty_rules and not household_ids and not individual_ids:
                raise ValidationError("There should be at least 1 rule in target criteria")

            TargetingCriteriaRuleInputValidator.validate(rule=rule, program=program)
