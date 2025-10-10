from django.db import models

from hope.models.file_temp import FileTemp
from hope.models.payment_plan import PaymentPlan
from hope.models.western_union_invoice import WesternUnionInvoice


class WesternUnionPaymentPlanReport(models.Model):
    qcf_file = models.ForeignKey(
        WesternUnionInvoice,
        related_name="reports",
        help_text="WU QCF File",
        on_delete=models.DO_NOTHING,
    )
    report_file = models.ForeignKey(
        FileTemp,
        related_name="+",
        help_text="WU QCF Report File",
        on_delete=models.DO_NOTHING,
        null=True,
    )
    payment_plan = models.ForeignKey(
        PaymentPlan,
        related_name="qcf_reports",
        on_delete=models.CASCADE,
    )
    sent = models.BooleanField(default=False)

    class Meta:
        app_label = "payment"
        verbose_name = "Western Union Payment Plan Report"
        verbose_name_plural = "Western Union Payment Plan Reports"

    def __str__(self) -> str:
        return f"{self.payment_plan.name} - sent: {self.sent}"
