from decimal import Decimal
from functools import cached_property
from typing import Optional

from django.conf import settings
from django.contrib.postgres.fields import CICharField
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import JSONField, Q
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition

from model_utils import Choices
from model_utils.models import SoftDeletableModel
from multiselectfield import MultiSelectField

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.core.exchange_rates import ExchangeRates
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.utils.models import ConcurrencyModel, TimeStampedUUIDModel


class GenericPaymentPlan(TimeStampedUUIDModel):
    # TODO MB pull_from_datahub update
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    status_date = models.DateTimeField()
    name = models.CharField(max_length=255, db_index=True)
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(db_index=True)
    program = models.ForeignKey("program.Program", on_delete=models.CASCADE)
    exchange_rate = models.DecimalField(decimal_places=8, blank=True, null=True, max_digits=12)

    total_entitled_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
        db_index=True,
        null=True,
    )
    total_entitled_quantity_usd = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.01"))], null=True
    )
    total_entitled_quantity_revised = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
        db_index=True,
        null=True,
    )
    total_entitled_quantity_revised_usd = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.01"))], null=True
    )
    total_delivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
        db_index=True,
        null=True,
    )
    total_delivered_quantity_usd = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.01"))], null=True
    )
    total_undelivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
        db_index=True,
        null=True,
    )
    total_undelivered_quantity_usd = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.01"))], null=True
    )

    class Meta:
        abstract = True

    def update_exchange_rate(self, exchange_rates_client=None):
        if exchange_rates_client is None:
            exchange_rates_client = ExchangeRates()

        self.exchange_rate = exchange_rates_client.get_exchange_rate_for_currency_code(
            self.currency, self.currency_exchange_date
        )


class GenericPayment(TimeStampedUUIDModel):
    STATUS_SUCCESS = "Transaction Successful"
    STATUS_ERROR = "Transaction Erroneous"
    STATUS_DISTRIBUTION_SUCCESS = "Distribution Successful"
    STATUS_NOT_DISTRIBUTED = "Not Distributed"
    ALLOW_CREATE_VERIFICATION = (STATUS_SUCCESS, STATUS_DISTRIBUTION_SUCCESS)
    STATUS_CHOICE = (
        (STATUS_DISTRIBUTION_SUCCESS, _("Distribution Successful")),
        (STATUS_NOT_DISTRIBUTED, _("Not Distributed")),
        (STATUS_SUCCESS, _("Transaction Successful")),
        (STATUS_ERROR, _("Transaction Erroneous")),
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
    household = models.ForeignKey("household.Household", on_delete=models.CASCADE)
    head_of_household = models.ForeignKey("household.Individual", on_delete=models.CASCADE, null=True)  # collector
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
    entitlement_quantity_usd = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.01"))], null=True
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
    transaction_reference_id = models.CharField(max_length=255, null=True)  # transaction_id
    service_provider = models.ForeignKey(
        "payment.ServiceProvider",
        on_delete=models.CASCADE,
        related_name="payment_records",
    )  # financial_service_provider

    class Meta:
        abstract = True

    @property
    def _parent(self):
        raise NotImplemented()

    def get_quantity_in_usd(self, amount: Decimal, exchange_rates_client=None):
        # TODO MB double check exchange rate dates
        if not amount:
            return None

        exchange_rate = self._parent.exchange_rate

        if not exchange_rate:
            if exchange_rates_client is None:
                exchange_rates_client = ExchangeRates()

                exchange_rate = exchange_rates_client.get_exchange_rate_for_currency_code(
                    self.currency, self._parent.currency_exchange_date
                )

        if exchange_rate is None:
            return None

        return Decimal(amount / Decimal(exchange_rate)).quantize(Decimal(".01"))


class PaymentPlan(SoftDeletableModel, GenericPaymentPlan):
    # TODO MB
    # - ADMIN
    # - store *count fields on create, update on lock/unlock
    # - update on household/targeting update?

    class Status(models.TextChoices):
        OPEN = "OPEN"
        LOCKED = "LOCKED"
        IN_APPROVAL = "IN_APPROVAL"
        IN_AUTHORIZATION = "IN_AUTHORIZATION"
        IN_REVIEW = "IN_REVIEW"
        ACCEPTED = "ACCEPTED"

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_payment_plans",
    )
    status = FSMField(default=Status.OPEN, protected=False, db_index=True)
    unicef_id = CICharField(max_length=250, blank=True, db_index=True)
    target_population = models.ForeignKey(
        TargetPopulation,
        on_delete=models.CASCADE,
        related_name="payment_plans",
    )
    currency = models.CharField(
        max_length=4,
    )
    dispersion_start_date = models.DateTimeField()
    dispersion_end_date = models.DateTimeField()
    female_children_count = models.PositiveSmallIntegerField(default=0)
    male_children_count = models.PositiveSmallIntegerField(default=0)
    female_adults_count = models.PositiveSmallIntegerField(default=0)
    male_adult_count = models.PositiveSmallIntegerField(default=0)
    total_households_count = models.PositiveSmallIntegerField(default=0)
    total_individuals_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Payment Plan"
        ordering = ["created_at"]

    @transition(
        field=status,
        source=Status.OPEN,
        target=Status.LOCKED,
    )
    def status_lock(self):
        # TODO MB additional actions
        # - set/unset excluded on parent lock
        # udpte numbers
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=Status.LOCKED,
        target=Status.OPEN,
    )
    def status_unlock(self):
        # TODO MB additional actions
        # - set/unset excluded on parent lock
        # udpte numbers
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=Status.LOCKED,
        target=Status.IN_APPROVAL,
    )
    def status_send_to_approval(self):
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=[Status.IN_APPROVAL, Status.IN_AUTHORIZATION, Status.IN_REVIEW],
        target=Status.LOCKED,
    )
    def status_reject(self):
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=Status.IN_AUTHORIZATION,
        target=Status.IN_REVIEW,
    )
    def status_authorize(self):
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=Status.IN_REVIEW,
        target=Status.ACCEPTED,
    )
    def status_mark_as_reviewed(self):
        self.status_date = timezone.now()

    @property
    def currency_exchange_date(self):
        return self.dispersion_end_date


