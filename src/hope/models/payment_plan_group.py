from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.db.models import Exists, OuterRef, Q, Sum, TextField, Value
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _
from flags.state import flag_state

from hope.apps.activity_log.utils import create_mapping_dict
from hope.contrib.vision.choices import VisionStatus
from hope.models.utils import AdminUrlMixin, TimeStampedUUIDModel, UnicefIdentifiedModel

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from hope.models import AcceptanceProcessThreshold, BusinessArea, PaymentPlan, Program


class PaymentPlanGroup(TimeStampedUUIDModel, UnicefIdentifiedModel, AdminUrlMixin):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "name",
            "cycle",
            "status",
            "financial_service_provider",
            "background_action_status",
            "delivery_import_file",
            "abort_comment",
            "closure_comment",
            "closed_by",
        ],
        {"currency.code": "currency"},
    )

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        LOCKED = "LOCKED", "Locked"
        IN_APPROVAL = "IN_APPROVAL", "In Approval"
        IN_AUTHORIZATION = "IN_AUTHORIZATION", "In Authorization"
        IN_REVIEW = "IN_REVIEW", "In Review"
        ACCEPTED = "ACCEPTED", "Accepted"
        ABORTED = "ABORTED", "Aborted"
        FINISHED = "FINISHED", "Finished"
        READY_FOR_CLOSURE = "READY_FOR_CLOSURE", "Ready for Closure"
        CLOSED = "CLOSED", "Closed"

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
    status = models.CharField(
        max_length=50,
        default=Status.OPEN,
        db_index=True,
        choices=Status.choices,
    )
    status_date = models.DateTimeField(blank=True, null=True)
    financial_service_provider = models.ForeignKey(
        "payment.FinancialServiceProvider",
        on_delete=models.PROTECT,
        related_name="payment_plan_groups",
        null=True,
        blank=True,
    )
    currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.PROTECT,
        related_name="payment_plan_groups",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
    )
    abort_comment = models.CharField(max_length=255, blank=True)
    closure_comment = models.TextField(null=True, blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )
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
    def program(self) -> "Program":
        return self.cycle.program

    @property
    def business_area(self) -> "BusinessArea":
        return self.cycle.program.business_area

    @property
    def is_reconciled(self) -> bool:
        from hope.models import Payment, PaymentPlan

        eligible_payments = Payment.objects.filter(
            parent__payment_plan_group=self, parent__plan_type=PaymentPlan.PlanType.REGULAR
        ).eligible()
        return eligible_payments.exists() and not eligible_payments.filter(status__in=Payment.PENDING_STATUSES).exists()

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
        not yet sent to the gateway, and is not already being sent. When both Vision feature flags
        are active, plans already managed by Vision are also excluded.
        """
        from hope.models import FinancialServiceProvider, PaymentPlan, PaymentPlanSplit

        if self.financial_service_provider is None:
            return self.payment_plans.none()
        payment_plans = self.payment_plans.annotate(
            has_unsent_splits=Exists(
                PaymentPlanSplit.objects.filter(payment_plan=OuterRef("pk"), sent_to_payment_gateway=False)
            )
        ).filter(
            Q(status=PaymentPlan.Status.ACCEPTED)
            & Q(has_unsent_splits=True)
            & ~Q(background_action_status=PaymentPlan.BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY)
        )
        if self.financial_service_provider.communication_channel != FinancialServiceProvider.COMMUNICATION_CHANNEL_API:
            payment_plans = payment_plans.filter(use_payment_gateway=True)
        if flag_state("VISION_INTEGRATION_ACTIVE"):
            payment_plans = payment_plans.annotate(
                # PaymentPlan.vision_status treats missing Vision data as NOT_SENT. Apply the same fallback in SQL;
                # otherwise PostgreSQL evaluates the negated exclusion against NULL and drops legacy/manual plans.
                vision_workflow_status=Coalesce(
                    KeyTextTransform("status", KeyTextTransform("vision", "internal_data")),
                    Value(VisionStatus.NOT_SENT.value),
                    output_field=TextField(),
                )
            ).exclude(
                # Group PG sending rules for ACCEPTED plans:
                # - Released through Vision: exclude it because automatic PG sending was already attempted; failures
                #   are retried in Django admin.
                # - Accepted before Vision was enabled, or manually released while Vision was disabled: include it
                #   because its Vision state is missing or NOT_SENT and no automatic PG send was scheduled.
                # - Follow-Up plan: include it because the FC was reserved for the source plan and Follow-Ups do not
                #   use Vision, even if historical Vision data is present.
                Q(business_area__vision_integration_active=True)
                & ~Q(vision_workflow_status=VisionStatus.NOT_SENT.value)
                # Follow-Ups reuse funds reserved for their source plan and never use Vision. They stay on the normal
                # group PG path even if historical Vision data remains in internal_data.
                & ~Q(plan_type=PaymentPlan.PlanType.FOLLOW_UP)
            )
        return payment_plans
