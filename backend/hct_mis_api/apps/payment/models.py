from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from hct_mis_api.apps.utils.models import TimeStampedUUIDModel
from model_utils import Choices


class PaymentRecord(TimeStampedUUIDModel):
    DELIVERY_TYPE_CHOICE = (
        ("DELIVERED", _("Delivered")),
        ("IN_PROGRESS", _("In Progress")),
    )
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    cash_assist_id = models.CharField(max_length=255)
    delivery_type = models.CharField(
        max_length=255, choices=DELIVERY_TYPE_CHOICE,
    )
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
    payment_record_verification = models.OneToOneField(
        "payment.PaymentRecordVerification", on_delete=models.CASCADE,
    )


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
    status = models.CharField(
        choices=STATUS_CHOICE, max_length=10,
    )


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
