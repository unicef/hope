from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.db import models
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce

from hope.models.file_temp import FileTemp
from hope.models.payment import Payment
from hope.models.utils import AdminUrlMixin, LongNameIndex, TimeStampedUUIDModel, UnicefIdentifiedModel

if TYPE_CHECKING:
    from hope.models import AcceptanceProcessThreshold


class FollowUpInstruction(TimeStampedUUIDModel, UnicefIdentifiedModel, AdminUrlMixin):
    class Status:
        OPEN = "OPEN"
        LOCKED = "LOCKED"
        LOCKED_FSP = "LOCKED_FSP"
        IN_APPROVAL = "IN_APPROVAL"
        IN_AUTHORIZATION = "IN_AUTHORIZATION"
        IN_REVIEW = "IN_REVIEW"
        ACCEPTED = "ACCEPTED"
        FINISHED = "FINISHED"
        CLOSED = "CLOSED"
        ABORTED = "ABORTED"

    class BackgroundActionStatus(models.TextChoices):
        XLSX_EXPORTING = "XLSX_EXPORTING", "Exporting XLSX"
        XLSX_IMPORTING_RECONCILIATION = "XLSX_IMPORTING_RECONCILIATION", "Importing Reconciliation from XLSX"
        XLSX_EXPORT_ERROR = "XLSX_EXPORT_ERROR", "Error while exporting XLSX"
        XLSX_IMPORT_ERROR = "XLSX_IMPORT_ERROR", "Error while importing XLSX"

    STATUS_PRECEDENCE = (
        Status.OPEN,
        Status.LOCKED,
        Status.LOCKED_FSP,
        Status.IN_APPROVAL,
        Status.IN_AUTHORIZATION,
        Status.IN_REVIEW,
        Status.ACCEPTED,
        Status.FINISHED,
        Status.CLOSED,
        Status.ABORTED,
    )
    SUMMARY_PDF_STATUSES = (Status.IN_REVIEW, Status.ACCEPTED, Status.FINISHED)
    BACKGROUND_ACTION_ERROR_STATES = (
        BackgroundActionStatus.XLSX_EXPORT_ERROR,
        BackgroundActionStatus.XLSX_IMPORT_ERROR,
    )

    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.PROTECT)
    program = models.ForeignKey("program.Program", on_delete=models.PROTECT, related_name="follow_up_instructions")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_follow_up_instructions",
    )
    financial_service_provider = models.ForeignKey(
        "payment.FinancialServiceProvider",
        on_delete=models.PROTECT,
        related_name="follow_up_instructions",
        null=True,
        blank=True,
    )
    currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.PROTECT,
        related_name="follow_up_instructions",
        null=True,
        blank=True,
    )
    dispersion_start_date = models.DateField(blank=True, null=True, help_text="Dispersion Start Date")
    dispersion_end_date = models.DateField(blank=True, null=True, help_text="Dispersion End Date")
    use_payment_gateway = models.BooleanField(
        default=False,
        help_text="Send the payment plans through the payment gateway regardless of the FSP communication channel",
    )
    background_action_status = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        choices=BackgroundActionStatus.choices,
    )
    export_file = models.ForeignKey(
        FileTemp,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
        help_text="Export File",
    )
    reconciliation_import_file = models.ForeignKey(
        FileTemp,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
        help_text="Reconciliation Import File",
    )
    export_pdf_file_summary = models.ForeignKey(
        FileTemp,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
        help_text="Generated summary PDF",
    )
    abort_comment = models.CharField(max_length=255, blank=True, default="")
    closure_comment = models.TextField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )

    class Meta:
        app_label = "payment"
        ordering = ["created_at"]
        verbose_name = "Follow Up Instruction"
        verbose_name_plural = "Follow Up Instructions"
        indexes = [
            LongNameIndex(fields=["created_at"], name="payment_followupinstruction_created_at_5807ab3f"),
            LongNameIndex(fields=["updated_at"], name="payment_followupinstruction_updated_at_197e3019"),
            LongNameIndex(fields=["unicef_id"], name="payment_followupinstruction_unicef_id_8793ca7b"),
            LongNameIndex(
                fields=["unicef_id"],
                opclasses=["varchar_pattern_ops"],
                name="payment_followupinstruction_unicef_id_8793ca7b_like",
            ),
        ]

    def __str__(self) -> str:
        return self.unicef_id or str(self.id)

    @property
    def status(self) -> str | None:
        # Proxy status: return the earliest workflow stage still present among child payment plans.
        statuses = list(self.payment_plans.values_list("status", flat=True))
        if not statuses:
            return None
        for candidate in self.STATUS_PRECEDENCE:
            if candidate in statuses:
                return candidate
        return statuses[0]

    @property
    def total_entitled_quantity_usd(self) -> Decimal:
        return self.payment_plans.aggregate(total=Coalesce(Sum("total_entitled_quantity_usd"), Decimal(0)))["total"]

    @cached_property
    def acceptance_process_threshold(self) -> "AcceptanceProcessThreshold | None":
        total_entitled_quantity_usd = int(self.total_entitled_quantity_usd)
        return self.business_area.acceptance_process_thresholds.filter(
            payments_range_usd__contains=NumericRange(
                total_entitled_quantity_usd, total_entitled_quantity_usd, bounds="[]"
            )
        ).first()

    @property
    def approval_number_required(self) -> int:
        return self.acceptance_process_threshold.approval_number_required if self.acceptance_process_threshold else 1

    @property
    def authorization_number_required(self) -> int:
        threshold = self.acceptance_process_threshold
        return threshold.authorization_number_required if threshold else 1

    @property
    def finance_release_number_required(self) -> int:
        threshold = self.acceptance_process_threshold
        return threshold.finance_release_number_required if threshold else 1

    @property
    def export_file_link(self) -> str | None:
        try:
            return self.export_file.file.url if self.export_file and self.export_file.file else None
        except FileTemp.DoesNotExist:
            return None

    @property
    def has_export_file(self) -> bool:
        return self.export_file_link is not None

    def remove_export_file(self) -> None:
        if self.export_file:
            self.export_file.file.delete(save=False)
            self.export_file.delete()
            self.export_file = None

    def payments_summary(self) -> dict[str, Any]:
        payments = Payment.objects.filter(parent__follow_up_instruction=self).eligible()
        summary = payments.aggregate(
            child_payment_plans_count=Count("parent_id", distinct=True),
            households_count=Count("household_id", distinct=True),
            total_entitled_quantity=Sum("entitlement_quantity"),
            total_entitled_quantity_usd=Sum("entitlement_quantity_usd"),
            total_delivered_quantity=Sum("delivered_quantity"),
            total_delivered_quantity_usd=Sum("delivered_quantity_usd"),
        )
        total_entitled_quantity = summary["total_entitled_quantity"] or Decimal(0)
        total_entitled_quantity_usd = summary["total_entitled_quantity_usd"] or Decimal(0)
        total_delivered_quantity = summary["total_delivered_quantity"] or Decimal(0)
        total_delivered_quantity_usd = summary["total_delivered_quantity_usd"] or Decimal(0)
        return {
            "child_payment_plans_count": summary["child_payment_plans_count"] or 0,
            "households_count": summary["households_count"] or 0,
            "total_entitled_quantity": total_entitled_quantity,
            "total_entitled_quantity_usd": total_entitled_quantity_usd,
            "total_delivered_quantity": total_delivered_quantity,
            "total_delivered_quantity_usd": total_delivered_quantity_usd,
            "total_undelivered_quantity": total_entitled_quantity - total_delivered_quantity,
            "total_undelivered_quantity_usd": total_entitled_quantity_usd - total_delivered_quantity_usd,
        }
