"""Models for target population and target rules."""

import datetime as dt
import functools
from typing import List

from django.db.models import Q

from core.utils import EnumGetChoices
from django.conf import settings
from django.contrib.postgres.fields import IntegerRangeField
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.validators import (
    RangeMinValueValidator,
    RangeMaxValueValidator,
)
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from psycopg2.extras import NumericRange
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


class TargetStatus(EnumGetChoices):
    DRAFT = "Draft"
    APPROVED = "Approved"
    FINALIZED = "Finalized"


class TargetPopulation(TimeStampedUUIDModel):
    """Model for target populations.

    Has N:N association with households.
    """

    STATE_CHOICES = TargetStatus.get_choices()
    # fields
    name = models.TextField(unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="target_populations",
        null=True,
    )
    status = models.CharField(
        max_length=_MAX_LEN, choices=STATE_CHOICES, default=TargetStatus.DRAFT,
    )
    households = models.ManyToManyField(
        "household.Household",
        related_name="target_populations",
        through="HouseholdSelection",
    )
    candidate_list_total_households = models.PositiveIntegerField(
        blank=True, null=True
    )
    candidate_list_total_individuals = models.PositiveIntegerField(
        blank=True, null=True
    )
    final_list_total_households = models.PositiveIntegerField(
        blank=True, null=True
    )
    final_list_total_individuals = models.PositiveIntegerField(
        blank=True, null=True
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

    _total_households = models.PositiveIntegerField(default=0)
    _total_family_size = models.PositiveIntegerField(default=0)

    @property
    def total_households(self):
        """Gets sum of all household numbers from association."""
        return (
            self.households.count()
            if not self._total_households
            else self._total_households
        )

    @property
    def final_list(self):
        if self.status == TargetStatus.DRAFT:
            return []
        return self.households.filter(final=True)


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
        "household.Household", on_delete=models.CASCADE
    )
    target_population = models.ForeignKey(
        "TargetPopulation", on_delete=models.CASCADE
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


class TargetingCriteria(TimeStampedUUIDModel):
    """
    This is a set of ORed Rules. These are either applied for a candidate list
    (against Golden Record) or for a final list (against the approved candidate
    list).
    """

    pass

    def to_query_dict(self):
        if self.rules.count() == 0:
            return None
        query = None
        for criteria in self.rules:
            if query is None:
                query = Q(criteria.get_query)


class TargetingCriteriaRule(TimeStampedUUIDModel):
    """
    This is a set of ANDed Filters.
    """

    targeting_criteria = models.ForeignKey(
        "TargetingCriteria", related_name="rules", on_delete=models.CASCADE,
    )

    def get_query(self):
        pass


class TargetingCriteriaRuleFilter(TimeStampedUUIDModel):
    """
    This is one explicit filter like: 
        :Age <> 10-20
        :Sex = Female
        :Sex != Male
    """

    COMPARISON_CHOICES = Choices(
        ("EQUALS", _("Equals")),
        ("CONTAINS", _("Contains")),
        ("NOT_CONTAINS", _("Does not contain")),
        ("RANGE", _("In between <>")),
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
    field_name = models.CharField(max_length=20)
    arguments = JSONField(
        help_text="""
            Array of arguments
            """
    )

    def get_query_for_cor_field(self):
        pass

    def get_query(self):
        if self.comparision_method == "Equals":
            pass


class TargetRule(models.Model):
    """Model for storing each rule as a seperate entry.

     Decoupled and belongs to a target population entry.

     There are two attributes to look out for.
     core_fields will have fixed set of key attributes.
     flex-fields may vary in terms of keys per entry.

     Key attributes are like:
        - intake_group
        - sex
        - age_min
        - age_max
        - school_distance_min
        - school_distance_max
        - num_individuals_min
        - num_individuals_max
    
    TODO(Jan): Delete when the model approach above is done.
     """

    flex_rules = JSONField()
    core_rules = JSONField()
    target_population = models.ForeignKey(
        "TargetPopulation",
        related_name="target_rules",
        on_delete=models.PROTECT,
    )


class FilterAttrType(models.Model):
    """Mapping of field:field_type.

    Gets core and flex field meta info per field.
    """

    flex_field_types = JSONField()
    core_field_types = JSONField()

    # TODO(codecakes): add during search filter task.
    @classmethod
    def apply_filters(cls, rule_obj: dict) -> List:
        return [
            functools.partial(functor, rule_obj)
            for functor in (
                cls.get_age,
                cls.get_gender,
                cls.get_family_size,
                cls.get_intake_group,
            )
        ]

    @classmethod
    def get_age(cls, rule_obj: dict) -> dict:
        age_min = rule_obj.get("age_min")
        age_max = rule_obj.get("age_max")
        result = {}
        this_year = dt.date.today().year
        if age_min:
            result["head_of_household_dob__year__lte"] = this_year - age_min
        if age_max:
            result["head_of_household_dob__year__gte"] = this_year - age_max
        return result

    @classmethod
    def get_gender(cls, rule_obj: dict) -> dict:
        if "sex" in rule_obj:
            return {"head_of_household__sex": rule_obj["sex"]}
        return {}

    @classmethod
    def get_family_size(cls, rule_obj: dict) -> dict:
        if (
            "num_individuals_min" in rule_obj
            and "num_individuals_max" in rule_obj
        ):
            return {
                "family_size__gte": rule_obj["num_individuals_min"],
                "family_size__lte": rule_obj["num_individuals_max"],
            }
        return {}

    @classmethod
    def get_intake_group(cls, rule_obj: dict) -> dict:
        if "intake_group" in rule_obj:
            return {
                "registration_data_import_id__name": rule_obj["intake_group"],
            }
        return {}
