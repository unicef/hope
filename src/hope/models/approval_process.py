from django.conf import settings
from django.db import models
from django.db.models import Q

from hope.models.utils import TimeStampedUUIDModel


class ApprovalProcess(TimeStampedUUIDModel):
    sent_for_approval_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True, blank=True
    )
    sent_for_approval_date = models.DateTimeField(null=True, blank=True)
    sent_for_authorization_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True, blank=True
    )
    sent_for_authorization_date = models.DateTimeField(null=True, blank=True)
    sent_for_finance_release_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True, blank=True
    )
    sent_for_finance_release_date = models.DateTimeField(null=True, blank=True)
    payment_plan = models.ForeignKey(
        "payment.PaymentPlan", on_delete=models.CASCADE, related_name="approval_process", null=True, blank=True
    )
    payment_plan_group = models.ForeignKey(
        "payment.PaymentPlanGroup", on_delete=models.CASCADE, related_name="approval_process", null=True, blank=True
    )

    approval_number_required = models.PositiveIntegerField(default=1)
    authorization_number_required = models.PositiveIntegerField(default=1)
    finance_release_number_required = models.PositiveIntegerField(default=1)

    class Meta:
        app_label = "payment"
        ordering = ("-created_at",)
        verbose_name_plural = "Approval Processes"
        constraints = [
            models.CheckConstraint(
                condition=Q(payment_plan__isnull=False, payment_plan_group__isnull=True)
                | Q(payment_plan__isnull=True, payment_plan_group__isnull=False),
                name="approval_process_owned_by_plan_or_group",
            )
        ]
