import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.postgres.fields import IntegerRangeField
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.validators import (
    RangeMinValueValidator,
    RangeMaxValueValidator,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from model_utils.models import SoftDeletableModel
from psycopg2.extras import NumericRange


from core.core_fields_attributes import CORE_FIELDS_ATTRIBUTES, _INDIVIDUAL, TYPE_SELECT_MANY, _HOUSEHOLD
from core.models import FlexibleAttribute
from household.models import Individual, Household, MALE, FEMALE
from utils.models import TimeStampedUUIDModel

_MAX_LEN = 256
_MIN_RANGE = 1
_MAX_RANGE = 200


def get_serialized_range(min_range=None, max_range=None):
    return NumericRange(min_range or _MIN_RANGE, max_range or _MAX_RANGE)


def get_integer_range(min_range=None, max_range=None):
    """Numeric Range support for saving as InterRangeField."""
    min_range = min_range or _MIN_RANGE
    max_range = max_range or _MAX_RANGE
    return IntegerRangeField(
        default=get_serialized_range,
        blank=True,
        validators=[RangeMinValueValidator(min_range), RangeMaxValueValidator(max_range)],
    )


class TargetPopulation(SoftDeletableModel, TimeStampedUUIDModel):
    """Model for target populations.

    Has N:N association with households.
    """

    STATUS_DRAFT = "DRAFT"
    STATUS_APPROVED = "APPROVED"
    STATUS_FINALIZED = "FINALIZED"

    name = models.TextField(unique=True)
    ca_id = models.CharField(max_length=255, null=True)
    ca_hash_id = models.CharField(max_length=255, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="target_populations",
        null=True,
    )
    approved_at = models.DateTimeField(null=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_target_populations",
        null=True,
    )
    finalized_at = models.DateTimeField(null=True)
    finalized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="finalized_target_populations",
        null=True,
    )
    business_area = models.ForeignKey("core.BusinessArea", null=True, on_delete=models.CASCADE)
    STATUS_CHOICES = (
        (STATUS_DRAFT, _("Open")),
        (STATUS_APPROVED, _("Closed")),
        (STATUS_FINALIZED, _("Sent")),
    )

    status = models.CharField(
        max_length=_MAX_LEN,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    households = models.ManyToManyField(
        "household.Household",
        related_name="target_populations",
        through="HouseholdSelection",
    )
    candidate_list_total_households = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    candidate_list_total_individuals = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    final_list_total_households = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    final_list_total_individuals = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    selection_computation_metadata = models.TextField(
        blank=True,
        null=True,
        help_text="""This would be the metadata written to by say Corticon on how
        it arrived at the selection it made.""",
    )
    program = models.ForeignKey(
        "program.Program",
        blank=True,
        null=True,
        help_text="""Set only when the target population moves from draft to
            candidate list frozen state (approved)""",
        on_delete=models.SET_NULL,
    )
    candidate_list_targeting_criteria = models.OneToOneField(
        "TargetingCriteria",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="target_population_candidate",
    )
    final_list_targeting_criteria = models.OneToOneField(
        "TargetingCriteria",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="target_population_final",
    )
    sent_to_datahub = models.BooleanField(
        default=False,
        help_text="""
            Flag set when TP is processed by airflow task
            """,
    )
    steficon_rule = models.ForeignKey(
        "steficon.Rule", null=True, on_delete=models.SET_NULL, related_name="target_populations"
    )
    vulnerability_score_min = models.DecimalField(
        null=True,
        decimal_places=3,
        max_digits=6,
        help_text="Written by a tool such as Corticon.",
    )
    vulnerability_score_max = models.DecimalField(
        null=True,
        decimal_places=3,
        max_digits=6,
        help_text="Written by a tool such as Corticon.",
    )

    @property
    def vulnerability_score_filtered_households(self):
        queryset = self.households
        if self.vulnerability_score_max is not None:
            queryset = queryset.filter(selections__vulnerability_score__lte=self.vulnerability_score_max)
        if self.vulnerability_score_min is not None:
            queryset = queryset.filter(selections__vulnerability_score__gte=self.vulnerability_score_min)
        return queryset.distinct()

    @property
    def final_list(self):
        if self.status == TargetPopulation.STATUS_DRAFT:
            return []
        return (
            self.vulnerability_score_filtered_households.filter(selections__final=True)
            .order_by("created_at")
            .distinct()
        )

    @property
    def candidate_stats(self):
        if self.status == TargetPopulation.STATUS_DRAFT:
            households_ids = Household.objects.filter(self.candidate_list_targeting_criteria.get_query()).values_list(
                "id"
            )
        else:
            households_ids = self.vulnerability_score_filtered_households.values_list("id")
        delta18 = relativedelta(years=+18)
        date18ago = datetime.datetime.now() - delta18
        child_male = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__gt=date18ago,
            sex=MALE,
        ).count()
        child_female = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__gt=date18ago,
            sex=FEMALE,
        ).count()

        adult_male = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__lte=date18ago,
            sex=MALE,
        ).count()
        adult_female = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__lte=date18ago,
            sex=FEMALE,
        ).count()
        return {
            "child_male": child_male,
            "child_female": child_female,
            "adult_male": adult_male,
            "adult_female": adult_female,
        }

    def get_criteria_string(self):
        return self.candidate_list_targeting_criteria.get_criteria_string()

    @property
    def targeting_criteria_string(self):
        return self.get_criteria_string()

    @property
    def final_stats(self):
        if self.status == TargetPopulation.STATUS_DRAFT:
            return None
        elif self.status == TargetPopulation.STATUS_APPROVED:
            households_ids = self.vulnerability_score_filtered_households.filter(
                self.final_list_targeting_criteria.get_query()
            ).values_list("id")
        else:
            households_ids = self.final_list.values_list("id")
        delta18 = relativedelta(years=+18)
        date18ago = datetime.datetime.now() - delta18
        child_male = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__gt=date18ago,
            sex=MALE,
        ).count()
        child_female = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__gt=date18ago,
            sex=FEMALE,
        ).count()

        adult_male = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__lte=date18ago,
            sex=MALE,
        ).count()
        adult_female = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__lte=date18ago,
            sex=FEMALE,
        ).count()
        return {
            "child_male": child_male,
            "child_female": child_female,
            "adult_male": adult_male,
            "adult_female": adult_female,
        }

    class Meta:
        unique_together = ("name", "business_area")


