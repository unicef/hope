import logging
from typing import TYPE_CHECKING, Any, Dict

from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hct_mis_api.apps.core.field_attributes.fields_types import Scope
from hct_mis_api.apps.core.models import DataCollectingType, FlexibleAttribute
from hct_mis_api.apps.core.utils import get_attr_value
from hct_mis_api.apps.core.validators import BaseValidator
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.choices import FlexFieldClassification
from hct_mis_api.apps.targeting.models import (
    TargetingCriteriaRuleFilter,
    TargetPopulation,
)

if TYPE_CHECKING:
    from hct_mis_api.apps.steficon.models import Rule


logger = logging.getLogger(__name__)


class TargetValidator(BaseValidator):
    """Validator for Target Population."""

    @staticmethod
    def validate_is_finalized(target_status: str) -> None:
        if target_status == "FINALIZED":
            logger.error("Target Population has been finalized. Cannot change.")
            raise ValidationError("Target Population has been finalized. Cannot change.")


class RebuildTargetPopulationValidator:
    @staticmethod
    def validate(target_population: TargetPopulation) -> None:
        if target_population.status != TargetPopulation.STATUS_OPEN:
            message = f"Only Target Population with status {TargetPopulation.STATUS_OPEN} can be rebuild"
            logger.error(message)
            raise ValidationError(message)


class LockTargetPopulationValidator:
    @staticmethod
    def validate(target_population: TargetPopulation) -> None:
        if target_population.status != TargetPopulation.STATUS_OPEN:
            message = f"Only Target Population with status {TargetPopulation.STATUS_OPEN} can be approved"
            logger.error(message)
            raise ValidationError(message)


class UnlockTargetPopulationValidator:
    @staticmethod
    def validate(target_population: TargetPopulation) -> None:
        if not target_population.is_locked():
            message = "Only locked Target Population with status can be unlocked"
            logger.error(message)
            raise ValidationError(message)


class FinalizeTargetPopulationValidator:
    @staticmethod
    def validate(target_population: TargetPopulation) -> None:
        if not target_population.is_locked():
            message = "Only locked Target Population with status can be finalized"
            logger.error(message)
            raise ValidationError(message)
        if target_population.program.status != Program.ACTIVE:
            message = f"Only Target Population assigned to program with status {Program.ACTIVE} can be send"
            logger.error(message)
            raise ValidationError(message)


class TargetingCriteriaRuleFilterInputValidator:
    @staticmethod
    def validate(rule_filter: Any, program: Program) -> None:
        flex_field_classification = rule_filter.flex_field_classification
        if flex_field_classification == FlexFieldClassification.NOT_FLEX_FIELD:
            attributes = FieldFactory.from_scope(Scope.TARGETING).to_dict_by("name")
            attribute = attributes.get(rule_filter.field_name)
            if attribute is None:
                logger.error(f"Can't find any core field attribute associated with {rule_filter.field_name} field name")
                raise ValidationError(
                    f"Can't find any core field attribute associated with {rule_filter.field_name} field name"
                )
        elif flex_field_classification == FlexFieldClassification.FLEX_FIELD_NOT_PDU:
            try:
                attribute = FlexibleAttribute.objects.get(name=rule_filter.field_name, program=None)
            except FlexibleAttribute.DoesNotExist:
                logger.exception(
                    f"Can't find any flex field attribute associated with {rule_filter.field_name} field name",
                )
                raise ValidationError(
                    f"Can't find any flex field attribute associated with {rule_filter.field_name} field name"
                )
        else:
            try:
                attribute = FlexibleAttribute.objects.get(name=rule_filter.field_name, program=program)
            except FlexibleAttribute.DoesNotExist:
                logger.exception(
                    f"Can't find PDU flex field attribute associated with {rule_filter.field_name} field name in program {program.name}",
                )
                raise ValidationError(
                    f"Can't find PDU flex field attribute associated with {rule_filter.field_name} field name in program {program.name}",
                )
        comparison_attribute = TargetingCriteriaRuleFilter.COMPARISON_ATTRIBUTES.get(rule_filter.comparison_method)
        if comparison_attribute is None:
            logger.error(f"Unknown comparison method - {rule_filter.comparison_method}")
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
    def validate(rule: "Rule", program: "Program") -> None:
        total_len = 0
        filters = rule.get("filters")
        individuals_filters_blocks = rule.get("individuals_filters_blocks", [])
        if filters is not None:
            total_len += len(filters)
        if individuals_filters_blocks is not None:
            total_len += len(individuals_filters_blocks)

        if total_len < 1:
            logger.error("There should be at least 1 filter or block in rules")
            raise ValidationError("There should be at least 1 filter or block in rules")
        for rule_filter in filters:
            TargetingCriteriaRuleFilterInputValidator.validate(rule_filter=rule_filter, program=program)
        for individuals_filters_block in individuals_filters_blocks:
            individual_block_filters = individuals_filters_block.get("individual_block_filters", [])
            for individual_block_filter in individual_block_filters:
                TargetingCriteriaRuleFilterInputValidator.validate(rule_filter=individual_block_filter, program=program)


class TargetingCriteriaInputValidator:
    @staticmethod
    def validate(targeting_criteria: Dict, program: Program) -> None:
        program_dct = program.data_collecting_type
        rules = targeting_criteria.get("rules", [])
        household_ids = targeting_criteria.get("household_ids")
        individual_ids = targeting_criteria.get("individual_ids")
        if rules and (household_ids or individual_ids):
            logger.error("Target criteria can only have filters or ids, not possible to have both")
            raise ValidationError("Target criteria can only have filters or ids, not possible to have both")

        if household_ids and not (
            program_dct.household_filters_available or program_dct.type == DataCollectingType.Type.SOCIAL
        ):
            logger.error("Target criteria can only have individual ids")
            raise ValidationError("Target criteria can only have individual ids")
        if individual_ids and not program_dct.individual_filters_available:
            logger.error("Target criteria can only have household ids")
            raise ValidationError("Target criteria can only have household ids")

        if household_ids:
            ids_list = household_ids.split(",")
            ids_list = [i.strip() for i in ids_list]
            ids_list = [i for i in ids_list if i.startswith("HH")]
            if not Household.objects.filter(unicef_id__in=ids_list, program=program).exists():
                logger.error("The given households do not exist in the current program")
                raise ValidationError("The given households do not exist in the current program")

        if individual_ids:
            ids_list = individual_ids.split(",")
            ids_list = [i.strip() for i in ids_list]
            ids_list = [i for i in ids_list if i.startswith("IND")]
            if not Individual.objects.filter(unicef_id__in=ids_list, program=program).exists():
                logger.error("The given individuals do not exist in the current program")
                raise ValidationError("The given individuals do not exist in the current program")

        if len(rules) < 1 and not household_ids and not individual_ids:
            logger.error("There should be at least 1 rule in target criteria")
            raise ValidationError("There should be at least 1 rule in target criteria")

        if not household_ids and not individual_ids:
            for rule in rules:
                TargetingCriteriaRuleInputValidator.validate(rule=rule, program=program)
