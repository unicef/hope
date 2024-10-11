import logging
from typing import Any, List, Optional

from django.contrib.postgres.search import CombinedSearchQuery, SearchQuery
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet
from django.utils.translation import gettext_lazy as _

from model_utils import Choices

from hct_mis_api.apps.core.field_attributes.fields_types import (
    _HOUSEHOLD,
    _INDIVIDUAL,
    TYPE_DECIMAL,
    TYPE_INTEGER,
    TYPE_SELECT_MANY,
)
from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.core.utils import get_attr_value
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.targeting.choices import FlexFieldClassification

logger = logging.getLogger(__name__)


class TargetingCriteriaQueryingBase:
    """
    Whole query is built here
    this mixin connects OR blocks
    """

    def __init__(self, rules: Optional[List] = None, excluded_household_ids: Optional[List] = None) -> None:
        if rules is None:
            return
        self.rules = rules
        self.flag_exclude_if_active_adjudication_ticket = False
        self.flag_exclude_if_on_sanction_list = False
        if excluded_household_ids is None:
            self._excluded_household_ids = []
        else:
            self._excluded_household_ids = excluded_household_ids

    def get_household_queryset(self) -> QuerySet:
        return Household.objects

    def get_individual_queryset(self) -> QuerySet:
        return Individual.objects

    def get_rules(self) -> Any:
        return self.rules

    def get_excluded_household_ids(self) -> Any:
        return self._excluded_household_ids

    def get_criteria_string(self) -> str:
        rules = self.get_rules()
        rules_string = [x.get_criteria_string() for x in rules]
        return " OR ".join(rules_string).strip()

    def get_basic_query(self) -> Q:
        return Q(withdrawn=False) & ~Q(unicef_id__in=self.get_excluded_household_ids())

    def apply_targeting_criteria_exclusion_flags(self) -> Q:
        return self.apply_flag_exclude_if_active_adjudication_ticket() & self.apply_flag_exclude_if_on_sanction_list()

    def apply_flag_exclude_if_active_adjudication_ticket(self) -> Q:
        if not self.flag_exclude_if_active_adjudication_ticket:
            return Q()
        return ~Q(
            (
                Q(individuals__ticket_duplicates__isnull=False)
                & ~Q(individuals__ticket_duplicates__ticket__status=GrievanceTicket.STATUS_CLOSED)
            )
            | (
                Q(individuals__ticket_golden_records__isnull=False)
                & ~Q(individuals__ticket_golden_records__ticket__status=GrievanceTicket.STATUS_CLOSED)
            )
            | (
                Q(representatives__ticket_duplicates__isnull=False)
                & ~Q(representatives__ticket_duplicates__ticket__status=GrievanceTicket.STATUS_CLOSED)
            )
            | (
                Q(representatives__ticket_golden_records__isnull=False)
                & ~Q(representatives__ticket_golden_records__ticket__status=GrievanceTicket.STATUS_CLOSED)
            )
        )

    def apply_flag_exclude_if_on_sanction_list(self) -> Q:
        if not self.flag_exclude_if_on_sanction_list:
            return Q()
        return ~Q(
            Q(individuals__sanction_list_confirmed_match=True) | Q(representatives__sanction_list_confirmed_match=True)
        )

    def get_query(self) -> Q:
        rules = self.get_rules()
        query = Q()
        for rule in rules:
            query |= rule.get_query()
        return self.get_basic_query() & Q(query) & self.apply_targeting_criteria_exclusion_flags()


