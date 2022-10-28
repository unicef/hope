import logging

from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.field_attributes.core_fields_attributes import FieldFactory, Scope
from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.core.utils import get_attr_value
from hct_mis_api.apps.core.validators import BaseValidator
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import (
    TargetingCriteriaRuleFilter,
    TargetPopulation,
)

logger = logging.getLogger(__name__)


class TargetValidator(BaseValidator):
    """Validator for Target Population."""

    @staticmethod
    def validate_is_finalized(target_status):
        if target_status == "FINALIZED":
            logger.error("Target Population has been finalized. Cannot change.")
            raise ValidationError("Target Population has been finalized. Cannot change.")


class RebuildTargetPopulationValidator:
    @staticmethod
    def validate(target_population: TargetPopulation):
        if target_population.status != TargetPopulation.STATUS_OPEN:
            message = f"Only Target Population with status {TargetPopulation.STATUS_OPEN} can be rebuild"
            logger.error(message)
            raise ValidationError(message)


class LockTargetPopulationValidator:
    @staticmethod
    def validate(target_population: TargetPopulation):
        if target_population.status != TargetPopulation.STATUS_OPEN:
            message = f"Only Target Population with status {TargetPopulation.STATUS_OPEN} can be approved"
            logger.error(message)
            raise ValidationError(message)


class UnlockTargetPopulationValidator:
    @staticmethod
    def validate(target_population: TargetPopulation):
        if not target_population.is_locked():
            message = "Only locked Target Population with status can be unlocked"
            logger.error(message)
            raise ValidationError(message)


class FinalizeTargetPopulationValidator:
    @staticmethod
    def validate(target_population: TargetPopulation):
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
    def validate(rule_filter):
        is_flex_field = rule_filter.is_flex_field
        if not is_flex_field:
            attributes = FieldFactory.from_scope(Scope.TARGETING).to_dict_by("name")
            attribute = attributes.get(rule_filter.field_name)
            if attribute is None:
                logger.error(f"Can't find any core field attribute associated with {rule_filter.field_name} field name")
                raise ValidationError(
                    f"Can't find any core field attribute associated with {rule_filter.field_name} field name"
                )
        else:
            try:
                attribute = FlexibleAttribute.objects.get(name=rule_filter.field_name)
            except FlexibleAttribute.DoesNotExist:
                logger.exception(
                    f"Can't find any flex field attribute associated with {rule_filter.field_name} field name",
                )
                raise ValidationError(
                    f"Can't find any flex field attribute associated with {rule_filter.field_name} field name"
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
                logger.error(
                    f"SELECT_MANY expect at least 1 argument" f"expect {args_count} arguments, {given_args_count} given"
                )
                raise ValidationError(
                    f"SELECT_MANY expect at least 1 argument" f"expect {args_count} arguments, {given_args_count} given"
                )
        elif given_args_count != args_count:
            logger.error(
                f"Comparison method - {rule_filter.comparison_method} "
                f"expect {args_count} arguments, {given_args_count} given"
            )
            raise ValidationError(
                f"Comparison method - {rule_filter.comparison_method} "
                f"expect {args_count} arguments, {given_args_count} given"
            )
        if get_attr_value("type", attribute) not in comparison_attribute.get("supported_types"):
            logger.error(
                f"{rule_filter.field_name} is {get_attr_value('type', attribute)} type filter "
                f"and does not accept - {rule_filter.comparison_method} comparison method"
            )
            raise ValidationError(
                f"{rule_filter.field_name} is {get_attr_value( 'type', attribute)} type filter "
                f"and does not accept - {rule_filter.comparison_method} comparison method"
            )


class TargetingCriteriaRuleInputValidator:
    @staticmethod
    def validate(rule):
        total_len = 0
        filters = rule.get("filters")
        individuals_filters_blocks = rule.get("individuals_filters_blocks")
        if filters is not None:
            total_len += len(filters)
        if individuals_filters_blocks is not None:
            total_len += len(individuals_filters_blocks)

        if total_len < 1:
            logger.error("There should be at least 1 filter or block in rules")
            raise ValidationError("There should be at least 1 filter or block in rules")
        for rule_filter in filters:
            TargetingCriteriaRuleFilterInputValidator.validate(rule_filter)


class TargetingCriteriaInputValidator:
    @staticmethod
    def validate(targeting_criteria):
        rules = targeting_criteria.get("rules")
        if len(rules) < 1:
            logger.error("There should be at least 1 rule in target criteria")
            raise ValidationError("There should be at least 1 rule in target criteria")
        for rule in rules:
            TargetingCriteriaRuleInputValidator.validate(rule)
