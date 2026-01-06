from django.db import models

from hope.models.file_temp import FileTemp


class WesternUnionInvoice(models.Model):
    name = models.CharField(max_length=255, unique=True)
    file = models.ForeignKey(
        FileTemp,
        related_name="+",
        help_text="WU QCF File",
        on_delete=models.DO_NOTHING,
        null=True,
    )
    payments = models.ManyToManyField(
        "Payment",
        through="WesternUnionInvoicePayment",
        related_name="invoices",
    )

    class Meta:
        app_label = "payment"
        verbose_name = "Western Union Invoice"
        verbose_name_plural = "Western Union Invoices"

    def __str__(self) -> str:
        return self.name
