from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from hct_mis_api.apps.utils.models import AbstractSession


class Session(AbstractSession):
    pass


class SessionModel(models.Model):
    session = models.ForeignKey("Session", on_delete=models.CASCADE)

    class Meta:
        abstract = True


class TargetPopulation(SessionModel):
    mis_id = models.UUIDField()
    ca_id = models.CharField(max_length=255,)
    ca_hash_id = models.UUIDField()

    class Meta:
        unique_together = ("session", "mis_id")


class Programme(SessionModel):
    mis_id = models.UUIDField()
    ca_id = models.CharField(max_length=255,)
    ca_hash_id = models.CharField(max_length=255,)

    class Meta:
        unique_together = ("session", "mis_id")


class CashPlan(SessionModel):
    DISTRIBUTION_COMPLETED = "Distribution Completed"
    DISTRIBUTION_COMPLETED_WITH_ERRORS = "Distribution Completed with Errors"
    TRANSACTION_COMPLETED = "Transaction Completed"
    TRANSACTION_COMPLETED_WITH_ERRORS = "Transaction Completed with Errors"
    STATUS_CHOICE = (
        (DISTRIBUTION_COMPLETED, _("Distribution Completed")),
        (DISTRIBUTION_COMPLETED_WITH_ERRORS, _("Distribution Completed with Errors"),),
        (TRANSACTION_COMPLETED, _("Transaction Completed")),
        (TRANSACTION_COMPLETED_WITH_ERRORS, _("Transaction Completed with Errors"),),
    )
    business_area = models.CharField(max_length=20, null=True)
    cash_plan_id = models.CharField(max_length=255)
    cash_plan_hash_id = models.UUIDField()
    status = models.CharField(max_length=255, null=True,)
    status_date = models.DateTimeField(null=True)
    name = models.CharField(max_length=255, null=True)
    distribution_level = models.CharField(max_length=255, null=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    dispersion_date = models.DateTimeField(null=True)
    coverage_duration = models.PositiveIntegerField(null=True)
    coverage_unit = models.CharField(max_length=255, null=True)
    comments = models.CharField(max_length=255, null=True)
    program_mis_id = models.UUIDField(null=True)
    delivery_type = models.CharField(max_length=255, null=True)
    assistance_measurement = models.CharField(max_length=255, null=True)
    assistance_through = models.CharField(max_length=255, null=True)
    vision_id = models.CharField(max_length=255, null=True)
    funds_commitment = models.CharField(max_length=255, null=True)
    down_payment = models.CharField(max_length=255, null=True)
    validation_alerts_count = models.IntegerField(null=True)
    total_persons_covered = models.IntegerField(null=True)
    total_persons_covered_revised = models.IntegerField(null=True)
    payment_records_count = models.IntegerField(null=True)
    total_entitled_quantity = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.01"))], null=True,
    )
    total_entitled_quantity_revised = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.01"))], null=True,
    )
    total_delivered_quantity = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.01"))], null=True,
    )
    total_undelivered_quantity = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.01"))], null=True,
    )

    class Meta:
        unique_together = ("session", "cash_plan_id")


class PaymentRecord(SessionModel):
    DELIVERY_TYPE_CARDLESS_CASH_WITHDRAWAL = "Cardless cash withdrawal"
    DELIVERY_TYPE_CASH = "Cash"
    DELIVERY_TYPE_CASH_BY_FSP = "Cash by FSP"
    DELIVERY_TYPE_CHEQUE = "Cheque"
    DELIVERY_TYPE_DEPOSIT_TO_CARD = "Deposit to Card"
    DELIVERY_TYPE_IN_KIND = "In Kind"
    DELIVERY_TYPE_MOBILE_MONEY = "Mobile Money"
    DELIVERY_TYPE_OTHER = "Other"
    DELIVERY_TYPE_PRE_PAID_CARD = "Pre-paid card"
    DELIVERY_TYPE_REFERRAL = "Referral"
    DELIVERY_TYPE_TRANSFER = "Transfer"
    DELIVERY_TYPE_TRANSFER_TO_ACCOUNT = "Transfer to Account"
    DELIVERY_TYPE_VOUCHER = "Voucher"

    DELIVERY_TYPE_CHOICE = (
        (DELIVERY_TYPE_CARDLESS_CASH_WITHDRAWAL, _("Cardless cash withdrawal")),
        (DELIVERY_TYPE_CASH, _("Cash")),
        (DELIVERY_TYPE_CASH_BY_FSP, _("Cash by FSP")),
        (DELIVERY_TYPE_CHEQUE, _("Cheque")),
        (DELIVERY_TYPE_DEPOSIT_TO_CARD, _("Deposit to Card")),
        (DELIVERY_TYPE_IN_KIND, _("In Kind")),
        (DELIVERY_TYPE_MOBILE_MONEY, _("Mobile Money")),
        (DELIVERY_TYPE_OTHER, _("Other")),
        (DELIVERY_TYPE_PRE_PAID_CARD, _("Pre-paid card")),
        (DELIVERY_TYPE_REFERRAL, _("Referral")),
        (DELIVERY_TYPE_TRANSFER, _("Transfer")),
        (DELIVERY_TYPE_TRANSFER_TO_ACCOUNT, _("Transfer to Account")),
        (DELIVERY_TYPE_VOUCHER, _("Voucher")),
    )
    business_area = models.CharField(max_length=20, null=True)
    status = models.CharField(max_length=255, null=True)
    status_date = models.DateTimeField(null=True)
    ca_id = models.CharField(max_length=255)
    ca_hash_id = models.UUIDField()
    registration_ca_id = models.CharField(max_length=255, null=True)
    household_mis_id = models.UUIDField(null=True)
    # head of household
    head_of_household_mis_id = models.UUIDField(null=True)
    full_name = models.CharField(max_length=255, null=True)
    total_persons_covered = models.IntegerField(null=True)
    distribution_modality = models.CharField(max_length=255, null=True)
    target_population_mis_id = models.UUIDField(null=True)
    target_population_cash_assist_id = models.CharField(max_length=255, null=True)
    cash_plan_ca_id = models.CharField(max_length=255, null=True)
    entitlement_card_number = models.CharField(max_length=255, null=True)
    entitlement_card_status = models.CharField(max_length=20, null=True)
    entitlement_card_issue_date = models.DateField(null=True)
    delivery_type = models.CharField(
        choices=DELIVERY_TYPE_CHOICE, default=DELIVERY_TYPE_CASH, max_length=20, null=True,
    )
    currency = models.CharField(max_length=4, null=True)
    entitlement_quantity = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.01"))], null=True,
    )
    delivered_quantity = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.01"))], null=True,
    )
    delivery_date = models.DateTimeField(null=True)
    service_provider_ca_id = models.CharField(max_length=255, null=True)
    transaction_reference_id = models.CharField(max_length=255, null=True)
    vision_id = models.CharField(max_length=255, null=True)

    class Meta:
        unique_together = ("session", "ca_id")


class ServiceProvider(SessionModel):
    business_area = models.CharField(max_length=20)
    ca_id = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=100)
    country = models.CharField(max_length=3,)
    vision_id = models.CharField(max_length=255)

    class Meta:
        unique_together = ("session", "ca_id")
