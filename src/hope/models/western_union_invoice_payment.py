from django.db import models


class WesternUnionInvoicePayment(models.Model):
    STATUS_PAID_OR_DELIVERED = "2"
    STATUS_CANCELLED = "6"
    STATUS_PURGED = "7"
    TRANSACTION_STATUS_CHOICES = [
        (STATUS_PAID_OR_DELIVERED, "Paid or delivered"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_PURGED, "Purged"),
    ]

    western_union_invoice = models.ForeignKey(
        "WesternUnionInvoice",
        on_delete=models.CASCADE,
    )
    payment = models.ForeignKey(
        "Payment",
        on_delete=models.CASCADE,
    )
    transaction_status = models.CharField(
        max_length=1,
        choices=TRANSACTION_STATUS_CHOICES,
    )

    class Meta:
        app_label = "payment"

    def __str__(self) -> str:
        return f"{self.payment.unicef_id} - {self.transaction_status}"
