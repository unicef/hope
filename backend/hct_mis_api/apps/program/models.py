from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from hct_mis_api.apps.utils.models import TimeStampedUUIDModel


class Program(TimeStampedUUIDModel):
    DRAFT = 'DRAFT'
    ACTIVE = 'ACTIVE'
    FINISHED = 'FINISHED'
    STATUS_CHOICE = (
        (DRAFT, _('Draft')),
        (ACTIVE, _('Active')),
        (FINISHED, _('Finished')),
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
    location = models.ForeignKey('core.Location', on_delete=models.CASCADE, related_name='programs')
    budget = models.DecimalField(decimal_places=2, max_digits=12)


class CashPlan(TimeStampedUUIDModel):
    program = models.ForeignKey('Program', on_delete=models.CASCADE, related_name='cash_plans')
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    disbursement_date = models.DateTimeField()
    number_of_households = models.PositiveIntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='cash_plans',
                                   null=True)
    coverage_duration = models.PositiveIntegerField()
    coverage_units = models.CharField(max_length=255)
    target_population = models.ForeignKey('targeting.TargetPopulation', on_delete=models.CASCADE,
                                          related_name='cash_plans')
    cash_assist_id = models.CharField(max_length=255)
    distribution_modality = models.CharField(max_length=255)
    fsp = models.CharField(max_length=255)