class CashPlan(GenericPaymentPlan):
    DISTRIBUTION_COMPLETED = "Distribution Completed"
    DISTRIBUTION_COMPLETED_WITH_ERRORS = "Distribution Completed with Errors"
    TRANSACTION_COMPLETED = "Transaction Completed"
    TRANSACTION_COMPLETED_WITH_ERRORS = "Transaction Completed with Errors"

    STATUS_CHOICE = (
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
    )
    ca_id = models.CharField(max_length=255, null=True, db_index=True)
    ca_hash_id = models.UUIDField(unique=True, null=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICE, db_index=True)
    distribution_level = models.CharField(max_length=255)
    dispersion_date = models.DateTimeField()
    coverage_duration = models.PositiveIntegerField()
    coverage_unit = models.CharField(max_length=255)
    comments = models.CharField(max_length=255, null=True)
    delivery_type = models.CharField(
        choices=GenericPayment.DELIVERY_TYPE_CHOICE,
        max_length=24,
        null=True,
        db_index=True,
    )
    assistance_measurement = models.CharField(max_length=255, db_index=True)
    assistance_through = models.CharField(max_length=255, db_index=True)
    service_provider = models.ForeignKey(
        "payment.ServiceProvider",
        null=True,
        related_name="cash_plans",
        on_delete=models.CASCADE,
    )
    vision_id = models.CharField(max_length=255, null=True)
    funds_commitment = models.CharField(max_length=255, null=True)
    down_payment = models.CharField(max_length=255, null=True)
    validation_alerts_count = models.IntegerField()
    total_persons_covered = models.IntegerField(db_index=True)
    total_persons_covered_revised = models.IntegerField(db_index=True)

    def __str__(self):
        return self.name

    @property
    def payment_records_count(self):
        return self.payment_records.count()

    @property
    def bank_reconciliation_success(self):
        return self.payment_records.filter(status__in=PaymentRecord.ALLOW_CREATE_VERIFICATION).count()

    @property
    def bank_reconciliation_error(self):
        return self.payment_records.filter(status=PaymentRecord.STATUS_ERROR).count()

    @cached_property
    def total_number_of_households(self):
        # https://unicef.visualstudio.com/ICTD-HCT-MIS/_workitems/edit/84040
        return self.payment_records.count()

    @property
    def currency(self):
        payment_record = self.payment_records.first()
        return payment_record.currency if payment_record else None

    @property
    def currency_exchange_date(self):
        return self.dispersion_date

    @property
    def can_create_payment_verification_plan(self):
        return self.available_payment_records().count() > 0

    def available_payment_records(self, payment_verification_plan: Optional["CashPlanPaymentVerification"] = None):
        from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import (
            does_payment_record_have_right_hoh_phone_number,
        )

        params = Q(status__in=PaymentRecord.ALLOW_CREATE_VERIFICATION, delivered_quantity__gt=0)

        if payment_verification_plan:
            params &= Q(
                Q(verification__isnull=True) | Q(verification__cash_plan_payment_verification=payment_verification_plan)
            )
        else:
            params &= Q(verification__isnull=True)

        payment_records = self.payment_records.filter(params).distinct()

        valid_payment_records_list = [
            payment_record.pk
            for payment_record in payment_records
            if does_payment_record_have_right_hoh_phone_number(payment_record)
        ]
        return PaymentRecord.objects.filter(pk__in=valid_payment_records_list)

    class Meta:
        verbose_name = "Cash Plan"
        ordering = ["created_at"]


