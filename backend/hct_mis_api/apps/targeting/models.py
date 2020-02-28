import enum
from typing import List

from django.conf import settings
from django.contrib.postgres.fields import IntegerRangeField
from django.contrib.postgres.validators import RangeMinValueValidator, RangeMaxValueValidator
from django.db import models
from household.models import Household
from model_utils.models import UUIDModel
from psycopg2.extras import NumericRange

_MAX_LEN = 256


def get_serialized_range(min_range=None, max_range=None):
    return NumericRange(min_range or 1, max_range or 101)


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
    # saves (min, max) individuals from households.
    num_individuals_household = IntegerRangeField(
        default=get_serialized_range,
        blank=True,
        validators=[RangeMinValueValidator(1),
                    RangeMaxValueValidator(50000)])
    status = models.CharField(max_length=_MAX_LEN,
                              blank=False,
                              choices=_STATE_CHOICES,
                              null=False,
                              default=TargetStatus.IN_PROGRESS)

    @classmethod
    def bulk_add_households(cls, household_ca_ids):
        # add households
        households = [
            Household.objects.get(
                household_ca_id=target_household["household_ca_id"])
            for target_household in household_ca_ids
        ]


class TargetFilter(models.Model):
    _GENDER_CHOICES = Gender.get_choices()

    intake_group = models.CharField(max_length=_MAX_LEN, null=False)
    sex = models.CharField(max_length=2, choices=_GENDER_CHOICES)
    age = models.IntegerField()
    school_distance_min = models.IntegerField()
    school_distance_max = models.IntegerField()
    num_individuals_household_min = models.IntegerField()
    num_individuals_household_max = models.IntegerField()
    target_population = models.ForeignKey("TargetPopulation",
                                          related_name="target_filters",
                                          on_delete=models.PROTECT,
                                          null=False)