class HouseholdSelection(TimeStampedUUIDModel):
    """
    This model contains metadata associated with the relation between a target
    population and a household. Its understood that once the candidate list of
    households has been frozen, some external system (eg. Corticon) will run
    to calculate vulnerability score. The user (may) filter again then against
    the approved candidate list and mark the households as having been
    'selected' or not (final=True/False). By default a draft list or frozen
    candidate list  will have final set to True.
    """

    household = models.ForeignKey(
        "household.Household",
        on_delete=models.CASCADE,
        related_name="selections",
    )
    target_population = models.ForeignKey("TargetPopulation", on_delete=models.CASCADE, related_name="selections")
    vulnerability_score = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        help_text="Written by a tool such as Corticon.",
    )
    final = models.BooleanField(
        default=True,
        help_text="""
            When set to True, this means the household has been selected from
            the candidate list. Only these households will be sent to
            CashAssist when a sync is run for the associated target population.
            """,
    )


class TargetingCriteriaQueryingMixin:
    def __init__(self, rules=None):
        if rules is None:
            return
        self.rules = rules

    def get_criteria_string(self):
        rules = self.rules if isinstance(self.rules, list) else self.rules.all()
        rules_string = [x.get_criteria_string() for x in rules]
        return " OR ".join(rules_string).strip()

    def get_query(self):
        query = Q()
        rules = self.rules if isinstance(self.rules, list) else self.rules.all()
        for rule in rules:
            query |= rule.get_query()
        return query


class TargetingCriteria(TimeStampedUUIDModel, TargetingCriteriaQueryingMixin):
    """
    This is a set of ORed Rules. These are either applied for a candidate list
    (against Golden Record) or for a final list (against the approved candidate
    list).
    """

    def get_query(self):
        query = super().get_query()
        try:
            if (
                self.target_population_final
                and self.target_population_final.status != TargetPopulation.STATUS_DRAFT
                and self.target_population_final.program is not None
                and self.target_population_final.program.individual_data_needed
            ):
                query &= Q(size__gt=0)
        except TargetPopulation.DoesNotExist:
            pass
        return query


