from django.db import models

from hope.models.file_temp import FileTemp
from hope.models.utils import LongNameIndex


def get_status_choices() -> tuple:
    return WesternUnionInvoice.STATUS_CHOICES


class WesternUnionInvoice(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_ERROR = "ERROR"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_ERROR, "Error"),
    )

    name = models.CharField(max_length=255, unique=True)
    is_legacy = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)
    file = models.ForeignKey(
        FileTemp,
        related_name="+",
        help_text="Western Union invoice file",
        on_delete=models.DO_NOTHING,
        null=True,
    )
    advice_name = models.CharField(max_length=255, null=True, blank=True)
    matched_data = models.ForeignKey(
        "WesternUnionData",
        related_name="matched_invoices",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    net_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    charges = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=get_status_choices, default=STATUS_PENDING)
    error_msg = models.TextField(null=True, blank=True)
    payments = models.ManyToManyField(
        "Payment",
        through="WesternUnionInvoicePayment",
        related_name="invoices",
    )

    class Meta:
        app_label = "payment"
        verbose_name = "Western Union Invoice"
        verbose_name_plural = "Western Union Invoices"
        ordering = ("id",)
        indexes = [
            LongNameIndex(fields=["status"], name="payment_westernunioninvoice_status_f3104712"),
            LongNameIndex(
                fields=["status"],
                opclasses=["varchar_pattern_ops"],
                name="payment_westernunioninvoice_status_f3104712_like",
            ),
        ]

    def __str__(self) -> str:
        return self.name