class PaymentRecord(ConcurrencyModel, GenericPayment):
    ENTITLEMENT_CARD_STATUS_ACTIVE = "ACTIVE"
    ENTITLEMENT_CARD_STATUS_INACTIVE = "INACTIVE"
    ENTITLEMENT_CARD_STATUS_CHOICE = Choices(
        (ENTITLEMENT_CARD_STATUS_ACTIVE, _("Active")),
        (ENTITLEMENT_CARD_STATUS_INACTIVE, _("Inactive")),
    )

    ca_id = models.CharField(max_length=255, null=True, db_index=True)
    ca_hash_id = models.UUIDField(unique=True, null=True)
    cash_plan = models.ForeignKey(
        CashPlan,
        on_delete=models.CASCADE,
        related_name="payment_records",
        null=True,
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
    vision_id = models.CharField(max_length=255, null=True)
    registration_ca_id = models.CharField(max_length=255, null=True)

    @property
    def _parent(self):
        return self.cash_plan


class Payment(SoftDeletableModel, GenericPaymentPlan):
    # TODO MB
    # - ADMIN
    payment_plan = models.ForeignKey(
        PaymentPlan,
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
    )
    excluded = models.BooleanField(default=False)
    entitlement_date = models.DateTimeField(null=True, blank=True)

    @property
    def _parent(self):
        return self.payment_plan


class ServiceProvider(TimeStampedUUIDModel):
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    ca_id = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, null=True)
    short_name = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=3)
    vision_id = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.full_name


class CashPlanPaymentVerification(TimeStampedUUIDModel, ConcurrencyModel):
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
    VERIFICATION_CHANNEL_RAPIDPRO = "RAPIDPRO"
    VERIFICATION_CHANNEL_XLSX = "XLSX"
    VERIFICATION_CHANNEL_MANUAL = "MANUAL"
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_FINISHED, "Finished"),
        (STATUS_PENDING, "Pending"),
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
        CashPlan,
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
    rapid_pro_flow_start_uuid = models.CharField(max_length=255, blank=True)
    age_filter = JSONField(null=True)
    excluded_admin_areas_filter = JSONField(null=True)
    sex_filter = models.CharField(null=True, max_length=10)
    activation_date = models.DateTimeField(null=True)
    completion_date = models.DateTimeField(null=True)
    unicef_id = models.CharField(blank=True, max_length=250)

    class Meta:
        ordering = ("created_at",)

    @property
    def business_area(self):
        return self.cash_plan.business_area

    def set_active(self):
        self.status = CashPlanPaymentVerification.STATUS_ACTIVE
        self.activation_date = timezone.now()

    def set_pending(self):
        self.status = CashPlanPaymentVerification.STATUS_PENDING
        self.responded_count = None
        self.received_count = None
        self.not_received_count = None
        self.received_with_problems_count = None
        self.activation_date = None
        self.rapid_pro_flow_start_uuid = ""


