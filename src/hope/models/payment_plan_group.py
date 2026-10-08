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
from hope.models.payment_plan import PaymentPlan, last_approval_step
from hope.models.utils import AdminUrlMixin, TimeStampedUUIDModel, UnicefIdentifiedModel

if TYPE_CHECKING:
    from datetime import datetime

    from django.db.models import QuerySet

    from hope.models import AcceptanceProcessThreshold, BusinessArea, Program, User


class PaymentPlanGroup(TimeStampedUUIDModel, UnicefIdentifiedModel, AdminUrlMixin):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "name",
            "cycle",
            "status",
            "plan_type",
            "source_group",
            "financial_service_provider",
            "background_action_status",
            "export_file_delivery",
            "delivery_import_file",
            "export_pdf_file_summary",
            "abort_comment",
            "closure_comment",
            "closed_by",
        ],
        {"currency.code": "currency", "currency.vision_code": "currency_vision_code"},
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

    CHILD_GROUP_SOURCE_STATUSES = (Status.ACCEPTED, Status.FINISHED)
    # Statuses in which payments go out and come back: delivery export, send to Payment Gateway, reconciliation import.
    DELIVERY_STATUSES = (Status.ACCEPTED, Status.FINISHED)
    SUMMARY_PDF_STATUSES = (Status.IN_REVIEW, Status.ACCEPTED, Status.FINISHED)
    LINKED_GROUP_SOURCE_PLAN_TYPES = {
        PaymentPlan.PlanType.FOLLOW_UP: (
            PaymentPlan.PlanType.REGULAR,
            PaymentPlan.PlanType.TOP_UP,
            PaymentPlan.PlanType.TOP_UP_AMENDMENT,
        ),
        PaymentPlan.PlanType.TOP_UP: (PaymentPlan.PlanType.REGULAR,),
        PaymentPlan.PlanType.TOP_UP_AMENDMENT: (PaymentPlan.PlanType.TOP_UP,),
    }

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
    export_file_delivery = models.ForeignKey(
        "core.FileTemp",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Generated payment list XLSX for the FSP [sys]",
    )
    delivery_import_file = models.ForeignKey(
        "core.FileTemp",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Uploaded reconciliation XLSX [sys]",
    )
    export_pdf_file_summary = models.ForeignKey(
        "core.FileTemp",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Generated summary PDF [sys]",
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
    plan_type = models.CharField(
        max_length=20,
        choices=PaymentPlan.PlanType.choices,
        default=PaymentPlan.PlanType.REGULAR,
        db_index=True,
        help_text="Type of the Payment Plans the group runs; a Follow-Up / Top-Up / Amendment group is linked [sys]",
    )
    source_group = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="linked_groups",
        null=True,
        blank=True,
        help_text="The group this Follow-Up / Top-Up / Amendment group was created from [sys]",
    )

    class Meta:
        app_label = "payment"
        verbose_name = "Payment Plan Group"
        unique_together = ("cycle", "name")
        ordering = ["created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(plan_type=PaymentPlan.PlanType.REGULAR, source_group__isnull=True)
                | (~Q(plan_type=PaymentPlan.PlanType.REGULAR) & Q(source_group__isnull=False)),
                name="payment_plan_group_source_group_only_on_linked",
            ),
        ]

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

    def plans_qualifying_for_linked_group(self, plan_type: "PaymentPlan.PlanType") -> list[PaymentPlan]:
        """Plans of this group that a linked Follow-Up / Top-Up / Amendment group would get a child plan for."""
        if self.plan_type not in self.LINKED_GROUP_SOURCE_PLAN_TYPES[plan_type]:
            return []
        payment_plans = list(self.payment_plans.order_by("created_at"))
        if plan_type == PaymentPlan.PlanType.FOLLOW_UP:
            return [plan for plan in payment_plans if plan.unsuccessful_payments_for_follow_up().exists()]
        if self.status not in self.CHILD_GROUP_SOURCE_STATUSES:
            return []
        return [plan for plan in payment_plans if plan.eligible_payments_for_child_plan().exists()]

    @property
    def last_approval_process_date(self) -> "datetime | None":
        return last_approval_step(self.approval_process.first(), self.status, self.updated_at).modified_date

    @property
    def last_approval_process_by(self) -> "User | None":
        return last_approval_step(self.approval_process.first(), self.status, self.updated_at).modified_by

    @property
    def can_split(self) -> bool:
        from hope.models import PaymentPlanSplit

        return (
            self.status == PaymentPlanGroup.Status.ACCEPTED
            and not PaymentPlanSplit.objects.filter(
                payment_plan__payment_plan_group=self, sent_to_payment_gateway=True
            ).exists()
        )

    @property
    def is_reconciled(self) -> bool:
        from hope.models import Payment

        eligible_payments = Payment.objects.filter(parent__payment_plan_group=self).eligible()
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

    @property
    def export_file_link(self) -> str | None:
        if self.export_file_delivery_id and self.export_file_delivery.file:
            return self.export_file_delivery.file.url
        return None

    @property
    def can_export(self) -> bool:
        """Released and not exported yet; exporting again once a file exists is `can_regenerate_export`."""
        return self.status in self.DELIVERY_STATUSES and self.export_file_delivery_id is None

    @property
    def can_regenerate_export(self) -> bool:
        return self.status in self.DELIVERY_STATUSES and self.export_file_delivery_id is not None

    def remove_export_file_delivery(self) -> None:
        file_temp = self.export_file_delivery
        if file_temp is None:
            return
        self.export_file_delivery = None
        file_field = file_temp.file
        file_temp.delete()
        # Storage delete is not transactional: delete the file when the transaction commits
        transaction.on_commit(lambda: file_field.delete(save=False))

    def sendable_to_payment_gateway_plans(self) -> "QuerySet[PaymentPlan]":
        """Narrow the group's payment plans to the ones that can be sent to the payment gateway.

        A plan qualifies when it is ACCEPTED, has an FSP routed through the payment gateway
        (use_payment_gateway is True or the FSP communication_channel is API), still has splits
        not yet sent to the gateway, and is not already being sent. When both Vision feature flags
        are active, plans already managed by Vision are also excluded.
        """
        from hope.models import FinancialServiceProvider, PaymentPlanSplit

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
