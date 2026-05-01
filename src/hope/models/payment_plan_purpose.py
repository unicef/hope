from django.db import models
from django.utils.translation import gettext_lazy as _

from hope.models.utils import TimeStampedUUIDModel, UnicefIdentifiedModel


class PaymentPlanPurpose(TimeStampedUUIDModel, UnicefIdentifiedModel):
    business_area = models.ForeignKey(
        "core.BusinessArea", on_delete=models.CASCADE, related_name="payment_plan_purposes"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        app_label = "core"
        verbose_name = _("Payment Plan Purpose")
        constraints = [
            models.UniqueConstraint(
                fields=["name", "business_area"],
                name="unique_paymentplanpurpose_name_business_area",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.business_area})"
