from datetime import date
from decimal import Decimal
from typing import Any

from hope.apps.activity_log.utils import create_mapping_dict
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint, Sum
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError as DRFValidationError

from hope.models.program import Program
from hope.models.utils import AdminUrlMixin, TimeStampedUUIDModel, UnicefIdentifiedModel, ConcurrencyModel


class ProgramCycle(AdminUrlMixin, TimeStampedUUIDModel, UnicefIdentifiedModel, ConcurrencyModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "title",
            "status",
            "start_date",
            "end_date",
            "created_by",
        ],
    )
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"
    STATUS_CHOICE = (
        (DRAFT, _("Draft")),
        (ACTIVE, _("Active")),
        (FINISHED, _("Finished")),
    )
    title = models.CharField(
        _("Title"),
        max_length=255,
        null=True,
        blank=True,
        default="Default Programme Cycle",
    )
    program = models.ForeignKey("Program", on_delete=models.CASCADE, related_name="cycles")
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, db_index=True, default=DRAFT)
    start_date = models.DateField()  # first from program
    end_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Created by"),
        related_name="+",
    )

    class Meta:
        app_label = "program"
        constraints = [
            UniqueConstraint(
                fields=["title", "program"],
                name="program_cycle_title_unique_per_program",
            ),
        ]
        ordering = ["start_date"]
        verbose_name = "Programme Cycle"

    def clean(self) -> None:
        start_date = parse_date(self.start_date) if isinstance(self.start_date, str) else self.start_date
        end_date = parse_date(self.end_date) if isinstance(self.end_date, str) else self.end_date

        if end_date and end_date < start_date:
            raise ValidationError("End date cannot be before start date.")

        if self._state.adding and self.program.cycles.exclude(pk=self.pk).filter(end_date__gte=start_date).exists():
            raise ValidationError("Start date must be after the latest cycle.")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} ({self.status})"

    @property
    def can_remove_cycle(self) -> bool:
        return not self.payment_plans.exists() and self.program.cycles.count() > 1 and self.status == ProgramCycle.DRAFT

    @property
    def total_entitled_quantity_usd(self) -> Decimal:
        total_entitled_usd = self.payment_plans.aggregate(total_entitled_usd=Sum("total_entitled_quantity_usd"))[
            "total_entitled_usd"
        ]
        return total_entitled_usd or Decimal(0.0)

    @property
    def total_undelivered_quantity_usd(self) -> Decimal:
        total_undelivered_usd = self.payment_plans.aggregate(
            total_undelivered_usd=Sum("total_undelivered_quantity_usd")
        )["total_undelivered_usd"]
        return total_undelivered_usd or Decimal(0.0)

    @property
    def total_delivered_quantity_usd(self) -> Decimal:
        total_delivered_usd = self.payment_plans.aggregate(total_delivered_usd=Sum("total_delivered_quantity_usd"))[
            "total_delivered_usd"
        ]
        return total_delivered_usd or Decimal(0.0)

    @property
    def program_start_date(self) -> date:
        return self.program.start_date

    @property
    def program_end_date(self) -> date:
        return self.program.end_date

    @property
    def frequency_of_payments(self) -> str:
        return self.program.get_frequency_of_payments_display()

    def validate_program_active_status(self) -> None:
        # all changes with Program Cycle are possible within Active Program
        if self.program.status != Program.ACTIVE:
            raise DRFValidationError("Program should be within Active status.")

    def validate_payment_plan_status(self) -> None:
        """Validate status for Finishing Cycle."""
        from hope.models.payment_plan import PaymentPlan

        if (
            PaymentPlan.objects.filter(program_cycle=self)
            .exclude(
                status__in=PaymentPlan.PRE_PAYMENT_PLAN_STATUSES
                + (PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED),
            )
            .exists()
        ):
            raise DRFValidationError("All Payment Plans and Follow-Up Payment Plans have to be Reconciled.")

    def set_active(self) -> None:
        self.validate_program_active_status()
        if self.status in (ProgramCycle.DRAFT, ProgramCycle.FINISHED):
            self.status = ProgramCycle.ACTIVE
            self.save()

    def set_draft(self) -> None:
        self.validate_program_active_status()
        if self.status == ProgramCycle.ACTIVE:
            self.status = ProgramCycle.DRAFT
            self.save()

    def set_finish(self) -> None:
        self.validate_program_active_status()
        self.validate_payment_plan_status()
        if self.status == ProgramCycle.ACTIVE:
            self.status = ProgramCycle.FINISHED
            self.save()
