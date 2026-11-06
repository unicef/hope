from django.db import models

from hope.models.utils import LongNameIndex, TimeStampedUUIDModel


class PaymentListSplitPayments(TimeStampedUUIDModel):
    payment_list_split = models.ForeignKey(
        "payment.PaymentListSplit",
        on_delete=models.CASCADE,
        related_name="payment_list_split",
        db_column="payment_plan_split_id",
    )
    payment = models.ForeignKey(
        "payment.Payment",
        on_delete=models.CASCADE,
        related_name="payment_list_split_payment",
    )

    class Meta:
        app_label = "payment"
        db_table = "payment_paymentplansplitpayments"
        unique_together = ("payment_list_split", "payment")
        ordering = ("id",)
        indexes = [
            LongNameIndex(fields=["created_at"], name="payment_paymentplansplitpayments_created_at_e95fd4c6"),
            LongNameIndex(fields=["updated_at"], name="payment_paymentplansplitpayments_updated_at_ced8e717"),
        ]