class TargetingCriteriaRuleQueryingBase:
    """
    Gets query for single block
    combines individual filters block with household filters
    """

    def __init__(self, filters: Optional[Any] = None, individuals_filters_blocks: Optional[Any] = None) -> None:
        if filters is not None:
            self.filters = filters
        if individuals_filters_blocks is not None:
            self.individuals_filters_blocks = individuals_filters_blocks

    def get_filters(self) -> Any:
        return self.filters

    def get_individuals_filters_blocks(self) -> Any:
        return self.individuals_filters_blocks

    def get_criteria_string(self) -> str:
        filters = self.get_filters()
        filters_strings = [x.get_criteria_string() for x in filters]
        individuals_filters_blocks = self.get_individuals_filters_blocks()
        individuals_filters_blocks_strings = [x.get_criteria_string() for x in individuals_filters_blocks]
        all_strings = []
        if len(filters_strings):
            all_strings.append(f"H({' AND '.join(filters_strings).strip()})")
        if len(individuals_filters_blocks_strings):
            all_strings.append(f"I({' AND '.join(individuals_filters_blocks_strings).strip()})")
        return " AND ".join(all_strings).strip()

    def get_query(self) -> Q:
        query = Q()
        filters = self.get_filters()
        individuals_filters_blocks = self.get_individuals_filters_blocks()
        # Thats household filters
        for ruleFilter in filters:
            query &= ruleFilter.get_query()
        # filter individual block
        for individuals_filters_block in individuals_filters_blocks:
            query &= individuals_filters_block.get_query()
        return query


class TargetingIndividualRuleFilterBlockBase:
    def __init__(
        self, individual_block_filters: Optional[Any] = None, target_only_hoh: Optional[List[Household]] = None
    ) -> None:
        if individual_block_filters is not None:
            self.individual_block_filters = individual_block_filters
        if target_only_hoh is not None:
            self.target_only_hoh = target_only_hoh

    def get_individual_block_filters(self) -> Any:
        return self.individual_block_filters

    def get_criteria_string(self) -> str:
        filters = self.get_individual_block_filters()
        filters_string = [x.get_criteria_string() for x in filters]
        return f"({' AND '.join(filters_string).strip()})"

    def get_basic_individual_query(self) -> Q:
        return Q(duplicate=False) & Q(withdrawn=False)

    def get_query(self) -> Q:
        individuals_query = self.get_basic_individual_query()
        filters = self.get_individual_block_filters()
        filtered = False
        search_query = SearchQuery("")

        for ruleFilter in filters:
            filtered = True
            if ruleFilter.field_name in ("observed_disability", "full_name"):
                for arg in getattr(ruleFilter, "parametrizer", []):
                    search_query &= SearchQuery(arg)
            else:
                individuals_query &= ruleFilter.get_query()
        if not filtered:
            return Q()
        if self.target_only_hoh:
            # only filtering against heads of household
            individuals_query &= Q(heading_household__isnull=False)

        individual_query = Individual.objects
        if isinstance(search_query, CombinedSearchQuery):
            q = individual_query.filter(vector_column=search_query).filter(individuals_query)
        else:
            q = individual_query.filter(individuals_query)

        households_id = q.values_list("household_id", flat=True)
        return Q(id__in=households_id)


