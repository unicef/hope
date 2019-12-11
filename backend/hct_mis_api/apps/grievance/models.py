from django.conf import settings
from django.db import models
from model_utils.models import UUIDModel


class Grievance(UUIDModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    opened_date = models.DateTimeField()
    household = models.ForeignKey('household.Household', related_name='grievances')
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='grievances')

    def __str__(self):
        return self.name