class TargetingCriteriaRuleQueryingMixin:
    def __init__(self, filters=None, individuals_filters_blocks=None):
        if filters is not None:
            self.filters = filters
        if individuals_filters_blocks is not None:
            self.individuals_filters_blocks = individuals_filters_blocks

    def get_criteria_string(self):
        filters = self.filters if isinstance(self.filters, list) else self.filters.all()
        filters_strings = [x.get_criteria_string() for x in filters]
        individuals_filters_blocks = (
            self.individuals_filters_blocks
            if isinstance(self.individuals_filters_blocks, list)
            else self.individuals_filters_blocks.all()
        )
        individuals_filters_blocks_strings = [x.get_criteria_string() for x in individuals_filters_blocks]
        all_strings = []
        if len(filters_strings):
            all_strings.append(f"H({' AND '.join(filters_strings).strip()})")
        if len(individuals_filters_blocks_strings):
            all_strings.append(f"I({' AND '.join(individuals_filters_blocks_strings).strip()})")
        return " AND ".join(all_strings).strip()

    def get_query(self):
        query = Q()
        filters = self.filters if isinstance(self.filters, list) else self.filters.all()
        individuals_filters_blocks = (
            self.individuals_filters_blocks
            if isinstance(self.individuals_filters_blocks, list)
            else self.individuals_filters_blocks.all()
        )
        # Thats household filters
        for ruleFilter in filters:
            query &= ruleFilter.get_query()
        # filter individual block
        for individuals_filters_block in individuals_filters_blocks:
            query &= individuals_filters_block.get_query()
        return query


class TargetingCriteriaRule(TimeStampedUUIDModel, TargetingCriteriaRuleQueryingMixin):
    """
    This is a set of ANDed Filters.
    """

    targeting_criteria = models.ForeignKey(
        "TargetingCriteria",
        related_name="rules",
        on_delete=models.CASCADE,
    )


class TargetingIndividualRuleFilterBlockMixin:
    def __init__(self, individual_block_filters=None):
        if individual_block_filters is not None:
            self.individual_block_filters = individual_block_filters

    def get_criteria_string(self):
        filters = (
            self.individual_block_filters
            if isinstance(self.individual_block_filters, list)
            else self.individual_block_filters.all()
        )
        filters_string = [x.get_criteria_string() for x in filters]
        return f"({' AND '.join(filters_string).strip()})"

    def get_query(self):
        individuals_query = Q()
        filters = (
            self.individual_block_filters
            if isinstance(self.individual_block_filters, list)
            else self.individual_block_filters.all()
        )
        filtered = False
        for ruleFilter in filters:
            filtered = True
            individuals_query &= ruleFilter.get_query()
        if not filtered:
            return Q()
        households_id = Individual.objects.filter(individuals_query).values_list("household_id", flat=True)
        return Q(id__in=households_id)


class TargetingIndividualRuleFilterBlock(
    TimeStampedUUIDModel,
    TargetingIndividualRuleFilterBlockMixin,
):
    targeting_criteria_rule = models.ForeignKey(
        "TargetingCriteriaRule", on_delete=models.CASCADE, related_name="individuals_filters_blocks"
    )


