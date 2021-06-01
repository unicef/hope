from decimal import Decimal

from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel, ConcurrencyModel


class PaymentRecord(TimeStampedUUIDModel, ConcurrencyModel):
    STATUS_SUCCESS = "Transaction Successful"
    STATUS_ERROR = "Transaction Erroneous"
    STATUS_DISTRIBUTION_SUCCESS = "Distribution Successful"
    STATUS_NOT_DISTRIBUTED = "Not Distributed"
    ALLOW_CREATE_VERIFICATION = (STATUS_SUCCESS, STATUS_DISTRIBUTION_SUCCESS)
    STATUS_CHOICE = (
        (STATUS_SUCCESS, _("Transaction Successful")),
        (STATUS_ERROR, _("Transaction Erroneous")),
        (STATUS_DISTRIBUTION_SUCCESS, _("Distribution Successful")),
        (STATUS_NOT_DISTRIBUTED, _("Not Distributed")),
    )
    ENTITLEMENT_CARD_STATUS_ACTIVE = "ACTIVE"
    ENTITLEMENT_CARD_STATUS_INACTIVE = "INACTIVE"
    ENTITLEMENT_CARD_STATUS_CHOICE = Choices(
        (ENTITLEMENT_CARD_STATUS_ACTIVE, _("Active")),
        (ENTITLEMENT_CARD_STATUS_INACTIVE, _("Inactive")),
    )

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

    DELIVERY_TYPES_IN_CASH = (
        DELIVERY_TYPE_CARDLESS_CASH_WITHDRAWAL,
        DELIVERY_TYPE_CASH,
        DELIVERY_TYPE_CASH_BY_FSP,
        DELIVERY_TYPE_CHEQUE,
        DELIVERY_TYPE_DEPOSIT_TO_CARD,
        DELIVERY_TYPE_IN_KIND,
        DELIVERY_TYPE_MOBILE_MONEY,
        DELIVERY_TYPE_OTHER,
        DELIVERY_TYPE_PRE_PAID_CARD,
        DELIVERY_TYPE_REFERRAL,
        DELIVERY_TYPE_TRANSFER,
        DELIVERY_TYPE_TRANSFER_TO_ACCOUNT,
    )
    DELIVERY_TYPES_IN_VOUCHER = (DELIVERY_TYPE_VOUCHER,)

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
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICE,
    )
    status_date = models.DateTimeField()
    ca_id = models.CharField(max_length=255, null=True)
    ca_hash_id = models.UUIDField(unique=True, null=True)
    cash_plan = models.ForeignKey(
        "program.CashPlan",
        on_delete=models.CASCADE,
        related_name="payment_records",
        null=True,
    )
    household = models.ForeignKey(
        "household.Household",
        on_delete=models.CASCADE,
        related_name="payment_records",
    )
    head_of_household = models.ForeignKey(
        "household.Individual", on_delete=models.CASCADE, related_name="payment_records", null=True
    )

    full_name = models.CharField(max_length=255)
    total_persons_covered = models.IntegerField()
    distribution_modality = models.CharField(
        max_length=255,
    )
    target_population = models.ForeignKey(
        "targeting.TargetPopulation",
        on_delete=models.CASCADE,
        related_name="payment_records",
    )
    target_population_cash_assist_id = models.CharField(max_length=255)
    entitlement_card_number = models.CharField(max_length=255, null=True)
    entitlement_card_status = models.CharField(
        choices=ENTITLEMENT_CARD_STATUS_CHOICE, default="ACTIVE", max_length=20, null=True
    )
    entitlement_card_issue_date = models.DateField(null=True)
    delivery_type = models.CharField(
        choices=DELIVERY_TYPE_CHOICE,
        max_length=24,
    )
    currency = models.CharField(
        max_length=4,
    )
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
    delivered_quantity_usd = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.01"))], null=True
    )
    delivery_date = models.DateTimeField()
    service_provider = models.ForeignKey(
        "payment.ServiceProvider",
        on_delete=models.CASCADE,
        related_name="payment_records",
    )
    transaction_reference_id = models.CharField(max_length=255, null=True)
    vision_id = models.CharField(max_length=255, null=True)
    registration_ca_id = models.CharField(max_length=255, null=True)


class ServiceProvider(TimeStampedUUIDModel):
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    ca_id = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=100)
    country = models.CharField(max_length=3)
    vision_id = models.CharField(max_length=255)


