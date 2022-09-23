from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Count, JSONField, Q
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from model_utils import Choices

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.utils.models import (
    ConcurrencyModel,
    TimeStampedUUIDModel,
    UnicefIdentifiedModel,
)


class PaymentRecord(TimeStampedUUIDModel, ConcurrencyModel):
    STATUS_SUCCESS = "Transaction Successful"
    STATUS_ERROR = "Transaction Erroneous"
    STATUS_DISTRIBUTION_SUCCESS = "Distribution Successful"
    STATUS_NOT_DISTRIBUTED = "Not Distributed"
    STATUS_FORCE_FAILED = "Force failed"

    STATUS_CHOICE = (
        (STATUS_DISTRIBUTION_SUCCESS, _("Distribution Successful")),
        (STATUS_NOT_DISTRIBUTED, _("Not Distributed")),
        (STATUS_SUCCESS, _("Transaction Successful")),
        (STATUS_ERROR, _("Transaction Erroneous")),
        (STATUS_FORCE_FAILED, _("Force failed")),
    )

    ALLOW_CREATE_VERIFICATION = (STATUS_SUCCESS, STATUS_DISTRIBUTION_SUCCESS)

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
    ca_id = models.CharField(max_length=255, null=True, db_index=True)
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
    delivery_date = models.DateTimeField(null=True, blank=True)
    service_provider = models.ForeignKey(
        "payment.ServiceProvider",
        on_delete=models.CASCADE,
        related_name="payment_records",
    )
    transaction_reference_id = models.CharField(max_length=255, null=True)
    vision_id = models.CharField(max_length=255, null=True)
    registration_ca_id = models.CharField(max_length=255, null=True)

    def mark_as_failed(self):
        if self.status is self.STATUS_FORCE_FAILED:
            raise ValidationError("Status shouldn't be failed")
        self.status = self.STATUS_FORCE_FAILED
        self.status_date = timezone.now()


class ServiceProvider(TimeStampedUUIDModel):
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    ca_id = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, null=True)
    short_name = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=3)
    vision_id = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.full_name


