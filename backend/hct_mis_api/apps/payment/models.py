from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum, UUIDField
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from hct_mis_api.apps.utils.models import TimeStampedUUIDModel


class PaymentRecord(TimeStampedUUIDModel):
    STATUS_CHOICE = (
        ("SUCCESS", _("Sucess")),
        ("PENDING", _("Pending")),
        ("ERROR", _("Error")),
    )
    ENTITLEMENT_CARD_STATUS_CHOICE = Choices(
        ("ACTIVE", _("Active")), ("INACTIVE", _("Inactive")),
    )
    DELIVERY_TYPE_CHOICE = (
        ("CASH", _("Cash")),
        ("DEPOSIT_TO_CARD", _("Deposit to Card")),
        ("TRANSFER", _("Transfer")),
    )
    business_area = models.ForeignKey(
        "core.BusinessArea", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICE,)
    status_date = models.DateTimeField()
    cash_plan = models.ForeignKey(
        "program.CashPlan", on_delete=models.CASCADE, related_name="payment_records",
    )
    household = models.ForeignKey(
        "Household", on_delete=models.CASCADE, related_name="payment_records",
    )
    full_name = models.CharField(max_length=255)
    total_persons_covered = models.IntegerField()
    distribution_modality = models.CharField(max_length=255,)
    target_population = models.ForeignKey(
        "targeting.TargetPopulation",
        on_delete=models.CASCADE,
        related_name="payment_records",
    )
    target_population_cash_assist_id = models.CharField(max_length=255)
    entitlement_card_number = models.CharField(max_length=255,)
    entitlement_card_status = models.CharField(
        choices=STATUS_CHOICE, default="ACTIVE", max_length=20,
    )
    entitlement_card_issue_date = models.DateField()
    delivery_type = models.CharField(
        choices=DELIVERY_TYPE_CHOICE, default="ACTIVE", max_length=20,
    )
    currency = models.CharField(max_length=4,)
    entitlement_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    delivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    delivery_date = models.DateTimeField()
    service_provider = models.ForeignKey(
        "payment.ServiceProvider",
        on_delete=models.CASCADE,
        related_name="payment_records",
    )


class ServiceProvider(TimeStampedUUIDModel):
    business_area = models.ForeignKey(
        "core.BusinessArea", on_delete=models.CASCADE
    )
    cash_assist_id = models.CharField(max_length=255, primary_key=True)
    full_name = models.CharField(max_length=255, primary_key=True)
    short_name = models.CharField(max_length=4, primary_key=True)
    country = models.CharField(max_length=3, primary_key=True)
    vision_id = models.CharField(max_length=255, primary_key=True)