class CashPlanPaymentVerification(TimeStampedUUIDModel, ConcurrencyModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "status",
            "cash_plan",
            "sampling",
            "verification_method",
            "sample_size",
            "responded_count",
            "received_count",
            "not_received_count",
            "received_with_problems_count",
            "confidence_interval",
            "margin_of_error",
            "rapid_pro_flow_id",
            "rapid_pro_flow_start_uuid",
            "age_filter",
            "excluded_admin_areas_filter",
            "sex_filter",
            "activation_date",
            "completion_date",
        ]
    )
    STATUS_PENDING = "PENDING"
    STATUS_ACTIVE = "ACTIVE"
    STATUS_FINISHED = "FINISHED"
    SAMPLING_FULL_LIST = "FULL_LIST"
    SAMPLING_RANDOM = "RANDOM"
    VERIFICATION_METHOD_RAPIDPRO = "RAPIDPRO"
    VERIFICATION_METHOD_XLSX = "XLSX"
    VERIFICATION_METHOD_MANUAL = "MANUAL"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_FINISHED, "Finished"),
    )
    SAMPLING_CHOICES = (
        (SAMPLING_FULL_LIST, "Full list"),
        (SAMPLING_RANDOM, "Random sampling"),
    )
    VERIFICATION_METHOD_CHOICES = (
        (VERIFICATION_METHOD_RAPIDPRO, "RAPIDPRO"),
        (VERIFICATION_METHOD_XLSX, "XLSX"),
        (VERIFICATION_METHOD_MANUAL, "MANUAL"),
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    cash_plan = models.ForeignKey(
        "program.CashPlan",
        on_delete=models.CASCADE,
        related_name="verifications",
    )
    sampling = models.CharField(max_length=50, choices=SAMPLING_CHOICES)
    verification_method = models.CharField(max_length=50, choices=VERIFICATION_METHOD_CHOICES)
    sample_size = models.PositiveIntegerField(null=True)
    responded_count = models.PositiveIntegerField(null=True)
    received_count = models.PositiveIntegerField(null=True)
    not_received_count = models.PositiveIntegerField(null=True)
    received_with_problems_count = models.PositiveIntegerField(null=True)
    confidence_interval = models.FloatField(null=True)
    margin_of_error = models.FloatField(null=True)
    rapid_pro_flow_id = models.CharField(max_length=255, blank=True)
    rapid_pro_flow_start_uuid = models.CharField(max_length=255, blank=True)
    age_filter = JSONField(null=True)
    excluded_admin_areas_filter = JSONField(null=True)
    sex_filter = models.CharField(null=True, max_length=10)
    activation_date = models.DateTimeField(null=True)
    completion_date = models.DateTimeField(null=True)

    @property
    def business_area(self):
        return self.cash_plan.business_area


@receiver(
    post_save,
    sender=CashPlanPaymentVerification,
    dispatch_uid="update_verification_status_in_cash_plan",
)
def update_verification_status_in_cash_plan(sender, instance, **kwargs):
    instance.cash_plan.verification_status = instance.status
    instance.cash_plan.save()


class PaymentVerification(TimeStampedUUIDModel, ConcurrencyModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "cash_plan_payment_verification",
            "payment_record",
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
        (STATUS_PENDING, "PENDING"),
        (STATUS_RECEIVED, "RECEIVED"),
        (STATUS_NOT_RECEIVED, "NOT RECEIVED"),
        (STATUS_RECEIVED_WITH_ISSUES, "RECEIVED WITH ISSUES"),
    )
    cash_plan_payment_verification = models.ForeignKey(
        "CashPlanPaymentVerification",
        on_delete=models.CASCADE,
        related_name="payment_record_verifications",
    )
    payment_record = models.ForeignKey("PaymentRecord", on_delete=models.CASCADE, related_name="verifications")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_PENDING)
    status_date = models.DateTimeField(null=True)
    received_amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=True,
    )

    @property
    def is_manually_editable(self):
        if (
            self.cash_plan_payment_verification.verification_method
            != CashPlanPaymentVerification.VERIFICATION_METHOD_MANUAL
        ):
            return False
        minutes_elapsed = (timezone.now() - self.status_date).total_seconds() / 60
        return not (self.status != PaymentVerification.STATUS_PENDING and minutes_elapsed > 10)

    @property
    def business_area(self):
        return self.cash_plan_payment_verification.cash_plan.business_area
