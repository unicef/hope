from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
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
    entitlement_card_issue_date = models.DateTimeField(blank=True, null=True)
    entitlement_card_number = models.CharField(
        max_length=255, choices=DELIVERY_TYPE_CHOICE,
    )
    currency = models.CharField(max_length=255)
    delivery_date = models.DateTimeField(blank=True, null=True)
    transaction_reference_id = models.CharField(max_length=255)
    fsp = models.CharField(max_length=255)
