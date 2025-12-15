from django.db import models

from hope.models.utils import TimeStampedUUIDModel


class PaymentPlanSplitPayments(TimeStampedUUIDModel):
    payment_plan_split = models.ForeignKey(
        "payment.PaymentPlanSplit",
        on_delete=models.CASCADE,
        related_name="payment_plan_split",
    )
    payment = models.ForeignKey(
        "payment.Payment",
        on_delete=models.CASCADE,
        related_name="payment_plan_split_payment",
    )

    class Meta:
        app_label = "payment"
        unique_together = ("payment_plan_split", "payment")
