from django.db import models
from django.db.models import JSONField

from hope.models.payment import Payment
from hope.models.utils import LongNameIndex, TimeStampedUUIDModel


class PaymentHouseholdSnapshot(TimeStampedUUIDModel):
    snapshot_data = JSONField(default=dict, blank=True)
    household_id = models.UUIDField()
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name="household_snapshot")

    class Meta:
        app_label = "payment"
        ordering = ("id",)
        indexes = [
            LongNameIndex(fields=["created_at"], name="payment_paymenthouseholdsnapshot_created_at_dbec5131"),
            LongNameIndex(fields=["updated_at"], name="payment_paymenthouseholdsnapshot_updated_at_8f771f31"),
        ]
