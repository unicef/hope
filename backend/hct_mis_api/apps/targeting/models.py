"""Models for target population and target rules."""

import datetime as dt
import enum
import functools
from typing import List

from django.conf import settings
from django.contrib.postgres.fields import IntegerRangeField
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.validators import (
    RangeMinValueValidator,
    RangeMaxValueValidator,
)
from django.db import models
from model_utils.models import UUIDModel
from psycopg2.extras import NumericRange

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


class EnumGetChoices(enum.Enum):
    def __init__(self, *args, **kwargs):
        super().__init__()

    @classmethod
    def get_choices(cls) -> List[tuple]:
        return [(field.name, field.value) for field in cls]


class TargetStatus(EnumGetChoices):
    IN_PROGRESS = "In Progress"
    FINALIZED = "Finalized"


class TargetPopulation(UUIDModel):
    """Model for target populations.

    Has N:N association with households.
    """

    STATE_CHOICES = TargetStatus.get_choices()
    # fields
    name = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # TODO(codecakes): check and use auditlog instead.
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
    total_households = models.IntegerField(default=0)
    total_family_size = models.IntegerField(default=0)
    households = models.ManyToManyField(
        "household.Household", related_name="target_populations"
    )


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
        age_min = 0
        age_max = 0
        today = dt.date.today()
        this_year = today.year
        year_min = this_year - rule_obj.get("age_min", age_min)
        year_max = this_year - rule_obj.get("age_max", age_max)
        if year_min <= year_max < this_year:
            dob_min = dt.date(year_min, 1, 1)
            dob_max = dt.date(year_max, 12, 31)
            return {
                "head_of_household__dob__gte": dob_min,
                "head_of_household__dob__lte": dob_max,
            }
        return {}

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