class TargetingCriteriaFilterMixin:

    COMPARISION_ATTRIBUTES = {
        "EQUALS": {
            "arguments": 1,
            "lookup": "",
            "negative": False,
            "supported_types": ["INTEGER", "SELECT_ONE", "STRING"],
        },
        "NOT_EQUALS": {"arguments": 1, "lookup": "", "negative": True, "supported_types": ["INTEGER", "SELECT_ONE"]},
        "CONTAINS": {
            "min_arguments": 1,
            "arguments": 1,
            "lookup": "__icontains",
            "negative": False,
            "supported_types": ["SELECT_MANY", "STRING"],
        },
        "NOT_CONTAINS": {"arguments": 1, "lookup": "__icontains", "negative": True, "supported_types": ["STRING"]},
        "RANGE": {"arguments": 2, "lookup": "__range", "negative": False, "supported_types": ["INTEGER"]},
        "NOT_IN_RANGE": {"arguments": 2, "lookup": "__range", "negative": True, "supported_types": ["INTEGER"]},
        "GREATER_THAN": {"arguments": 1, "lookup": "__gt", "negative": False, "supported_types": ["INTEGER"]},
        "LESS_THAN": {"arguments": 1, "lookup": "__lt", "negative": False, "supported_types": ["INTEGER"]},
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

    def get_query_for_lookup(self, lookup, select_many=False):
        comparision_attribute = TargetingCriteriaRuleFilter.COMPARISION_ATTRIBUTES.get(self.comparision_method)
        args_count = comparision_attribute.get("arguments")
        if self.arguments is None:
            raise ValidationError(
                f"{self.field_name} {self.comparision_method} filter query expect {args_count} " f"arguments"
            )
        args_input_count = len(self.arguments)
        if select_many:
            if args_input_count < 1:
                raise ValidationError(
                    f"{self.field_name} SELECT MULTIPLE CONTAINS filter query expect at least 1 argument"
                )
        elif args_count != args_input_count:
            raise ValidationError(
                f"{self.field_name} {self.comparision_method} filter query expect {args_count} "
                f"arguments gets {args_input_count}"
            )
        argument = self.arguments if args_input_count > 1 else self.arguments[0]

        if select_many:
            query = Q(**{f"{lookup}__contains": argument})
        else:
            query = Q(**{f"{lookup}{comparision_attribute.get('lookup')}": argument})
        if comparision_attribute.get("negative"):
            return ~query
        return query

    def get_query_for_core_field(self):
        core_fields = CORE_FIELDS_ATTRIBUTES
        core_field_attrs = [attr for attr in core_fields if attr.get("name") == self.field_name]
        if len(core_field_attrs) != 1:
            raise ValidationError(
                f"There are no Core Field Attributes associated with this fieldName {self.field_name}"
            )
        core_field_attr = core_field_attrs[0]
        get_query = core_field_attr.get("get_query")
        if get_query:
            return get_query(self.comparision_method, self.arguments)
        lookup = core_field_attr.get("lookup")
        if not lookup:
            raise ValidationError(
                f"Core Field Attributes associated with this fieldName {self.field_name}"
                f" doesn't have get_query method or lookup field"
            )
        lookup_prefix = self.get_lookup_prefix(core_field_attr["associated_with"])
        return self.get_query_for_lookup(
            f"{lookup_prefix}{lookup}",
            select_many=core_field_attr.get("type") == TYPE_SELECT_MANY,
        )

    def get_query_for_flex_field(self):
        flex_field_attr = FlexibleAttribute.objects.get(name=self.field_name)
        if not flex_field_attr:
            raise ValidationError(
                f"There are no Core Field Attributes associated with this fieldName {self.field_name}"
            )
        lookup_prefix = self.get_lookup_prefix(_INDIVIDUAL if flex_field_attr.associated_with == 1 else _HOUSEHOLD)
        lookup = f"{lookup_prefix}flex_fields__{flex_field_attr.name}"
        return self.get_query_for_lookup(
            lookup,
            select_many=flex_field_attr.type == TYPE_SELECT_MANY,
        )

    def get_query(self):
        if not self.is_flex_field:
            return self.get_query_for_core_field()
        return self.get_query_for_flex_field()

    def __str__(self):
        return f"{self.field_name} {self.comparision_method} {self.arguments}"


# TODO It should be household only
class TargetingCriteriaRuleFilter(TimeStampedUUIDModel, TargetingCriteriaFilterMixin):
    """
    This is one explicit filter like:
        :Age <> 10-20
        :Residential Status = Refugee
        :Residential Status != Refugee
    """

    comparision_method = models.CharField(
        max_length=20,
        choices=TargetingCriteriaFilterMixin.COMPARISON_CHOICES,
    )
    targeting_criteria_rule = models.ForeignKey(
        "TargetingCriteriaRule",
        related_name="filters",
        on_delete=models.CASCADE,
    )
    is_flex_field = models.BooleanField(default=False)
    field_name = models.CharField(max_length=50)
    arguments = JSONField(
        help_text="""
            Array of arguments
            """
    )


class TargetingIndividualBlockRuleFilter(TimeStampedUUIDModel, TargetingCriteriaFilterMixin):
    """
    This is one explicit filter like:
        :Age <> 10-20
        :Residential Status = Refugee
        :Residential Status != Refugee
    """

    comparision_method = models.CharField(
        max_length=20,
        choices=TargetingCriteriaFilterMixin.COMPARISON_CHOICES,
    )
    individuals_filters_block = models.ForeignKey(
        "TargetingIndividualRuleFilterBlock",
        related_name="individual_block_filters",
        on_delete=models.CASCADE,
    )
    is_flex_field = models.BooleanField(default=False)
    field_name = models.CharField(max_length=50)
    arguments = JSONField(
        help_text="""
            Array of arguments
            """
    )

    def get_lookup_prefix(self, associated_with):
        return ""
