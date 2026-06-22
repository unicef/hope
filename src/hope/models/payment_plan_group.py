from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Exists, OuterRef, Q
from django.utils.translation import gettext_lazy as _

from hope.models.utils import AdminUrlMixin, TimeStampedUUIDModel, UnicefIdentifiedModel

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from hope.models import PaymentPlan


class PaymentPlanGroup(TimeStampedUUIDModel, UnicefIdentifiedModel, AdminUrlMixin):
    class BackgroundActionStatus(models.TextChoices):
        XLSX_EXPORTING = "XLSX_EXPORTING", "Exporting XLSX file"
        XLSX_EXPORT_ERROR = "XLSX_EXPORT_ERROR", "Export XLSX file Error"
        XLSX_IMPORTING_RECONCILIATION = (
            "XLSX_IMPORTING_RECONCILIATION",
            "Importing Reconciliation XLSX file",
        )
        XLSX_IMPORT_ERROR = "XLSX_IMPORT_ERROR", "Import XLSX file Error"

    BACKGROUND_ACTION_ERROR_STATES = [
        BackgroundActionStatus.XLSX_EXPORT_ERROR,
        BackgroundActionStatus.XLSX_IMPORT_ERROR,
    ]

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
    background_action_status = models.CharField(
        max_length=50,
        default=None,
        db_index=True,
        blank=True,
        null=True,
        choices=BackgroundActionStatus.choices,
        help_text="Background Action Status for celery export/import task [sys]",
    )

    class Meta:
        app_label = "payment"
        verbose_name = "Payment Plan Group"
        unique_together = ("cycle", "name")
        ordering = ["created_at"]

    def delete(self, *args: object, **kwargs: object) -> tuple[int, dict]:
        with transaction.atomic():
            cycle_group_pks = list(
                PaymentPlanGroup.objects.filter(cycle_id=self.cycle_id).values_list("pk", flat=True).select_for_update()
            )
            if len(cycle_group_pks) <= 1:
                raise ValidationError("Cannot delete the last group in a cycle.")
            return super().delete(*args, **kwargs)  # type: ignore

    def __str__(self) -> str:
        return f"{self.name} for {self.cycle}"

    @property
    def can_start_background_action(self) -> bool:
        """Whether a new export/import can start: the group is idle or in an error state."""
        return (
            self.background_action_status is None
            or self.background_action_status in PaymentPlanGroup.BACKGROUND_ACTION_ERROR_STATES
        )

    def can_reexport_batch(self, export_tag: int) -> bool:
        return (
            self.can_start_background_action
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
