import logging

from django.conf import settings
from django.contrib.postgres.fields import IntegerRangeField
from django.contrib.postgres.validators import RangeMinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from psycopg2._range import NumericRange

from hope.apps.utils.models import TimeStampedUUIDModel

logger = logging.getLogger(__name__)


class ApprovalProcess(TimeStampedUUIDModel):
    sent_for_approval_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True
    )
    sent_for_approval_date = models.DateTimeField(null=True)
    sent_for_authorization_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True
    )
    sent_for_authorization_date = models.DateTimeField(null=True)
    sent_for_finance_release_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True
    )
    sent_for_finance_release_date = models.DateTimeField(null=True)
    payment_plan = models.ForeignKey("payment.PaymentPlan", on_delete=models.CASCADE, related_name="approval_process")

    approval_number_required = models.PositiveIntegerField(default=1)
    authorization_number_required = models.PositiveIntegerField(default=1)
    finance_release_number_required = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "Approval Processes"


class Approval(TimeStampedUUIDModel):
    APPROVAL = "APPROVAL"
    AUTHORIZATION = "AUTHORIZATION"
    FINANCE_RELEASE = "FINANCE_RELEASE"
    REJECT = "REJECT"
    TYPE_CHOICES = (
        (APPROVAL, "Approval"),
        (AUTHORIZATION, "Authorization"),
        (FINANCE_RELEASE, "Finance Release"),
        (REJECT, "Reject"),
    )

    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default=APPROVAL, verbose_name=_("Approval type"))
    comment = models.CharField(max_length=500, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    approval_process = models.ForeignKey(ApprovalProcess, on_delete=models.CASCADE, related_name="approvals")

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.type or ""  # pragma: no cover

    @property
    def info(self) -> str:
        types_map = {
            self.APPROVAL: "Approved",
            self.AUTHORIZATION: "Authorized",
            self.FINANCE_RELEASE: "Released",
            self.REJECT: "Rejected",
        }

        return f"{types_map.get(self.type)} by {self.created_by}" if self.created_by else types_map.get(self.type, "")


class AcceptanceProcessThreshold(TimeStampedUUIDModel):
    business_area = models.ForeignKey(
        "core.BusinessArea", on_delete=models.PROTECT, related_name="acceptance_process_thresholds"
    )
    payments_range_usd = IntegerRangeField(
        default=NumericRange(0, None),
        validators=[
            RangeMinValueValidator(0),
        ],
    )
    approval_number_required = models.PositiveIntegerField(default=1)
    authorization_number_required = models.PositiveIntegerField(default=1)
    finance_release_number_required = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ("payments_range_usd",)

    def __str__(self) -> str:
        return (
            f"{self.payments_range_usd} USD, "
            f"Approvals: {self.approval_number_required} "
            f"Authorization: {self.authorization_number_required} "
            f"Finance Releases: {self.finance_release_number_required}"
        )
