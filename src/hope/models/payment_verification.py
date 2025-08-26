from decimal import Decimal

from hope.apps.activity_log.utils import create_mapping_dict
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from hope.models.business_area import BusinessArea
from hope.models.utils import TimeStampedUUIDModel, ConcurrencyModel, AdminUrlMixin
from hope.models.payment_verification_plan import PaymentVerificationPlan


class PaymentVerification(TimeStampedUUIDModel, ConcurrencyModel, AdminUrlMixin):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "payment_verification_plan",
            "status",
            "status_date",
            "received_amount",
        ]
    )
    STATUS_PENDING = "PENDING"
    STATUS_RECEIVED = "RECEIVED"
    STATUS_NOT_RECEIVED = "NOT_RECEIVED"
    STATUS_RECEIVED_WITH_ISSUES = "RECEIVED_WITH_ISSUES"
    STATUS_CHOICES = (
        (STATUS_NOT_RECEIVED, "NOT RECEIVED"),
        (STATUS_PENDING, "PENDING"),
        (STATUS_RECEIVED, "RECEIVED"),
        (STATUS_RECEIVED_WITH_ISSUES, "RECEIVED WITH ISSUES"),
    )
    payment = models.ForeignKey(
        "payment.Payment",
        on_delete=models.CASCADE,
        related_name="payment_verifications",
    )
    payment_verification_plan = models.ForeignKey(
        "payment.PaymentVerificationPlan",
        on_delete=models.CASCADE,
        related_name="payment_record_verifications",
    )

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_PENDING)
    status_date = models.DateTimeField(null=True)
    received_amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=True,
    )
    sent_to_rapid_pro = models.BooleanField(default=False)

    class Meta:
        app_label = "payment"

    @property
    def is_manually_editable(self) -> bool:
        if self.payment_verification_plan.verification_channel != PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL:
            return False
        minutes_elapsed = (timezone.now() - self.status_date).total_seconds() / 60
        return not (self.status != PaymentVerification.STATUS_PENDING and minutes_elapsed > 10)

    @property
    def business_area(self) -> BusinessArea:
        return self.payment_verification_plan.payment_plan.business_area

    def set_pending(self) -> None:
        self.status_date = timezone.now()
        self.status = PaymentVerification.STATUS_PENDING
        self.received_amount = None
