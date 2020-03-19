"""Models for target population and target rules."""

import datetime as dt
import functools
from typing import List

from core.utils import EnumGetChoices
from django.conf import settings
from django.contrib.postgres.fields import IntegerRangeField
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.validators import (
    RangeMinValueValidator,
    RangeMaxValueValidator,
)
from django.db import models
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
    IN_PROGRESS = "In Progress"
    FINALIZED = "Finalized"


class TargetPopulation(TimeStampedUUIDModel):
    """Model for target populations.

    Has N:N association with households.
    """

    STATE_CHOICES = TargetStatus.get_choices()
    # fields
    name = models.TextField(unique=True)
    # TODO(codecakes): check and use auditlog instead.
    # Dependent field. Change to auditlog or change depending modules in future CL.
    last_edited_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="target_populations",
        null=True,
    )
    status = models.CharField(
        max_length=_MAX_LEN,
        choices=STATE_CHOICES,
        default=TargetStatus.IN_PROGRESS,
    )
    households = models.ManyToManyField(
        "household.Household", related_name="target_populations"
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

    @total_households.setter
    def total_households(self, value: int):
        """

        Args:
            value (int): the aggregated value of total households
        """
        self._total_households = value

    @property
    def total_family_size(self):
        """Gets sum of all family sizes from all the households."""
        return (
            (
                self.households.aggregate(models.Sum("family_size")).get(
                    "family_size__sum"
                )
            )
            if not self._total_family_size
            else self._total_family_size
        )

    @total_family_size.setter
    def total_family_size(self, value: int):
        """

        Args:
            value (int): the aggregated value of the total family sizes.
        """
        self._total_family_size = value


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
