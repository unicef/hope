from django.conf import settings
from django.db import models

from hct_mis_api.apps.utils.models import TimeStampedUUIDModel


class Grievance(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    opened_date = models.DateTimeField()
    household = models.ForeignKey('household.Household', related_name='grievances', on_delete=models.CASCADE)
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='grievances', on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
