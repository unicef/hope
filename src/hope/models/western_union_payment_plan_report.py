from django.db import models

from hope.models.file_temp import FileTemp
from hope.models.payment_plan import PaymentPlan
from hope.models.western_union_invoice import WesternUnionInvoice


class WesternUnionPaymentPlanReport(models.Model):
    invoice = models.ForeignKey(
        WesternUnionInvoice,
        related_name="reports",
        help_text="Western Union invoice",
        on_delete=models.DO_NOTHING,
    )
    report_file = models.ForeignKey(
        FileTemp,
        related_name="+",
        help_text="Western Union report file",
        on_delete=models.DO_NOTHING,
        null=True,
    )
    payment_plan = models.ForeignKey(
        PaymentPlan,
        related_name="western_union_reports",
        on_delete=models.CASCADE,
    )
    sent = models.BooleanField(default=False)

    class Meta:
        app_label = "payment"
        verbose_name = "Western Union Payment Plan Report"
        verbose_name_plural = "Western Union Payment Plan Reports"
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.invoice} - {self.payment_plan}"
