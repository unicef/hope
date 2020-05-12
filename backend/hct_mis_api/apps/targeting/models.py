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

from core.core_fields_attributes import CORE_FIELDS_ATTRIBUTES, _INDIVIDUAL
from core.models import FlexibleAttribute
from household.models import Individual, Household
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
        validators=[
            RangeMinValueValidator(min_range),
            RangeMaxValueValidator(max_range),
        ],
    )


class TargetPopulation(SoftDeletableModel, TimeStampedUUIDModel):
    """Model for target populations.

    Has N:N association with households.
    """

    name = models.TextField(unique=True)
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
    business_area = models.ForeignKey(
        "core.BusinessArea", null=True, on_delete=models.CASCADE
    )
    STATUS_CHOICES = (
        ("DRAFT", _("Open")),
        ("APPROVED", _("Closed")),
        ("FINALIZED", _("Sent")),
    )

    status = models.CharField(
        max_length=_MAX_LEN, choices=STATUS_CHOICES, default="DRAFT",
    )
    households = models.ManyToManyField(
        "household.Household",
        related_name="target_populations",
        through="HouseholdSelection",
    )
    candidate_list_total_households = models.PositiveIntegerField(
        blank=True, null=True,
    )
    candidate_list_total_individuals = models.PositiveIntegerField(
        blank=True, null=True,
    )
    final_list_total_households = models.PositiveIntegerField(
        blank=True, null=True,
    )
    final_list_total_individuals = models.PositiveIntegerField(
        blank=True, null=True,
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

    @property
    def final_list(self):
        if self.status == "DRAFT":
            return []
        return (
            self.households.filter(selections__final=True)
            .order_by("created_at")
            .distinct()
        )

    @property
    def candidate_stats(self):
        if self.status == "DRAFT":
            households_ids = Household.objects.filter(
                self.candidate_list_targeting_criteria.get_query()
            ).values_list("id")
        else:
            households_ids = self.households.values_list("id")
        delta18 = relativedelta(years=+18)
        date18ago = datetime.datetime.now() - delta18
        child_male = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__gt=date18ago,
            sex="MALE",
        ).count()
        child_female = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__gt=date18ago,
            sex="FEMALE",
        ).count()

        adult_male = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__lte=date18ago,
            sex="MALE",
        ).count()
        adult_female = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__lte=date18ago,
            sex="FEMALE",
        ).count()
        return {
            "child_male": child_male,
            "child_female": child_female,
            "adult_male": adult_male,
            "adult_female": adult_female,
        }

    @property
    def final_stats(self):
        if self.status == "Draft":
            return None
        elif self.status == "APPROVED":
            households_ids = Household.objects.filter(
                self.candidate_list_targeting_criteria.get_query()
            ).values_list("id")
        else:
            households_ids = self.final_list.values_list("id")
        delta18 = relativedelta(years=+18)
        date18ago = datetime.datetime.now() - delta18
        child_male = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__gt=date18ago,
            sex="MALE",
        ).count()
        child_female = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__gt=date18ago,
            sex="FEMALE",
        ).count()

        adult_male = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__lte=date18ago,
            sex="MALE",
        ).count()
        adult_female = Individual.objects.filter(
            household__id__in=households_ids,
            birth_date__lte=date18ago,
            sex="FEMALE",
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
    target_population = models.ForeignKey(
        "TargetPopulation", on_delete=models.CASCADE, related_name="selections"
    )
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

    pass


class TargetingCriteriaRuleQueryingMixin:
    def __init__(self, filters=None):
        if filters is None:
            return
        self.filters = filters

    def get_query(self):
        query = Q()
        filters = (
            self.filters
            if isinstance(self.filters, list)
            else self.filters.all()
        )
        for ruleFilter in filters:
            query &= ruleFilter.get_query()
        return query


class TargetingCriteriaRule(
    TimeStampedUUIDModel, TargetingCriteriaRuleQueryingMixin
):
    """
    This is a set of ANDed Filters.
    """

    targeting_criteria = models.ForeignKey(
        "TargetingCriteria", related_name="rules", on_delete=models.CASCADE,
    )


class TargetingCriteriaRuleFilter(TimeStampedUUIDModel):
    """
    This is one explicit filter like:
        :Age <> 10-20
        :Residential Status = Refugee
        :Residential Status != Refugee
    """

    COMPARISION_ATTRIBUTES = {
        "EQUALS": {
            "arguments": 1,
            "lookup": "",
            "negative": False,
            "supported_types": ["INTEGER", "SELECT_ONE", "STRING"],
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
            "supported_types": ["INTEGER"],
        },
        "NOT_IN_RANGE": {
            "arguments": 2,
            "lookup": "__range",
            "negative": True,
            "supported_types": ["INTEGER"],
        },
        "GREATER_THAN": {
            "arguments": 1,
            "lookup": "__gt",
            "negative": False,
            "supported_types": ["INTEGER"],
        },
        "LESS_THAN": {
            "arguments": 1,
            "lookup": "__lt",
            "negative": False,
            "supported_types": ["INTEGER"],
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
    comparision_method = models.CharField(
        max_length=20, choices=COMPARISON_CHOICES,
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

    def get_query_for_lookup(self, lookup, select_many=False):
        comparision_attribute = TargetingCriteriaRuleFilter.COMPARISION_ATTRIBUTES.get(
            self.comparision_method
        )
        args_count = comparision_attribute.get("arguments")
        if self.arguments is None:
            raise ValidationError(
                f"{self.field_name} {self.comparision_method} filter query expect {args_count} "
                f"arguments"
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
            query = Q(
                **{f"{lookup}{comparision_attribute.get('lookup')}": argument}
            )
        if comparision_attribute.get("negative"):
            return ~query
        return query

    def get_query_for_core_field(self):
        core_fields = CORE_FIELDS_ATTRIBUTES
        core_field_attrs = [
            attr for attr in core_fields if attr.get("name") == self.field_name
        ]
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
        return self.get_query_for_lookup(
            f"{'individuals__' if core_field_attr['associated_with']==_INDIVIDUAL else ''}{lookup}",
            select_many=core_field_attr.get("type") == "SELECT_MANY",
        )

    def get_query_for_flex_field(self):
        flex_field_attr = FlexibleAttribute.objects.get(name=self.field_name)
        if not flex_field_attr:
            raise ValidationError(
                f"There are no Core Field Attributes associated with this fieldName {self.field_name}"
            )
        lookup = f"{'individuals__' if flex_field_attr.associated_with else ''}flex_fields__{flex_field_attr.name}"
        return self.get_query_for_lookup(
            lookup, select_many=flex_field_attr.type == "SELECT_MANY",
        )

    def get_query(self):
        if not self.is_flex_field:
            return self.get_query_for_core_field()
        return self.get_query_for_flex_field()
