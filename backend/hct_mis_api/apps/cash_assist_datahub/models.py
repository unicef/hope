from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from utils.models import AbstractSession


class Session(AbstractSession):
    pass


class SessionModel(models.Model):
    session_id = models.ForeignKey("Session", on_delete=models.CASCADE)

    class Meta:
        abstract = True


class TargetPopulation(SessionModel):
    mis_id = models.UUIDField(unique=True)
    ca_id = models.CharField(max_length=255, primary_key=True,)
    ca_hash_id = models.UUIDField(unique=True)


class Programme(SessionModel):
    mis_id = models.UUIDField(unique=True,)
    ca_id = models.CharField(max_length=255, primary_key=True)
    ca_hash_id = models.CharField(max_length=255, unique=True)


class CashPlan(SessionModel):
    DISTRIBUTION_COMPLETED = (
        "Distribution Completed"  # or "DISTRIBUTION_COMPLETED"
    )
    DISTRIBUTION_COMPLETED_WITH_ERRORS = "Distribution Completed with Errors"
    TRANSACTION_COMPLETED = "Transaction Completed"
    TRANSACTION_COMPLETED_WITH_ERRORS = "Transaction Completed with Errors"
    business_area = models.CharField(max_length=20)
    cash_plan_id = models.CharField(max_length=255)
    cash_plan_hash_id = models.UUIDField(primary_key=True,)
    status = models.CharField(
        max_length=255,
        choices=(
            (DISTRIBUTION_COMPLETED, _("Distribution Completed")),
            (
                DISTRIBUTION_COMPLETED_WITH_ERRORS,
                _("Distribution Completed with Errors"),
            ),
            (TRANSACTION_COMPLETED, _("Transaction Completed")),
            (
                TRANSACTION_COMPLETED_WITH_ERRORS,
                _("Transaction Completed with Errors"),
            ),
        ),
    )
    status_date = models.DateTimeField()
    name = models.CharField(max_length=255)
    distribution_level = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    dispersion_date = models.DateTimeField()
    coverage_duration = models.PositiveIntegerField()
    coverage_unit = models.CharField(max_length=255)
    comments = models.CharField(max_length=255)
    program_mis_id = models.UUIDField()
    delivery_type = models.CharField(max_length=255)
    assistance_measurement = models.CharField(max_length=255)
    assistance_through = models.CharField(max_length=255)
    vision_id = models.CharField(max_length=255)
    funds_commitment = models.CharField(max_length=255)
    down_payment = models.CharField(max_length=255)
    validation_alerts_count = models.IntegerField()
    total_persons_covered = models.IntegerField()
    total_persons_covered_revised = models.IntegerField()
    payment_records_count = models.IntegerField()
    total_entitled_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    total_entitled_quantity_revised = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    total_delivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    total_undelivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )


class PaymentRecord(SessionModel):
    STATUS_SUCCESS = "SUCCESS"
    STATUS_PENDING = "PENDING"
    STATUS_ERROR = "ERROR"
    ENTITLEMENT_CARD_STATUS_ACTIVE = "ACTIVE"
    ENTITLEMENT_CARD_STATUS_INACTIVE = "INACTIVE"
    DELIVERY_TYPE_CASH = "CASH"
    DELIVERY_TYPE_DEPOSIT_TO_CARD = "DEPOSIT_TO_CARD"
    DELIVERY_TYPE_TRANSFER = "TRANSFER"
    STATUS_CHOICE = (
        (STATUS_SUCCESS, _("Sucess")),
        (STATUS_PENDING, _("Pending")),
        (STATUS_ERROR, _("Error")),
    )
    ENTITLEMENT_CARD_STATUS_CHOICE = Choices(
        (ENTITLEMENT_CARD_STATUS_ACTIVE, _("Active")),
        (ENTITLEMENT_CARD_STATUS_INACTIVE, _("Inactive")),
    )
    DELIVERY_TYPE_CHOICE = (
        (DELIVERY_TYPE_CASH, _("Cash")),
        (DELIVERY_TYPE_DEPOSIT_TO_CARD, _("Deposit to Card")),
        (DELIVERY_TYPE_TRANSFER, _("Transfer")),
    )
    business_area = models.CharField(max_length=20)
    status = models.CharField(max_length=255, choices=STATUS_CHOICE,)
    status_date = models.DateTimeField()
    ca_id = models.CharField(max_length=255)
    ca_hash_id = models.UUIDField(primary_key=True,)
    registration_ca_id = models.CharField(max_length=255)
    household_mis_id = models.UUIDField()
    # head of household
    focal_point_mis_id = models.UUIDField()
    full_name = models.CharField(max_length=255)
    total_persons_covered = models.IntegerField()
    distribution_modality = models.CharField(max_length=255,)
    target_population_mis_id = models.UUIDField()
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
        "ServiceProvider",
        on_delete=models.CASCADE,
        related_name="payment_records",
    )


class ServiceProvider(SessionModel):
    business_area = models.CharField(max_length=20)
    ca_id = models.CharField(max_length=255, primary_key=True)
    full_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=4)
    country = models.CharField(max_length=3,)
    vision_id = models.CharField(max_length=255)
