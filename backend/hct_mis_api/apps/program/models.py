from django.conf import settings
from django.db import models

from hct_mis_api.apps.utils.models import TimeStampedUUIDModel


class Program(TimeStampedUUIDModel):
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'
    STATUS_CHOICE = (
        ACTIVE, _('In progress'),
        COMPLETED, _('Done'),
    )
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICE,
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.CharField(max_length=255)
    program_ca_id = models.CharField(max_length=255)
    location = models.ForeignKey('core.Location', related_name='programs', on_delete=models.CASCADE)
    budget = models.DecimalField()


class CashPlan(TimeStampedUUIDModel):
    program = models.ForeignKey('Progarm', related_name='cash_plans', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    disbursement_date = models.DateTimeField()
    number_of_households = models.PositiveIntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='cash_plans', on_delete=models.SET_NULL)
    coverage_duration = models.PositiveIntegerField()
    coverage_units = models.CharField(max_length=255)
    target_population = models.ForeignKey('targeting.TargetPopulation', related_name='cash_plans',
                                          on_delete=models.CASCADE)
    cash_assist_id = models.CharField(max_length=255)
    distribution_modality = models.CharField(max_length=255)
    fsp = models.CharField(max_length=255)
