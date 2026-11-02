from django.db import models

from hope.models.utils import LongNameIndex, TimeStampedUUIDModel


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
        ordering = ("id",)
        indexes = [
            LongNameIndex(fields=["created_at"], name="payment_paymentplansplitpayments_created_at_e95fd4c6"),
            LongNameIndex(fields=["updated_at"], name="payment_paymentplansplitpayments_updated_at_ced8e717"),
        ]
