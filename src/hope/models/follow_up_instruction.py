from decimal import Decimal
from typing import Any

from django.conf import settings
from django.db import models
from django.db.models import Count, Sum

from hope.models.file_temp import FileTemp
from hope.models.payment import Payment
from hope.models.utils import AdminUrlMixin, TimeStampedUUIDModel, UnicefIdentifiedModel


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

    class Meta:
        app_label = "payment"
        ordering = ["created_at"]
        verbose_name = "Follow Up Instruction"
        verbose_name_plural = "Follow Up Instructions"

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
