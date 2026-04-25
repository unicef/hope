from django.db import models
from django.utils.translation import gettext_lazy as _

from hope.models.utils import TimeStampedUUIDModel


class PaymentPlanPurpose(TimeStampedUUIDModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        app_label = "core"
        verbose_name = _("Payment Plan Purpose")

    def __str__(self) -> str:
        return self.name
