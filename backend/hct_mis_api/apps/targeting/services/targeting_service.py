import logging

from django.contrib.postgres.search import CombinedSearchQuery, SearchQuery
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from model_utils import Choices

from hct_mis_api.apps.core.core_fields_attributes import (
    _HOUSEHOLD,
    _INDIVIDUAL,
    TYPE_DECIMAL,
    TYPE_INTEGER,
    TYPE_SELECT_MANY,
)
from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.core.utils import (
    get_attr_value,
)
from hct_mis_api.apps.household.models import (
    Individual,
    Household,
)

logger = logging.getLogger(__name__)


class TargetingCriteriaQueryingMixin:
    """
    Whole query is built here
    this mixin connects OR blocks
    """

    def __init__(self, rules=None, excluded_household_ids=None):
        if rules is None:
            return
        self.rules = rules
        if excluded_household_ids is None:
            self._excluded_household_ids = []
        else:
            self._excluded_household_ids = excluded_household_ids

    def get_household_queryset(self):
        return Household.objects

    def get_individual_queryset(self):
        return Individual.objects

    def get_rules(self):
        return self.rules

    def get_excluded_household_ids(self):
        return self._excluded_household_ids

    def get_criteria_string(self):
        rules = self.get_rules()
        rules_string = [x.get_criteria_string() for x in rules]
        return " OR ".join(rules_string).strip()

    def get_basic_query(self):
        return Q(size__gt=0) & Q(withdrawn=False) & ~Q(unicef_id__in=self.get_excluded_household_ids())

    def get_query(self):

        rules = self.get_rules()
        query = Q()
        for rule in rules:
            household_queryset = self.get_household_queryset().filter(
                self.get_basic_query() & rule.get_household_query()
            )
            household_ids_from_individuals = (
                self.get_individual_queryset()
                .filter(rule.get_individual_query() & Q(household__in=household_queryset))
                .values_list("household_id")
            )
            query |= Q(id__in=household_ids_from_individuals)
        return query


class TargetingCriteriaRuleQueryingMixin:
    """
    Gets query for single block
    combines individual filters block with household filters
    """

    def __init__(self, filters=None, individuals_filters_blocks=None):
        if filters is not None:
            self.filters = filters
        if individuals_filters_blocks is not None:
            self.individuals_filters_blocks = individuals_filters_blocks

    def get_filters(self):
        return self.filters

    def get_individuals_filters_blocks(self):
        return self.individuals_filters_blocks

    def get_criteria_string(self):
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

    def get_household_query(self):
        query = Q()
        filters = self.get_filters()
        for ruleFilter in filters:
            query &= ruleFilter.get_query()
        return query

    def get_individual_query(self):
        query = Q()
        individuals_filters_blocks = self.get_individuals_filters_blocks()
        for individuals_filters_block in individuals_filters_blocks:
            query &= individuals_filters_block.get_query()
        return query


class TargetingIndividualRuleFilterBlockMixin:
    def __init__(self, individual_block_filters=None, target_only_hoh=None):
        if individual_block_filters is not None:
            self.individual_block_filters = individual_block_filters
        if target_only_hoh is not None:
            self.target_only_hoh = target_only_hoh

    def get_individual_block_filters(self):
        return self.individual_block_filters

    def get_criteria_string(self):
        filters = self.get_individual_block_filters()
        filters_string = [x.get_criteria_string() for x in filters]
        return f"({' AND '.join(filters_string).strip()})"

    def get_basic_individual_query(self):
        return Q(duplicate=False) & Q(withdrawn=False)

    def get_query(self):
        individuals_query = self.get_basic_individual_query()
        filters = self.get_individual_block_filters()
        filtered = False
        search_query = SearchQuery("")

        for ruleFilter in filters:
            filtered = True
            if ruleFilter.field_name in ("observed_disability", "full_name"):
                for arg in ruleFilter.arguments:
                    search_query &= SearchQuery(arg)
            else:
                individuals_query &= ruleFilter.get_query()
        if not filtered:
            return Q()
        if self.target_only_hoh:
            # only filtering against heads of household
            individuals_query &= Q(heading_household__isnull=False)
        return individuals_query
        individual_query = Individual.objects

        # if isinstance(search_query, CombinedSearchQuery):
        #     q = individual_query.filter(vector_column=search_query).filter(individuals_query)
        # else:
        #     q = individual_query.filter(individuals_query)
        #
        # households_id =  .values_list("household_id", flat=True)
        # return Q(id__in=households_id)


class TargetingCriteriaFilterMixin:
    COMPARISION_ATTRIBUTES = {
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
    )

    def get_criteria_string(self):
        return f"{{{self.field_name} {self.comparision_method} ({','.join([str(x) for x in self.arguments])})}}"

    def get_lookup_prefix(self, associated_with):
        return "individuals__" if associated_with == _INDIVIDUAL else ""

    def prepare_arguments(self, arguments, field_attr):
        is_flex_field = get_attr_value("is_flex_field", field_attr, False)
        if not is_flex_field:
            return arguments
        type = get_attr_value("type", field_attr, None)
        if type == TYPE_DECIMAL:
            return [float(arg) for arg in arguments]
        if type == TYPE_INTEGER:
            return [int(arg) for arg in arguments]
        return arguments

    def get_query_for_lookup(
        self,
        lookup,
        field_attr,
    ):
        select_many = get_attr_value("type", field_attr, None) == TYPE_SELECT_MANY
        comparision_attribute = TargetingCriteriaFilterMixin.COMPARISION_ATTRIBUTES.get(self.comparision_method)
        args_count = comparision_attribute.get("arguments")
        if self.arguments is None:
            logger.error(f"{self.field_name} {self.comparision_method} filter query expect {args_count} " f"arguments")
            raise ValidationError(
                f"{self.field_name} {self.comparision_method} filter query expect {args_count} " f"arguments"
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
                f"{self.field_name} {self.comparision_method} filter query expect {args_count} "
                f"arguments gets {args_input_count}"
            )
            raise ValidationError(
                f"{self.field_name} {self.comparision_method} filter query expect {args_count} "
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
            query = Q(**{f"{lookup}{comparision_attribute.get('lookup')}": argument})
        if comparision_attribute.get("negative"):
            return ~query
        return query

    def get_query_for_core_field(self):
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
            return get_query(self.comparision_method, self.arguments)
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

    def get_query_for_flex_field(self):
        flex_field_attr = FlexibleAttribute.objects.get(name=self.field_name)
        if not flex_field_attr:
            logger.error(f"There are no Flex Field Attributes associated with this fieldName {self.field_name}")
            raise ValidationError(
                f"There are no Flex Field Attributes associated with this fieldName {self.field_name}"
            )
        lookup_prefix = self.get_lookup_prefix(_INDIVIDUAL if flex_field_attr.associated_with == 1 else _HOUSEHOLD)
        lookup = f"{lookup_prefix}flex_fields__{flex_field_attr.name}"
        return self.get_query_for_lookup(lookup, flex_field_attr)

    def get_query(self):
        if not self.is_flex_field:
            return self.get_query_for_core_field()
        return self.get_query_for_flex_field()

    def __str__(self):
        return f"{self.field_name} {self.comparision_method} {self.arguments}"