class CashPlanPaymentVerification(TimeStampedUUIDModel, ConcurrencyModel, UnicefIdentifiedModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "status",
            "cash_plan",
            "sampling",
            "verification_channel",
            "sample_size",
            "responded_count",
            "received_count",
            "not_received_count",
            "received_with_problems_count",
            "confidence_interval",
            "margin_of_error",
            "rapid_pro_flow_id",
            "rapid_pro_flow_start_uuids",
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
    STATUS_INVALID = "INVALID"
    STATUS_RAPID_PRO_ERROR = "RAPID_PRO_ERROR"
    SAMPLING_FULL_LIST = "FULL_LIST"
    SAMPLING_RANDOM = "RANDOM"
    VERIFICATION_CHANNEL_RAPIDPRO = "RAPIDPRO"
    VERIFICATION_CHANNEL_XLSX = "XLSX"
    VERIFICATION_CHANNEL_MANUAL = "MANUAL"
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_FINISHED, "Finished"),
        (STATUS_PENDING, "Pending"),
        (STATUS_INVALID, "Invalid"),
        (STATUS_RAPID_PRO_ERROR, "RapidPro Error"),
    )
    SAMPLING_CHOICES = (
        (SAMPLING_FULL_LIST, "Full list"),
        (SAMPLING_RANDOM, "Random sampling"),
    )
    VERIFICATION_CHANNEL_CHOICES = (
        (VERIFICATION_CHANNEL_MANUAL, "MANUAL"),
        (VERIFICATION_CHANNEL_RAPIDPRO, "RAPIDPRO"),
        (VERIFICATION_CHANNEL_XLSX, "XLSX"),
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    cash_plan = models.ForeignKey(
        "program.CashPlan",
        on_delete=models.CASCADE,
        related_name="verifications",
    )
    sampling = models.CharField(max_length=50, choices=SAMPLING_CHOICES)
    verification_channel = models.CharField(max_length=50, choices=VERIFICATION_CHANNEL_CHOICES)
    sample_size = models.PositiveIntegerField(null=True)
    responded_count = models.PositiveIntegerField(null=True)
    received_count = models.PositiveIntegerField(null=True)
    not_received_count = models.PositiveIntegerField(null=True)
    received_with_problems_count = models.PositiveIntegerField(null=True)
    confidence_interval = models.FloatField(null=True)
    margin_of_error = models.FloatField(null=True)
    rapid_pro_flow_id = models.CharField(max_length=255, blank=True)
    rapid_pro_flow_start_uuids = ArrayField(models.CharField(max_length=255, blank=True), default=list)
    age_filter = JSONField(null=True)
    excluded_admin_areas_filter = JSONField(null=True)
    sex_filter = models.CharField(null=True, max_length=10)
    activation_date = models.DateTimeField(null=True)
    completion_date = models.DateTimeField(null=True)
    xlsx_file_exporting = models.BooleanField(default=False)
    xlsx_file_imported = models.BooleanField(default=False)
    error = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ("created_at",)

    @property
    def business_area(self):
        return self.cash_plan.business_area

    @property
    def has_xlsx_cash_plan_payment_verification_file(self):
        if all(
            [
                self.verification_channel == self.VERIFICATION_CHANNEL_XLSX,
                getattr(self, "xlsx_cashplan_payment_verification_file", None),
            ]
        ):
            return True
        return False

    @property
    def xlsx_cash_plan_payment_verification_file_link(self):
        if self.has_xlsx_cash_plan_payment_verification_file:
            return self.xlsx_cashplan_payment_verification_file.file.url
        return None

    @property
    def xlsx_cash_plan_payment_verification_file_was_downloaded(self):
        if self.has_xlsx_cash_plan_payment_verification_file:
            return self.xlsx_cashplan_payment_verification_file.was_downloaded
        return False

    def set_active(self):
        self.status = CashPlanPaymentVerification.STATUS_ACTIVE
        self.activation_date = timezone.now()
        self.error = None

    def set_pending(self):
        self.status = CashPlanPaymentVerification.STATUS_PENDING
        self.responded_count = None
        self.received_count = None
        self.not_received_count = None
        self.received_with_problems_count = None
        self.activation_date = None
        self.rapid_pro_flow_start_uuids = []

    def can_activate(self):
        return self.status not in (
            CashPlanPaymentVerification.STATUS_PENDING,
            CashPlanPaymentVerification.STATUS_RAPID_PRO_ERROR,
        )


class XlsxCashPlanPaymentVerificationFile(TimeStampedUUIDModel):
    file = models.FileField()
    cash_plan_payment_verification = models.OneToOneField(
        CashPlanPaymentVerification, related_name="xlsx_cashplan_payment_verification_file", on_delete=models.CASCADE
    )
    was_downloaded = models.BooleanField(default=False)
    created_by = models.ForeignKey(get_user_model(), null=True, related_name="+", on_delete=models.SET_NULL)


def build_summary(cash_plan):
    statuses_count = cash_plan.verifications.aggregate(
        active=Count("pk", filter=Q(status=CashPlanPaymentVerificationSummary.STATUS_ACTIVE)),
        pending=Count("pk", filter=Q(status=CashPlanPaymentVerificationSummary.STATUS_PENDING)),
        finished=Count("pk", filter=Q(status=CashPlanPaymentVerificationSummary.STATUS_FINISHED)),
    )
    summary = CashPlanPaymentVerificationSummary.objects.get(cash_plan=cash_plan)
    if statuses_count["active"] >= 1:
        summary.mark_as_active()
    elif statuses_count["finished"] >= 1 and statuses_count["active"] == 0 and statuses_count["pending"] == 0:
        summary.mark_as_finished()
    else:
        summary.mark_as_pending()
    summary.save()


@receiver(
    post_save,
    sender=CashPlanPaymentVerification,
    dispatch_uid="update_verification_status_in_cash_plan",
)
def update_verification_status_in_cash_plan(sender, instance, **kwargs):
    build_summary(instance.cash_plan)


@receiver(
    post_delete,
    sender=CashPlanPaymentVerification,
    dispatch_uid="update_verification_status_in_cash_plan_on_delete",
)
def update_verification_status_in_cash_plan_on_delete(sender, instance, **kwargs):
    build_summary(instance.cash_plan)


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
        (STATUS_NOT_RECEIVED, "NOT RECEIVED"),
        (STATUS_PENDING, "PENDING"),
        (STATUS_RECEIVED, "RECEIVED"),
        (STATUS_RECEIVED_WITH_ISSUES, "RECEIVED WITH ISSUES"),
    )
    cash_plan_payment_verification = models.ForeignKey(
        "CashPlanPaymentVerification",
        on_delete=models.CASCADE,
        related_name="payment_record_verifications",
    )
    payment_record = models.OneToOneField(
        "payment.PaymentRecord", related_name="verification", on_delete=models.CASCADE, null=True, blank=True
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

    @property
    def is_manually_editable(self):
        if (
            self.cash_plan_payment_verification.verification_channel
            != CashPlanPaymentVerification.VERIFICATION_CHANNEL_MANUAL
        ):
            return False
        minutes_elapsed = (timezone.now() - self.status_date).total_seconds() / 60
        return not (self.status != PaymentVerification.STATUS_PENDING and minutes_elapsed > 10)

    @property
    def business_area(self):
        return self.cash_plan_payment_verification.cash_plan.business_area

    def set_pending(self):
        self.status_date = timezone.now()
        self.status = PaymentVerification.STATUS_PENDING
        self.received_amount = None


class CashPlanPaymentVerificationSummary(TimeStampedUUIDModel):
    STATUS_PENDING = "PENDING"
    STATUS_ACTIVE = "ACTIVE"
    STATUS_FINISHED = "FINISHED"
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_FINISHED, "Finished"),
        (STATUS_PENDING, "Pending"),
    )
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name="Verification status", db_index=True
    )
    activation_date = models.DateTimeField(null=True)
    completion_date = models.DateTimeField(null=True)
    cash_plan = models.OneToOneField(
        "program.CashPlan", on_delete=models.CASCADE, related_name="cash_plan_payment_verification_summary"
    )

    def mark_as_active(self):
        self.status = self.STATUS_ACTIVE
        self.completion_date = None
        if self.activation_date is None:
            self.activation_date = timezone.now()

    def mark_as_finished(self):
        self.status = self.STATUS_FINISHED
        if self.completion_date is None:
            self.completion_date = timezone.now()

    def mark_as_pending(self):
        self.status = self.STATUS_PENDING
        self.completion_date = None
        self.activation_date = None
