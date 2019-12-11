from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from model_utils.models import UUIDModel


class TargetPopulation(UUIDModel):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='target_populations')
    rules = JSONField()
    households = models.ManyToManyField('household.Household', related_name='target_populations')

    def __str__(self):
        return self.name