def build_summary(cash_plan):
    active_count = cash_plan.verifications.filter(status=CashPlanPaymentVerificationSummary.STATUS_ACTIVE).count()
    pending_count = cash_plan.verifications.filter(status=CashPlanPaymentVerificationSummary.STATUS_PENDING).count()
    not_finished_count = cash_plan.verifications.exclude(
        status=CashPlanPaymentVerificationSummary.STATUS_FINISHED
    ).count()
    summary = CashPlanPaymentVerificationSummary.objects.get(cash_plan=cash_plan)
    if active_count >= 1:
        summary.status = CashPlanPaymentVerificationSummary.STATUS_ACTIVE
        summary.completion_date = None
        if summary.activation_date is None:
            summary.activation_date = timezone.now()
    elif not_finished_count == 0 and pending_count == 0:
        summary.status = CashPlanPaymentVerificationSummary.STATUS_FINISHED
        if summary.completion_date is None:
            summary.completion_date = timezone.now()
    else:
        summary.status = CashPlanPaymentVerificationSummary.STATUS_PENDING
        summary.completion_date = None
        summary.activation_date = None
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
        CashPlanPaymentVerification,
        on_delete=models.CASCADE,
        related_name="payment_record_verifications",
    )
    payment_record = models.OneToOneField(
        PaymentRecord, related_name="verification", on_delete=models.CASCADE, null=True, blank=True
    )
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
        CashPlan, on_delete=models.CASCADE, related_name="cash_plan_payment_verification_summary"
    )


class FinancialServiceProviderXlsxTemplate(TimeStampedUUIDModel):
    # TODO: add/remove fields after finalizing the fields
    COLUMNS_TO_CHOOSE = (
        ("payment_id", _("Payment ID")),
        ("household_id", _("Household ID")),
        ("admin_leve_2", _("Admin Level 2")),
        ("collector_name", _("Collector Name")),
        ("payment_channel", _("Payment Channel (Delivery mechanism)")),
        ("fsp_name", _("FSP Name")),
        ("entitlement_quantity", _("Entitlement Quantity")),
        ("tbd", _("TBD")),
    )
    DEFAULT_COLUMNS = [
        "payment_id",
        "household_id",
        "admin_leve_2",
        "collector_name",
        "payment_channel",
        "fsp_name",
        "entitlement_quantity",
    ]

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_financial_service_provider_xlsx_templates",
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    name = models.CharField(max_length=120, verbose_name=_("Name"))
    columns = MultiSelectField(
        choices=COLUMNS_TO_CHOOSE,
        default=DEFAULT_COLUMNS,
        verbose_name=_("Columns"),
        help_text=_("Select the columns to include in the report"),
    )

    def __str__(self):
        return f"{self.name} ({len(self.columns)})"


class FinancialServiceProvider(TimeStampedUUIDModel):
    COMMUNICATION_CHANNEL_API = "API"
    COMMUNICATION_CHANNEL_SFTP = "SFTP"
    COMMUNICATION_CHANNEL_XLSX = "XLSX"
    COMMUNICATION_CHANNEL_CHOICES = (
        (COMMUNICATION_CHANNEL_API, "API"),
        (COMMUNICATION_CHANNEL_SFTP, "SFTP"),
        (COMMUNICATION_CHANNEL_XLSX, "XLSX"),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_financial_service_providers",
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    name = models.CharField(max_length=100, unique=True)
    vision_vendor_number = models.CharField(max_length=100, unique=True)
    delivery_mechanisms = models.CharField(max_length=100)
    distribution_limit = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=True,
        help_text="The maximum amount of money that can be distributed or unlimited if 0",
        db_index=True,
    )
    communication_channel = models.CharField(max_length=6, choices=COMMUNICATION_CHANNEL_CHOICES, db_index=True)
    data_transfer_configuration = models.JSONField(
        help_text="JSON configuration for the data transfer mechanism",
        null=True,
        blank=True,
        default=dict,
    )
    fsp_xlsx_template = models.ForeignKey(
        FinancialServiceProviderXlsxTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("XLSX Template"),
    )

    def __str__(self):
        return f"{self.name} ({self.vision_vendor_number}): {self.communication_channel}"


class FinancialServiceProviderXlsxReport(TimeStampedUUIDModel):
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3
    STATUSES = (
        (IN_PROGRESS, _("Processing")),
        (COMPLETED, _("Generated")),
        (FAILED, _("Failed")),
    )
    financial_service_provider = models.ForeignKey(
        FinancialServiceProvider,
        on_delete=models.CASCADE,
        verbose_name=_("Financial Service Provider"),
    )
    file = models.FileField(blank=True, null=True, editable=False)
    status = models.IntegerField(choices=STATUSES, blank=True, null=True, editable=False, db_index=True)

    def __str__(self):
        return f"{self.template.name} ({self.status})"