class TargetingCriteriaFilterBase:
    COMPARISON_ATTRIBUTES = {
        "EQUALS": {
            "arguments": 1,
            "lookup": "",
            "negative": False,
            "supported_types": ["INTEGER", "SELECT_ONE", "STRING", "BOOL"],
        },
        "NOT_EQUALS": {
            "arguments": 1,
            "lookup": "",
            "negative": True,
            "supported_types": ["INTEGER", "SELECT_ONE"],
        },
        "CONTAINS": {
            "min_arguments": 1,
            "arguments": 1,
            "lookup": "__icontains",
            "negative": False,
            "supported_types": ["SELECT_MANY", "STRING"],
        },
        "NOT_CONTAINS": {
            "arguments": 1,
            "lookup": "__icontains",
            "negative": True,
            "supported_types": ["STRING"],
        },
        "RANGE": {
            "arguments": 2,
            "lookup": "__range",
            "negative": False,
            "supported_types": ["INTEGER", "DECIMAL", "DATE"],
        },
        "NOT_IN_RANGE": {
            "arguments": 2,
            "lookup": "__range",
            "negative": True,
            "supported_types": ["INTEGER", "DECIMAL"],
        },
        "GREATER_THAN": {
            "arguments": 1,
            "lookup": "__gte",
            "negative": False,
            "supported_types": ["INTEGER", "DECIMAL", "DATE"],
        },
        "LESS_THAN": {
            "arguments": 1,
            "lookup": "__lte",
            "negative": False,
            "supported_types": ["INTEGER", "DECIMAL", "DATE"],
        },
        "IS_NULL": {
            "arguments": 1,
            "lookup": "",
            "negative": False,
            "supported_types": ["DECIMAL", "DATE", "STRING", "BOOL"],
        },
    }

    COMPARISON_CHOICES = Choices(
        ("EQUALS", _("Equals")),
        ("NOT_EQUALS", _("Not Equals")),
        ("CONTAINS", _("Contains")),
        ("NOT_CONTAINS", _("Does not contain")),
        ("RANGE", _("In between <>")),
        ("NOT_IN_RANGE", _("Not in between <>")),
        ("GREATER_THAN", _("Greater than")),
        ("LESS_THAN", _("Less than")),
        ("IS_NULL", _("Is null")),
    )

    @property
    def field_name_combined(self) -> str:
        return f"{self.field_name}__{self.round_number}" if self.round_number else self.field_name

    def get_criteria_string(self) -> str:
        return f"{{{self.field_name_combined} {self.comparison_method} ({','.join([str(x) for x in self.arguments])})}}"

    def get_lookup_prefix(self, associated_with: str) -> str:
        return "individuals__" if associated_with == _INDIVIDUAL else ""

    def prepare_arguments(self, arguments: List, field_attr: str) -> List:
        is_flex_field = get_attr_value("is_flex_field", field_attr, False)
        if not is_flex_field:
            return arguments
        type = get_attr_value("type", field_attr, None)
        if type == FlexibleAttribute.PDU:
            if arguments == [None]:
                return arguments
            type = field_attr.pdu_data.subtype
        if type == TYPE_DECIMAL:
            return [float(arg) for arg in arguments]
        if type == TYPE_INTEGER:
            return [int(arg) for arg in arguments]
        return arguments

    def get_query_for_lookup(
        self,
        lookup: str,
        field_attr: str,
    ) -> Q:
        select_many = get_attr_value("type", field_attr, None) == TYPE_SELECT_MANY
        comparison_attribute = TargetingCriteriaFilterBase.COMPARISON_ATTRIBUTES.get(self.comparison_method)
        args_count = comparison_attribute.get("arguments")
        if self.arguments is None:
            logger.error(f"{self.field_name} {self.comparison_method} filter query expect {args_count} " f"arguments")
            raise ValidationError(
                f"{self.field_name} {self.comparison_method} filter query expect {args_count} " f"arguments"
            )
        args_input_count = len(self.arguments)
        if select_many:
            if args_input_count < 1:
                logger.error(f"{self.field_name} SELECT MULTIPLE CONTAINS filter query expect at least 1 argument")
                raise ValidationError(
                    f"{self.field_name} SELECT MULTIPLE CONTAINS filter query expect at least 1 argument"
                )
        elif args_count != args_input_count:
            logger.error(
                f"{self.field_name} {self.comparison_method} filter query expect {args_count} "
                f"arguments gets {args_input_count}"
            )
            raise ValidationError(
                f"{self.field_name} {self.comparison_method} filter query expect {args_count} "
                f"arguments gets {args_input_count}"
            )
        arguments = self.prepare_arguments(self.arguments, field_attr)
        argument = arguments if args_input_count > 1 else arguments[0]
        if select_many:
            if isinstance(argument, list):
                query = Q()
                for arg in argument:
                    # This regular expression can found the only exact word
                    query &= Q(**{f"{lookup}__icontains": arg})
            else:
                query = Q(**{f"{lookup}__contains": argument})
        else:
            query = Q(**{f"{lookup}{comparison_attribute.get('lookup')}": argument})
        if comparison_attribute.get("negative"):
            return ~query
        # ignore null values for PDU flex fields
        if (
            self.comparison_method != "IS_NULL"
            and self.flex_field_classification == FlexFieldClassification.FLEX_FIELD_PDU
        ):
            query &= ~Q(**{f"{lookup}": None})

        return query

    def get_query_for_core_field(self) -> Q:
        core_fields = self.get_core_fields()
        core_field_attrs = [attr for attr in core_fields if attr.get("name") == self.field_name]
        if len(core_field_attrs) != 1:
            logger.error(f"There are no Core Field Attributes associated with this fieldName {self.field_name}")
            raise ValidationError(
                f"There are no Core Field Attributes associated with this fieldName {self.field_name}"
            )
        core_field_attr = core_field_attrs[0]
        get_query = core_field_attr.get("get_query")
        if get_query:
            return get_query(
                self.comparison_method, self.arguments, is_social_worker_query=self.is_social_worker_program
            )
        lookup = core_field_attr.get("lookup")
        if not lookup:
            logger.error(
                f"Core Field Attributes associated with this fieldName {self.field_name}"
                " doesn't have get_query method or lookup field"
            )
            raise ValidationError(
                f"Core Field Attributes associated with this fieldName {self.field_name}"
                " doesn't have get_query method or lookup field"
            )
        lookup_prefix = self.get_lookup_prefix(core_field_attr["associated_with"])
        return self.get_query_for_lookup(f"{lookup_prefix}{lookup}", core_field_attr)

    def get_query_for_flex_field(self) -> Q:
        if self.flex_field_classification == FlexFieldClassification.FLEX_FIELD_PDU:
            targeting_criteria_rule = (
                getattr(self, "targeting_criteria_rule", None) or self.individuals_filters_block.targeting_criteria_rule
            )
            program = targeting_criteria_rule.targeting_criteria.target_population.program
            flex_field_attr = FlexibleAttribute.objects.filter(name=self.field_name, program=program).first()
            if not flex_field_attr:
                logger.error(
                    f"There is no PDU Flex Field Attribute associated with this fieldName {self.field_name} in program {program.name}"
                )
                raise ValidationError(
                    f"There is no PDU Flex Field Attribute associated with this fieldName {self.field_name} in program {program.name}"
                )
            if not self.round_number:
                logger.error(f"Round number is missing for PDU Flex Field Attribute {self.field_name}")
                raise ValidationError(f"Round number is missing for PDU Flex Field Attribute {self.field_name}")
            flex_field_attr_rounds_number = flex_field_attr.pdu_data.number_of_rounds
            if self.round_number > flex_field_attr_rounds_number:
                logger.error(
                    f"Round number {self.round_number} is greater than the number of rounds for PDU Flex Field Attribute {self.field_name}"
                )
                raise ValidationError(
                    f"Round number {self.round_number} is greater than the number of rounds for PDU Flex Field Attribute {self.field_name}"
                )
            field_name_combined = f"{flex_field_attr.name}__{self.round_number}__value"
        else:
            flex_field_attr = FlexibleAttribute.objects.filter(name=self.field_name, program=None).first()
            if not flex_field_attr:
                logger.error(f"There is no Flex Field Attributes associated with this fieldName {self.field_name}")
                raise ValidationError(
                    f"There is no Flex Field Attributes associated with this fieldName {self.field_name}"
                )
            field_name_combined = flex_field_attr.name
        lookup_prefix = self.get_lookup_prefix(_INDIVIDUAL if flex_field_attr.associated_with == 1 else _HOUSEHOLD)
        lookup = f"{lookup_prefix}flex_fields__{field_name_combined}"
        return self.get_query_for_lookup(lookup, flex_field_attr)

    def get_query(self) -> Q:
        if self.flex_field_classification == FlexFieldClassification.NOT_FLEX_FIELD:
            return self.get_query_for_core_field()
        return self.get_query_for_flex_field()

    def __str__(self) -> str:
        return f"{self.field_name} {self.comparison_method} {self.arguments}"
