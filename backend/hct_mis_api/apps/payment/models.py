from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from hct_mis_api.apps.utils.models import TimeStampedUUIDModel


class PaymentRecord(TimeStampedUUIDModel):
    STATUS_CHOICE = (
        ("SUCCESS", _("Sucess")),
        ("PENDING", _("Pending")),
        ("ERROR", _("Error")),
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICE,)
    name = models.CharField(max_length=255)
    status_date = models.DateTimeField()
    cash_assist_id = models.CharField(max_length=255)
    cash_plan = models.ForeignKey(
        "program.CashPlan",
        on_delete=models.CASCADE,
        related_name="payment_records",
    )

    household = models.ForeignKey(
        "household.Household",
        on_delete=models.CASCADE,
        related_name="payment_records",
    )
    head_of_household = models.CharField(max_length=255)
    total_person_covered = models.PositiveIntegerField()

    distribution_modality = models.CharField(max_length=255,)

    target_population = models.ForeignKey(
        "targeting.TargetPopulation",
        related_name="payment_records",
        on_delete=models.CASCADE,
    )
    entitlement = models.OneToOneField(
        "PaymentEntitlement",
        on_delete=models.SET_NULL,
        related_name="payment_record",
        null=True,
    )

    payment_record_verification = models.OneToOneField(
        "payment.PaymentRecordVerification",
        on_delete=models.SET_NULL,
        null=True,
    )


class PaymentEntitlement(TimeStampedUUIDModel):
    DELIVERY_TYPE_CHOICE = (
        ("CASH", _("Cash")),
        ("DEPOSIT_TO_CARD", _("Deposit to Card")),
        ("TRANSFER", _("Transfer")),
    )
    delivery_type = models.CharField(
        max_length=255, choices=DELIVERY_TYPE_CHOICE,
    )
    entitlement_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    delivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    entitlement_card_issue_date = models.DateField(blank=True, null=True)
    entitlement_card_number = models.CharField(
        max_length=255, choices=DELIVERY_TYPE_CHOICE,
    )
    currency = models.CharField(max_length=255)
    delivery_date = models.DateTimeField(blank=True, null=True)
    transaction_reference_id = models.CharField(max_length=255)
    fsp = models.CharField(max_length=255)


class VerificationProcess(TimeStampedUUIDModel):
    VERIFICATION_TYPE_CHOICE = Choices(
        ("RAPIDPRO", _("RapidPro")),
        ("MANUAL", _("Manual")),
        ("OTHER", _("Other")),
    )
    STATUS_CHOICE = Choices(
        ("PENDING", _("Pending")),
        ("ERROR", _("Error")),
        ("SUCCESS", _("Success")),
    )
    payment_records_to_verify = models.PositiveIntegerField()
    verification_type = models.CharField(
        choices=VERIFICATION_TYPE_CHOICE, max_length=10,
    )
    status = models.CharField(choices=STATUS_CHOICE, max_length=10,)


class PaymentRecordVerification(TimeStampedUUIDModel):
    STATUS_CHOICE = Choices(("STARTED", _("Started")), ("ENDED", _("Ended")),)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    sample_size = models.PositiveIntegerField()
    responded = models.PositiveIntegerField()
    received = models.PositiveIntegerField()
    not_received = models.PositiveIntegerField()
    received_correct_amount = models.PositiveIntegerField()
    received_wrong_amount = models.PositiveIntegerField()
    verification_process = models.ForeignKey(
        "payment.VerificationProcess",
        related_name="verification_processes",
        on_delete=models.CASCADE,
    )

    @property
    def total_number(self):
        return self.paymentrecord.aggregate(total_number=Sum("household"),)[
            "total_number"
        ]
