import enum
from typing import List

from django.conf import settings
from django.contrib.postgres.fields import IntegerRangeField
from django.contrib.postgres.validators import RangeMinValueValidator, RangeMaxValueValidator
from django.db import models
from django.db.models import Q
from household.models import Household
from model_utils.models import UUIDModel
from psycopg2.extras import NumericRange

_MAX_LEN = 256
_MIN_RANGE = 1
_MAX_RANGE = 200


def get_serialized_range(min_range=None, max_range=None):
    return NumericRange(min_range or _MIN_RANGE, max_range or _MAX_RANGE)


def get_integer_range(min_range=None, max_range=None):
    min_range = min_range or _MIN_RANGE
    max_range = max_range or _MAX_RANGE
    return IntegerRangeField(default=get_serialized_range,
                             blank=True,
                             validators=[
                                 RangeMinValueValidator(min_range),
                                 RangeMaxValueValidator(max_range)
                             ])


class EnumGetChoices(enum.Enum):
    def __init__(self, *args, **kwargs):
        super().__init__()

    @classmethod
    def get_choices(cls) -> List[tuple]:
        return [(field.name, field.value) for field in cls]


class TargetStatus(EnumGetChoices):
    IN_PROGRESS = 'In Progress'
    FINALIZED = 'Finalized'


class Gender(EnumGetChoices):
    M = 'M'
    F = 'F'


class TargetPopulation(UUIDModel):
    _STATE_CHOICES = TargetStatus.get_choices()
    # fields
    name = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_edited_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="target_populations",
        null=True,
    )
    households = models.ManyToManyField("household.Household",
                                        related_name="target_populations",
                                        blank=False)

    status = models.CharField(max_length=_MAX_LEN,
                              blank=False,
                              choices=_STATE_CHOICES,
                              null=False,
                              default=TargetStatus.IN_PROGRESS)

    @classmethod
    def bulk_get_households(cls, household_list):
        """Get associated households."""
        household_entries = (household["household_ca_id"]
                             for household in household_list)
        return Household.objects.filter(
            Q(household_ca_id__in=household_entries)).all()


class TargetFilter(models.Model):
    _GENDER_CHOICES = Gender.get_choices()

    intake_group = models.CharField(max_length=_MAX_LEN, null=False)
    sex = models.CharField(max_length=2, choices=_GENDER_CHOICES)
    age_min = models.IntegerField(max_length=_MAX_LEN, null=True)
    age_max = models.IntegerField(max_length=_MAX_LEN, null=True)
    school_distance_min = models.IntegerField(max_length=_MAX_LEN, null=True)
    school_distance_max = models.IntegerField(max_length=_MAX_LEN, null=True)
    num_individuals_min = models.IntegerField(max_length=_MAX_LEN, null=True)
    num_individuals_max = models.IntegerField(max_length=_MAX_LEN, null=True)
    school_distance_range = get_integer_range()
    target_population = models.ForeignKey("TargetPopulation",
                                          related_name="target_filters",
                                          on_delete=models.PROTECT,
                                          null=False)
