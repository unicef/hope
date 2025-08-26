from django.db import models
from django.db.models import JSONField

from hope.models.payment import Payment
from hope.models.utils import TimeStampedUUIDModel


class PaymentHouseholdSnapshot(TimeStampedUUIDModel):
    snapshot_data = JSONField(default=dict)
    household_id = models.UUIDField()
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name="household_snapshot")

    class Meta:
        app_label = "payment"
