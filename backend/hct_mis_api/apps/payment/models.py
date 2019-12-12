from django.db import models
from django.utils.translation import ugettext_lazy as _

from hct_mis_api.apps.utils.models import TimeStampedUUIDModel


class PaymentRecord(TimeStampedUUIDModel):
    DELIVERY_TYPE_CHOICE = (
        ('DELIVERED', _('Delivered')),
        ('IN_PROGRESS', _('In Progress')),
    )
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    cash_assist_id = models.CharField(max_length=255)
    delivery_type = models.CharField(
        max_length=255,
        choices=DELIVERY_TYPE_CHOICE,
    )
    cash_plan = models.ForeignKey('program.CashPlan', on_delete=models.CASCADE, related_name='payment_records')
    household = models.ForeignKey('household.Household', on_delete=models.CASCADE, related_name='payment_records')
