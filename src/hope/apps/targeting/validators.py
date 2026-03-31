import logging
from typing import Any

from rest_framework.exceptions import ValidationError

from hope.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hope.apps.core.field_attributes.fields_types import Scope
from hope.apps.core.utils import get_attr_value
from hope.apps.household.const import ROLE_ALTERNATE
from hope.apps.targeting.choices import FlexFieldClassification
from hope.models import (
    DataCollectingType,
    FlexibleAttribute,
    Household,
    Individual,
    IndividualRoleInHousehold,
    Program,
    TargetingCriteriaRuleFilter,
)

logger = logging.getLogger(__name__)


class TargetingCriteriaRuleFilterInputValidator:
    @staticmethod
    def _resolve_attribute(rule_filter: dict, program: Program) -> Any:
        flex_field_classification = rule_filter["flex_field_classification"]
        if flex_field_classification == FlexFieldClassification.NOT_FLEX_FIELD:
            attributes = FieldFactory.from_scope(Scope.TARGETING).to_dict_by("name")
            attribute = attributes.get(rule_filter["field_name"])
            if attribute is None:
                logger.warning(
                    f"Can't find any core field attribute associated with {rule_filter['field_name']} field name"
                )
                raise ValidationError(
                    f"Can't find any core field attribute associated with {rule_filter['field_name']} field name"
                )
            return attribute
        if flex_field_classification == FlexFieldClassification.FLEX_FIELD_BASIC:
            try:
                return FlexibleAttribute.objects.get(name=rule_filter["field_name"], program=None)
            except FlexibleAttribute.DoesNotExist:
                logger.warning(
                    f"Can't find any flex field attribute associated with {rule_filter['field_name']} field name",
                )
                raise ValidationError(
                    f"Can't find any flex field attribute associated with {rule_filter['field_name']} field name"
                )
        else:
            try:
                return FlexibleAttribute.objects.get(name=rule_filter["field_name"], program=program)
            except FlexibleAttribute.DoesNotExist:  # pragma: no cover
                logger.warning(
                    f"Can't find PDU flex field attribute associated with {rule_filter['field_name']}"
                    f" field name in program {program.name}",
                )
                raise ValidationError(
                    f"Can't find PDU flex field attribute associated with {rule_filter['field_name']}"
                    f" field name in program {program.name}",
                )

    @staticmethod
    def validate(rule_filter: dict, program: Program) -> None:
        attribute = TargetingCriteriaRuleFilterInputValidator._resolve_attribute(rule_filter, program)
        comparison_attribute = TargetingCriteriaRuleFilter.COMPARISON_ATTRIBUTES.get(rule_filter["comparison_method"])
        if comparison_attribute is None:
            logger.warning(f"Unknown comparison method - {rule_filter['comparison_method']}")
            raise ValidationError(f"Unknown comparison method - {rule_filter['comparison_method']}")
        args_count = comparison_attribute.get("arguments")
        given_args_count = len(rule_filter.get("arguments", []))
        select_many = get_attr_value("type", attribute) == "SELECT_MANY"
        if select_many:
            if given_args_count < 1:
                raise ValidationError("SELECT_MANY expects at least 1 argument")
        elif given_args_count != args_count:
            raise ValidationError(
                f"Comparison method '{rule_filter['comparison_method']}' "
                f"expected {args_count} arguments, {given_args_count} given"
            )
        field_type = get_attr_value("type", attribute, None)
        if field_type == FlexibleAttribute.PDU:
            field_type = attribute.pdu_data.subtype
        supported_types = comparison_attribute.get("supported_types")
        if not isinstance(supported_types, list):
            raise TypeError(f"Expected list for supported_types, got {type(supported_types).__name__}")
        if field_type not in supported_types:
            raise ValidationError(
                f"{rule_filter['field_name']} is '{get_attr_value('type', attribute)}' type filter "
                f"and does not accept '{rule_filter['comparison_method']}' comparison method"
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
            alternative_collectors_ids = rule.get("alternative_collectors_ids")

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

            # validate alternate collectors
            if alternative_collectors_ids:
                alt_col_ids_list = [i.strip() for i in alternative_collectors_ids.split(",")]

                invalid_ids = [i for i in alt_col_ids_list if not i.startswith(("HH", "IND"))]
                if invalid_ids:
                    raise ValidationError(f"Invalid collector ID(s): {invalid_ids}")

                hh_ids = [i for i in alt_col_ids_list if i.startswith("HH")]
                ind_ids = [i for i in alt_col_ids_list if i.startswith("IND")]
                existing_hh_roles = set(
                    IndividualRoleInHousehold.objects.filter(
                        household__unicef_id__in=hh_ids,
                        role=ROLE_ALTERNATE,
                    ).values_list("household__unicef_id", flat=True)
                )
                existing_ind_roles = set(
                    IndividualRoleInHousehold.objects.filter(
                        household__individuals__unicef_id__in=ind_ids,
                        role=ROLE_ALTERNATE,
                    ).values_list("household__individuals__unicef_id", flat=True)
                )
                missing_alt_roles = [unicef_id for unicef_id in hh_ids if unicef_id not in existing_hh_roles] + [
                    unicef_id for unicef_id in ind_ids if unicef_id not in existing_ind_roles
                ]
                if missing_alt_roles:
                    raise ValidationError(f"Can't find Alternate collector role for ID(s): {missing_alt_roles}")

            is_empty_rules = all(
                len(rule.get(key, [])) == 0
                for key in [
                    "households_filters_blocks",
                    "individuals_filters_blocks",
                ]
            )

            if is_empty_rules and not household_ids and not individual_ids:
                raise ValidationError("There should be at least 1 rule in target criteria")

            TargetingCriteriaRuleInputValidator.validate(rule=rule, program=program)
