from typing import Optional

from django.db import models
from django.db.models import Count, Q
from django.utils import timezone

from hope.models.utils import TimeStampedUUIDModel


def build_summary(payment_plan: Optional["PaymentPlan"]) -> None:
    if not payment_plan:
        return

    statuses_count = payment_plan.payment_verification_plans.aggregate(
        active=Count("pk", filter=Q(status=PaymentVerificationSummary.STATUS_ACTIVE)),
        pending=Count("pk", filter=Q(status=PaymentVerificationSummary.STATUS_PENDING)),
        finished=Count("pk", filter=Q(status=PaymentVerificationSummary.STATUS_FINISHED)),
    )
    summary = payment_plan.payment_verification_summary
    if statuses_count["active"] >= 1:
        summary.mark_as_active()
    elif statuses_count["finished"] >= 1 and statuses_count["active"] == 0 and statuses_count["pending"] == 0:
        summary.mark_as_finished()
    else:
        summary.status = PaymentVerificationSummary.STATUS_PENDING
        summary.completion_date = None
        summary.activation_date = None
        summary.mark_as_pending()
    summary.save()


class PaymentVerificationSummary(TimeStampedUUIDModel):
    STATUS_PENDING = "PENDING"
    STATUS_ACTIVE = "ACTIVE"
    STATUS_FINISHED = "FINISHED"
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_FINISHED, "Finished"),
        (STATUS_PENDING, "Pending"),
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="Verification status",
        db_index=True,
    )
    activation_date = models.DateTimeField(null=True)
    completion_date = models.DateTimeField(null=True)

    payment_plan = models.OneToOneField(
        "payment.PaymentPlan",
        on_delete=models.CASCADE,
        related_name="payment_verification_summary",
        null=True,
    )

    class Meta:
        app_label = "payment"

    def mark_as_active(self) -> None:
        self.status = self.STATUS_ACTIVE
        self.completion_date = None
        if self.activation_date is None:
            self.activation_date = timezone.now()

    def mark_as_finished(self) -> None:
        self.status = self.STATUS_FINISHED
        if self.completion_date is None:
            self.completion_date = timezone.now()

    def mark_as_pending(self) -> None:
        self.status = self.STATUS_PENDING
        self.completion_date = None
        self.activation_date = None
