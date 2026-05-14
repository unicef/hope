from django.db import models

from hope.models.file_temp import FileTemp


class WesternUnionInvoice(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_ERROR = "ERROR"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_ERROR, "Error"),
    ]

    name = models.CharField(max_length=255, unique=True)
    is_legacy = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)
    file = models.ForeignKey(
        FileTemp,
        related_name="+",
        help_text="WU AD File",
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
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

    def __str__(self) -> str:
        return self.name
