import datetime as dt
import enum
from typing import List

from django.conf import settings
from django.contrib.postgres.fields import IntegerRangeField
from django.contrib.postgres.validators import RangeMinValueValidator, RangeMaxValueValidator
from django.db import models
from model_utils.models import UUIDModel
from psycopg2.extras import NumericRange


def get_serialized_range():
    return NumericRange(1, 101)


class TargetStatus(enum.Enum):
    IN_PROGRESS = 'In Progress'
    FINALIZED = 'Finalized'

    @classmethod
    def get_choices(cls) -> List[tuple]:
        return [(field.name, field.value) for field in cls]


class TargetPopulation(UUIDModel):
    _STATE_CHOICES = TargetStatus.get_choices()
    # fields
    name = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_edited_at = models.DateTimeField(auto_now=False,
                                          null=True,
                                          default=dt.datetime.today())
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="target_populations",
        null=True,
    )
    households = models.ManyToManyField("household.Household",
                                        related_name="target_populations")
    # saves (min, max) individuals from households.
    num_individuals_household = IntegerRangeField(
        default=get_serialized_range,
        blank=True,
        validators=[RangeMinValueValidator(1),
                    RangeMaxValueValidator(50)])
    status = models.CharField(max_length=120,
                              blank=False,
                              choices=_STATE_CHOICES,
                              null=False,
                              default=TargetStatus.IN_PROGRESS)
