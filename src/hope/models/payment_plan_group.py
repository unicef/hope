from datetime import date
from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING, cast

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.db.models import Exists, OuterRef, Q, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from flags.state import flag_state

from hope.apps.activity_log.utils import create_mapping_dict
from hope.contrib.vision.choices import VisionStatus
from hope.models.approval import Approval
from hope.models.payment_plan import PaymentPlan, last_approval_step
from hope.models.utils import (
    AdminUrlMixin,
    InternalDataFieldModel,
    LongNameIndex,
    TimeStampedUUIDModel,
    UnicefIdentifiedModel,
)

if TYPE_CHECKING:
    from datetime import datetime

    from django.db.models import QuerySet

    from hope.models import AcceptanceProcessThreshold, BusinessArea, Program, User


class PaymentPlanGroup(TimeStampedUUIDModel, UnicefIdentifiedModel, InternalDataFieldModel, AdminUrlMixin):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "name",
            "cycle",
            "status",
            "plan_type",
            "source_group",
            "financial_service_provider",
            "use_payment_gateway",
            "exchange_rate",
            "custom_exchange_rate",
            "custom_exchange_rate_set_by",
            "dispersion_start_date",
            "dispersion_end_date",
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
        RECALCULATING = "RECALCULATING", "Recalculating Payment Plan data"
        RECALCULATING_ERROR = "RECALCULATING_ERROR", "Payment Plan recalculation error"
        XLSX_EXPORTING = "XLSX_EXPORTING", "Exporting XLSX file"
        XLSX_EXPORT_ERROR = "XLSX_EXPORT_ERROR", "Export XLSX file Error"
        XLSX_IMPORTING_RECONCILIATION = (
            "XLSX_IMPORTING_RECONCILIATION",
            "Importing Reconciliation XLSX file",
        )
        XLSX_IMPORT_ERROR = "XLSX_IMPORT_ERROR", "Import XLSX file Error"

    BACKGROUND_ACTION_ERROR_STATES = [
        BackgroundActionStatus.RECALCULATING_ERROR,
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
    dispersion_start_date = models.DateField(blank=True, null=True, help_text="Dispersion Start Date")
    dispersion_end_date = models.DateField(blank=True, null=True, help_text="Dispersion End Date")
    use_payment_gateway = models.BooleanField(
        default=False,
        help_text="Send the payment plans through the payment gateway regardless of the FSP communication channel",
    )
    exchange_rate = models.DecimalField(
        decimal_places=8, blank=True, null=True, max_digits=15, help_text="Exchange Rate [sys]"
    )
    custom_exchange_rate = models.BooleanField(default=False, help_text="Custom Exchange Rate flag [sys]")
    custom_exchange_rate_set_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="User who set the custom exchange rate [sys]",
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
        blank=True,
        null=True,
        choices=BackgroundActionStatus.choices,
        help_text="Background Action Status for asynchronous group tasks [sys]",
    )
    plan_type = models.CharField(
        max_length=20,
        choices=PaymentPlan.PlanType.choices,
        default=PaymentPlan.PlanType.REGULAR,
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
        indexes = [
            LongNameIndex(fields=["created_at"], name="payment_paymentplangroup_created_at_14a802c0"),
            LongNameIndex(fields=["updated_at"], name="payment_paymentplangroup_updated_at_b23558fe"),
            LongNameIndex(fields=["unicef_id"], name="payment_paymentplangroup_unicef_id_3fb17c90"),
            LongNameIndex(
                fields=["unicef_id"],
                opclasses=["varchar_pattern_ops"],
                name="payment_paymentplangroup_unicef_id_3fb17c90_like",
            ),
            LongNameIndex(
                fields=["background_action_status"], name="payment_paymentplangroup_background_action_status_2aeaeb44"
            ),
            LongNameIndex(
                fields=["background_action_status"],
                opclasses=["varchar_pattern_ops"],
                name="payment_paymentplangroup_background_action_status_2aeaeb44_like",
            ),
            LongNameIndex(fields=["status"], name="payment_paymentplangroup_status_c68e4ae6"),
            LongNameIndex(
                fields=["status"],
                opclasses=["varchar_pattern_ops"],
                name="payment_paymentplangroup_status_c68e4ae6_like",
            ),
            LongNameIndex(fields=["plan_type"], name="payment_paymentplangroup_plan_type_1e21f341"),
            LongNameIndex(
                fields=["plan_type"],
                opclasses=["varchar_pattern_ops"],
                name="payment_paymentplangroup_plan_type_1e21f341_like",
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

    @property
    def vision_managed(self) -> bool:
        if (
            self.plan_type == PaymentPlan.PlanType.FOLLOW_UP
            or not flag_state("VISION_INTEGRATION_ACTIVE")
            or not self.business_area.vision_integration_active
        ):
            return False
        if self.status == self.Status.IN_REVIEW:
            return self.payment_plans.exists()
        return self.vision_status != VisionStatus.NOT_SENT.value

    @property
    def vision_data(self) -> dict:
        data = (self.internal_data or {}).get("vision", {})
        return data if isinstance(data, dict) else {}

    @property
    def vision_status(self) -> str:
        return str(self.vision_data.get("status") or VisionStatus.NOT_SENT.value)

    @property
    def sent_to_vision(self) -> bool:
        return bool(self.vision_data.get("sent"))

    @property
    def can_send_to_vision(self) -> bool:
        return (
            self.status == self.Status.IN_REVIEW
            and self.vision_managed
            and self.vision_status in {VisionStatus.NOT_SENT.value, VisionStatus.SEND_FAILED.value}
            and not self.sent_to_vision
        )

    @property
    def can_assign_funds_commitments(self) -> bool:
        if self.status != self.Status.IN_REVIEW or self.plan_type == PaymentPlan.PlanType.FOLLOW_UP:
            return False
        return not self.vision_managed and self.payment_plans.exists()

    @property
    def funds_commitment_source_group(self) -> "PaymentPlanGroup":
        if self.plan_type == PaymentPlan.PlanType.FOLLOW_UP:
            return cast("PaymentPlanGroup", self.source_group)
        return self

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
    def currency_exchange_date(self) -> date:
        if self.status in (
            self.Status.ACCEPTED,
            self.Status.FINISHED,
            self.Status.READY_FOR_CLOSURE,
            self.Status.CLOSED,
        ):
            process = self.approval_process.first()
            if process and (approval := process.approvals.filter(type=Approval.FINANCE_RELEASE).first()):
                return approval.created_at.date()
        today = timezone.now().date()
        return min(today, self.dispersion_end_date) if self.dispersion_end_date else today

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

    @property
    def total_entitled_quantity(self) -> Decimal:
        return self.payment_plans.aggregate(total=Coalesce(Sum("total_entitled_quantity"), Decimal(0)))["total"]

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
        """Whether a new background action can start: the group is idle or in an error state."""
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
        (the group's use_payment_gateway is True or the FSP communication_channel is API), still has splits
        not yet sent to the gateway, and is not already being sent. With Vision active, plans
        in a group with Vision status other than NOT_SENT are excluded, except Follow-Up plans.
        """
        from hope.models import FinancialServiceProvider, PaymentPlanSplit

        if self.financial_service_provider is None or not (
            self.use_payment_gateway
            or self.financial_service_provider.communication_channel
            == FinancialServiceProvider.COMMUNICATION_CHANNEL_API
        ):
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
        # A group accepted while Vision was disabled still has NOT_SENT status and needs manual PG sending.
        # Groups sent to Vision use automatic PG dispatch; Follow-Up plans remain eligible here, and failed
        # automatic sends are retried in Django admin.
        if (
            self.vision_status != VisionStatus.NOT_SENT.value
            and flag_state("VISION_INTEGRATION_ACTIVE")
            and self.business_area.vision_integration_active
        ):
            return payment_plans.filter(plan_type=PaymentPlan.PlanType.FOLLOW_UP)
        return payment_plans
