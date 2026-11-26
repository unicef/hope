from django.db import models

from hope.models.file_temp import FileTemp
from hope.models.payment_list import PaymentList
from hope.models.western_union_invoice import WesternUnionInvoice


class WesternUnionPaymentListReport(models.Model):
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
    payment_list = models.ForeignKey(
        PaymentList,
        related_name="western_union_reports",
        on_delete=models.CASCADE,
        db_column="payment_plan_id",
    )
    sent = models.BooleanField(default=False)

    class Meta:
        app_label = "payment"
        db_table = "payment_westernunionpaymentplanreport"
        verbose_name = "Western Union Payment List Report"
        verbose_name_plural = "Western Union Payment List Reports"
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.invoice} - {self.payment_list}"
