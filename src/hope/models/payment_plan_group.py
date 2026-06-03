from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Exists, OuterRef, Q
from django.utils.translation import gettext_lazy as _

from hope.models.utils import AdminUrlMixin, TimeStampedUUIDModel, UnicefIdentifiedModel

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from hope.models import PaymentPlan


class PaymentPlanGroup(TimeStampedUUIDModel, UnicefIdentifiedModel, AdminUrlMixin):
    class BackgroundExportActionStatus(models.TextChoices):
        XLSX_EXPORTING = "XLSX_EXPORTING", "Exporting XLSX file"
        XLSX_EXPORT_ERROR = "XLSX_EXPORT_ERROR", "Export XLSX file Error"

    class BackgroundImportActionStatus(models.TextChoices):
        XLSX_IMPORTING_RECONCILIATION = (
            "XLSX_IMPORTING_RECONCILIATION",
            "Importing Reconciliation XLSX file",
        )
        XLSX_IMPORT_ERROR = "XLSX_IMPORT_ERROR", "Import XLSX file Error"

    cycle = models.ForeignKey(
        "program.ProgramCycle",
        on_delete=models.CASCADE,
        related_name="payment_plan_groups",
        verbose_name=_("Programme Cycle"),
    )
    name = models.CharField(max_length=255, default="Default Group")
    delivery_import_file = models.ForeignKey(
        "core.FileTemp",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Uploaded reconciliation XLSX [sys]",
    )
    background_action_status_export = models.CharField(
        max_length=50,
        default=None,
        db_index=True,
        blank=True,
        null=True,
        choices=BackgroundExportActionStatus.choices,
        help_text="Background Action Status for celery export task [sys]",
    )
    background_action_status_import = models.CharField(
        max_length=50,
        default=None,
        db_index=True,
        blank=True,
        null=True,
        choices=BackgroundImportActionStatus.choices,
        help_text="Background Action Status for celery import task [sys]",
    )

    class Meta:
        app_label = "payment"
        verbose_name = "Payment Plan Group"
        unique_together = ("cycle", "name")
        ordering = ["created_at"]

    def delete(self, *args: object, **kwargs: object) -> tuple[int, dict]:
        if self.cycle.payment_plan_groups.count() == 1:
            raise ValidationError("Cannot delete the last group in a cycle.")
        return super().delete(*args, **kwargs)  # type: ignore

    def __str__(self) -> str:
        return f"{self.name} for {self.cycle}"

    def can_reexport_batch(self, export_tag: int) -> bool:
        return (
            self.background_action_status_export != PaymentPlanGroup.BackgroundExportActionStatus.XLSX_EXPORTING
            and self.payment_plans.filter(
                export_tag=export_tag,
                export_file_delivery__isnull=False,
            ).exists()
        )

    def get_batch_export_file_link(self, export_tag: int) -> str | None:
        """Return the download URL of the batch's XLSX, or None if the batch has no stored file.

        A batch is identified by export_tag; every plan in the batch references the same
        export_file_delivery, so any plan with that tag yields the file.
        """
        plan = self.payment_plans.filter(export_tag=export_tag, export_file_delivery__isnull=False).first()
        if plan is None or not plan.export_file_delivery.file:
            return None
        return plan.export_file_delivery.file.url

    def sendable_to_payment_gateway_plans(self) -> "QuerySet[PaymentPlan]":
        """Narrow the group's payment plans to the ones that can be sent to the payment gateway.

        A plan qualifies when it is ACCEPTED, has an FSP routed through the payment gateway
        (use_payment_gateway is True or the FSP communication_channel is API), still has splits
        not yet sent to the gateway, and is not already being sent.
        """
        from hope.models import FinancialServiceProvider, PaymentPlan, PaymentPlanSplit

        return self.payment_plans.annotate(
            has_unsent_splits=Exists(
                PaymentPlanSplit.objects.filter(payment_plan=OuterRef("pk"), sent_to_payment_gateway=False)
            )
        ).filter(
            Q(status=PaymentPlan.Status.ACCEPTED)
            & Q(financial_service_provider__isnull=False)
            & (
                Q(use_payment_gateway=True)
                | Q(
                    financial_service_provider__communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API
                )
            )
            & Q(has_unsent_splits=True)
            & ~Q(background_action_status=PaymentPlan.BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY)
        )
