from decimal import Decimal

from auditlog.registry import auditlog
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from utils.models import TimeStampedUUIDModel


class PaymentRecord(TimeStampedUUIDModel):
    STATUS_SUCCESS = "SUCCESS"
    STATUS_PENDING = "PENDING"
    STATUS_ERROR = "ERROR"
    STATUS_CHOICE = (
        (STATUS_SUCCESS, _("Sucess")),
        (STATUS_PENDING, _("Pending")),
        (STATUS_ERROR, _("Error")),
    )
    ENTITLEMENT_CARD_STATUS_ACTIVE = "ACTIVE"
    ENTITLEMENT_CARD_STATUS_INACTIVE = "INACTIVE"
    ENTITLEMENT_CARD_STATUS_CHOICE = Choices((ENTITLEMENT_CARD_STATUS_ACTIVE, _("Active")),
                                             (ENTITLEMENT_CARD_STATUS_INACTIVE, _("Inactive")), )

    DELIVERY_TYPE_CASH = "CASH"
    DELIVERY_TYPE_DEPOSIT_TO_CARD = "DEPOSIT_TO_CARD"
    DELIVERY_TYPE_TRANSFER = "TRANSFER"

    DELIVERY_TYPE_CHOICE = (
        (DELIVERY_TYPE_CASH, _("Cash")),
        (DELIVERY_TYPE_DEPOSIT_TO_CARD, _("Deposit to Card")),
        (DELIVERY_TYPE_TRANSFER, _("Transfer")),
    )
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=STATUS_CHOICE, )
    status_date = models.DateTimeField()
    ca_id = models.CharField(max_length=255, null=True)
    ca_hash_id = models.UUIDField(unique=True, null=True)
    cash_plan = models.ForeignKey(
        "program.CashPlan", on_delete=models.CASCADE, related_name="payment_records", null=True,
    )
    household = models.ForeignKey("household.Household", on_delete=models.CASCADE, related_name="payment_records", )
    full_name = models.CharField(max_length=255)
    total_persons_covered = models.IntegerField()
    distribution_modality = models.CharField(max_length=255, )
    target_population = models.ForeignKey(
        "targeting.TargetPopulation", on_delete=models.CASCADE, related_name="payment_records",
    )
    target_population_cash_assist_id = models.CharField(max_length=255)
    entitlement_card_number = models.CharField(max_length=255, )
    entitlement_card_status = models.CharField(choices=ENTITLEMENT_CARD_STATUS_CHOICE, default="ACTIVE",
                                               max_length=20, )
    entitlement_card_issue_date = models.DateField()
    delivery_type = models.CharField(choices=DELIVERY_TYPE_CHOICE, default="ACTIVE", max_length=20, )
    currency = models.CharField(max_length=4, )
    entitlement_quantity = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.01"))],
    )
    delivered_quantity = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.01"))],
    )
    delivery_date = models.DateTimeField()
    service_provider = models.ForeignKey(
        "payment.ServiceProvider", on_delete=models.CASCADE, related_name="payment_records",
    )
    transaction_reference_id = models.CharField(max_length=255, null=True)
    vision_id = models.CharField(max_length=255, null=True)



class ServiceProvider(TimeStampedUUIDModel):
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    ca_id = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=100)
    country = models.CharField(max_length=3)
    vision_id = models.CharField(max_length=255)


class CashPlanPaymentVerification(TimeStampedUUIDModel):
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
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_PENDING)
    cash_plan = models.ForeignKey("program.CashPlan", on_delete=models.CASCADE, related_name="verifications", )
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


@receiver(
    post_save, sender=CashPlanPaymentVerification, dispatch_uid="update_verification_status_in_cash_plan",
)
def update_verification_status_in_cash_plan(sender, instance, **kwargs):
    instance.cash_plan.verification_status = instance.status
    instance.cash_plan.save()


class PaymentVerification(TimeStampedUUIDModel):
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
        "CashPlanPaymentVerification", on_delete=models.CASCADE, related_name="payment_record_verifications",
    )
    payment_record = models.ForeignKey("PaymentRecord", on_delete=models.CASCADE, related_name="verifications")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_PENDING)
    status_date = models.DateField(null=True)
    received_amount = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.01"))], null=True,
    )


auditlog.register(PaymentVerification)
auditlog.register(CashPlanPaymentVerification)
auditlog.register(PaymentRecord)
