import logging
from datetime import datetime
from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING, Any, Callable, Optional

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from model_utils import Choices

from hct_mis_api.apps.core.currencies import USDC
from hct_mis_api.apps.core.exchange_rates import ExchangeRates
from hct_mis_api.apps.payment.delivery_mechanisms import DeliveryMechanismChoices
from hct_mis_api.apps.utils.models import (
    AdminUrlMixin,
    ConcurrencyModel,
    TimeStampedUUIDModel,
)

if TYPE_CHECKING:
    from hct_mis_api.apps.core.exchange_rates.api import ExchangeRateClient


logger = logging.getLogger(__name__)


class GenericPaymentPlan(TimeStampedUUIDModel):
    usd_fields = [
        "total_entitled_quantity_usd",
        "total_entitled_quantity_revised_usd",
        "total_delivered_quantity_usd",
        "total_undelivered_quantity_usd",
    ]

    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    status_date = models.DateTimeField()
    start_date = models.DateTimeField(
        db_index=True,
        blank=True,
        null=True,
    )
    end_date = models.DateTimeField(
        db_index=True,
        blank=True,
        null=True,
    )
    program = models.ForeignKey("program.Program", on_delete=models.CASCADE)
    exchange_rate = models.DecimalField(decimal_places=8, blank=True, null=True, max_digits=14)

    total_entitled_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0"))],
        db_index=True,
        null=True,
    )
    total_entitled_quantity_usd = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0"))], null=True, blank=True
    )
    total_entitled_quantity_revised = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0"))],
        db_index=True,
        null=True,
        blank=True,
    )
    total_entitled_quantity_revised_usd = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0"))], null=True, blank=True
    )
    total_delivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0"))],
        db_index=True,
        null=True,
        blank=True,
    )
    total_delivered_quantity_usd = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0"))], null=True, blank=True
    )
    total_undelivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0"))],
        db_index=True,
        null=True,
        blank=True,
    )
    total_undelivered_quantity_usd = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0"))], null=True, blank=True
    )

    class Meta:
        abstract = True

    @property
    def get_unicef_id(self) -> str:
        return self.ca_id if isinstance(self, CashPlan) else self.unicef_id

    def get_exchange_rate(self, exchange_rates_client: Optional["ExchangeRateClient"] = None) -> float:
        if self.currency == USDC:
            # exchange rate for Digital currency
            return 1.0

        if exchange_rates_client is None:
            exchange_rates_client = ExchangeRates()

        return exchange_rates_client.get_exchange_rate_for_currency_code(self.currency, self.currency_exchange_date)

    @property
    def get_payment_verification_summary(self) -> Any:
        """PaymentPlan has only one payment_verification_summary"""
        from hct_mis_api.apps.payment.models import PaymentVerificationSummary

        c_type = ContentType.objects.get_for_model(self.__class__)
        try:
            verification_summary = PaymentVerificationSummary.objects.get(
                payment_plan_content_type_id=c_type.pk, payment_plan_object_id=self.pk
            )
        except PaymentVerificationSummary.DoesNotExist:
            return None
        return verification_summary

    @property
    def get_payment_verification_plans(self) -> Any:
        from hct_mis_api.apps.payment.models import PaymentVerificationPlan

        c_type = ContentType.objects.get_for_model(self.__class__)
        payment_verification_plans = PaymentVerificationPlan.objects.filter(
            payment_plan_content_type_id=c_type.pk, payment_plan_object_id=self.pk
        )
        return payment_verification_plans

    def available_payment_records(
        self,
        payment_verification_plan: Any = None,
        extra_validation: Optional[Callable] = None,
    ) -> QuerySet:
        params = Q(status__in=GenericPayment.ALLOW_CREATE_VERIFICATION, delivered_quantity__gt=0)

        if payment_verification_plan:
            params &= Q(
                Q(payment_verification__isnull=True)
                | Q(payment_verification__payment_verification_plan=payment_verification_plan)
            )
        else:
            params &= Q(payment_verification__isnull=True)

        payment_records = self.payment_items.select_related("head_of_household").filter(params).distinct()

        if extra_validation:
            payment_records = list(map(lambda pr: pr.pk, filter(extra_validation, payment_records)))

        qs = PaymentRecord.objects.filter(pk__in=payment_records)

        return qs

    @property
    def can_create_payment_verification_plan(self) -> int:
        return self.available_payment_records().count() > 0


class GenericPayment(TimeStampedUUIDModel):
    usd_fields = ["delivered_quantity_usd", "entitlement_quantity_usd"]

    STATUS_SUCCESS = "Transaction Successful"
    STATUS_ERROR = "Transaction Erroneous"
    STATUS_DISTRIBUTION_SUCCESS = "Distribution Successful"
    STATUS_NOT_DISTRIBUTED = "Not Distributed"
    STATUS_FORCE_FAILED = "Force failed"
    STATUS_DISTRIBUTION_PARTIAL = "Partially Distributed"
    STATUS_PENDING = "Pending"
    # Payment Gateway statuses
    STATUS_SENT_TO_PG = "Sent to Payment Gateway"
    STATUS_SENT_TO_FSP = "Sent to FSP"
    STATUS_MANUALLY_CANCELLED = "Manually Cancelled"

    STATUS_CHOICE = (
        (STATUS_DISTRIBUTION_SUCCESS, _("Distribution Successful")),  # Delivered Fully
        (STATUS_NOT_DISTRIBUTED, _("Not Distributed")),  # Not Delivered
        (STATUS_SUCCESS, _("Transaction Successful")),  # Delivered Fully
        (STATUS_ERROR, _("Transaction Erroneous")),  # Unsuccessful
        (STATUS_FORCE_FAILED, _("Force failed")),  # Force Failed
        (STATUS_DISTRIBUTION_PARTIAL, _("Partially Distributed")),  # Delivered Partially
        (STATUS_PENDING, _("Pending")),  # Pending
        (STATUS_SENT_TO_PG, _("Sent to Payment Gateway")),
        (STATUS_SENT_TO_FSP, _("Sent to FSP")),
        (STATUS_MANUALLY_CANCELLED, _("Manually Cancelled")),
    )

    ALLOW_CREATE_VERIFICATION = (STATUS_SUCCESS, STATUS_DISTRIBUTION_SUCCESS, STATUS_DISTRIBUTION_PARTIAL)
    PENDING_STATUSES = (STATUS_PENDING, STATUS_SENT_TO_PG, STATUS_SENT_TO_FSP)

    ENTITLEMENT_CARD_STATUS_ACTIVE = "ACTIVE"
    ENTITLEMENT_CARD_STATUS_INACTIVE = "INACTIVE"
    ENTITLEMENT_CARD_STATUS_CHOICE = Choices(
        (ENTITLEMENT_CARD_STATUS_ACTIVE, _("Active")),
        (ENTITLEMENT_CARD_STATUS_INACTIVE, _("Inactive")),
    )

    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICE,
        default=STATUS_PENDING,
    )
    status_date = models.DateTimeField()
    household = models.ForeignKey("household.Household", on_delete=models.CASCADE)
    head_of_household = models.ForeignKey("household.Individual", on_delete=models.CASCADE, null=True)
    delivery_type = models.ForeignKey("payment.DeliveryMechanism", on_delete=models.SET_NULL, null=True)
    currency = models.CharField(
        max_length=4,
    )
    entitlement_quantity = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.00"))], null=True, blank=True
    )
    entitlement_quantity_usd = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.00"))], null=True, blank=True
    )
    delivered_quantity = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.00"))], null=True, blank=True
    )
    delivered_quantity_usd = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.00"))], null=True, blank=True
    )
    delivery_date = models.DateTimeField(null=True, blank=True)
    transaction_reference_id = models.CharField(max_length=255, null=True, blank=True)  # transaction_id
    transaction_status_blockchain_link = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def verification(self) -> Any:
        from hct_mis_api.apps.payment.models import PaymentVerification

        c_type = ContentType.objects.get_for_model(self.__class__)
        try:
            verification = PaymentVerification.objects.get(payment_content_type_id=c_type.pk, payment_object_id=self.pk)
        except PaymentVerification.DoesNotExist:
            return None
        return verification

    def get_revert_mark_as_failed_status(self, delivered_quantity: Decimal) -> str:
        raise NotImplementedError()

    def mark_as_failed(self) -> None:
        if self.status is self.STATUS_FORCE_FAILED:
            raise ValidationError("Status shouldn't be failed")
        self.status = self.STATUS_FORCE_FAILED
        self.status_date = timezone.now()
        self.delivered_quantity = 0
        self.delivered_quantity_usd = 0
        self.delivery_date = None

    def revert_mark_as_failed(self, delivered_quantity: Decimal, delivery_date: datetime) -> None:
        if self.status != self.STATUS_FORCE_FAILED:
            raise ValidationError("Only payment marked as force failed can be reverted")
        if self.entitlement_quantity is None:
            raise ValidationError("Entitlement quantity need to be set in order to revert")

        self.status = self.get_revert_mark_as_failed_status(delivered_quantity)
        self.status_date = timezone.now()
        self.delivered_quantity = delivered_quantity
        self.delivery_date = delivery_date

    @property
    def get_unicef_id(self) -> str:
        return self.ca_id if isinstance(self, PaymentRecord) else self.unicef_id

    @property
    def payment_status(self) -> str:
        status = "-"
        if self.status == GenericPayment.STATUS_PENDING:
            status = "Pending"

        elif self.status in (GenericPayment.STATUS_DISTRIBUTION_SUCCESS, GenericPayment.STATUS_SUCCESS):
            status = "Delivered Fully"

        elif self.status == GenericPayment.STATUS_DISTRIBUTION_PARTIAL:
            status = "Delivered Partially"

        elif self.status == GenericPayment.STATUS_NOT_DISTRIBUTED:
            status = "Not Delivered"

        elif self.status == GenericPayment.STATUS_ERROR:
            status = "Unsuccessful"

        elif self.status == GenericPayment.STATUS_FORCE_FAILED:
            status = "Force Failed"

        return status


class CashPlan(ConcurrencyModel, AdminUrlMixin, GenericPaymentPlan):
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
    name = models.CharField(max_length=255, db_index=True)
    ca_id = models.CharField(max_length=255, null=True, db_index=True)
    ca_hash_id = models.UUIDField(unique=True, null=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICE, db_index=True)
    distribution_level = models.CharField(max_length=255)
    dispersion_date = models.DateTimeField()
    coverage_duration = models.PositiveIntegerField()
    coverage_unit = models.CharField(max_length=255)
    comments = models.CharField(max_length=255, null=True)
    delivery_type = models.CharField(
        choices=DeliveryMechanismChoices.DELIVERY_TYPE_CHOICES,
        max_length=32,
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
    payment_verification_summary = GenericRelation(
        "payment.PaymentVerificationSummary",
        content_type_field="payment_plan_content_type",
        object_id_field="payment_plan_object_id",
        related_query_name="cash_plan",
    )
    payment_verification_plan = GenericRelation(
        "payment.PaymentVerificationPlan",
        content_type_field="payment_plan_content_type",
        object_id_field="payment_plan_object_id",
        related_query_name="cash_plan",
    )
    is_migrated_to_payment_plan = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name or ""

    @property
    def payment_records_count(self) -> int:
        return self.payment_items.count()

    @property
    def bank_reconciliation_success(self) -> int:
        return self.payment_items.filter(status__in=PaymentRecord.ALLOW_CREATE_VERIFICATION).count()

    @property
    def bank_reconciliation_error(self) -> int:
        return self.payment_items.filter(status=PaymentRecord.STATUS_ERROR).count()

    @cached_property
    def total_number_of_households(self) -> int:
        # https://unicef.visualstudio.com/ICTD-HCT-MIS/_workitems/edit/84040
        return self.payment_items.count()

    @property
    def currency(self) -> Optional[str]:
        payment_record = self.payment_items.first()
        return payment_record.currency if payment_record else None

    @property
    def currency_exchange_date(self) -> datetime:
        return self.dispersion_date

    def unicef_id(self) -> str:
        return self.ca_id

    @property
    def verification_status(self) -> Optional[str]:
        summary = self.payment_verification_summary.first()
        return getattr(summary, "status", None)

    class Meta:
        verbose_name = "Cash Plan"
        ordering = ["created_at"]


class PaymentRecord(ConcurrencyModel, AdminUrlMixin, GenericPayment):
    ENTITLEMENT_CARD_STATUS_ACTIVE = "ACTIVE"
    ENTITLEMENT_CARD_STATUS_INACTIVE = "INACTIVE"
    ENTITLEMENT_CARD_STATUS_CHOICE = Choices(
        (ENTITLEMENT_CARD_STATUS_ACTIVE, _("Active")),
        (ENTITLEMENT_CARD_STATUS_INACTIVE, _("Inactive")),
    )

    ca_id = models.CharField(max_length=255, null=True, db_index=True)
    ca_hash_id = models.UUIDField(unique=True, null=True)
    parent = models.ForeignKey(
        "payment.CashPlan",
        on_delete=models.CASCADE,
        related_name="payment_items",
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
    service_provider = models.ForeignKey(
        "payment.ServiceProvider",
        on_delete=models.CASCADE,
    )
    payment_verification = GenericRelation(
        "payment.PaymentVerification",
        content_type_field="payment_content_type",
        object_id_field="payment_object_id",
        related_query_name="payment_record",
    )
    ticket_complaint_details = GenericRelation(
        "grievance.TicketComplaintDetails",
        content_type_field="payment_content_type",
        object_id_field="payment_object_id",
        related_query_name="payment_record",
    )
    ticket_sensitive_details = GenericRelation(
        "grievance.TicketSensitiveDetails",
        content_type_field="payment_content_type",
        object_id_field="payment_object_id",
        related_query_name="payment_record",
    )

    @property
    def unicef_id(self) -> str:
        return self.ca_id

    def get_revert_mark_as_failed_status(self, delivered_quantity: Decimal) -> str:
        return self.STATUS_SUCCESS


class ServiceProvider(TimeStampedUUIDModel):
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    ca_id = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, null=True)
    short_name = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=3)
    vision_id = models.CharField(max_length=255, null=True)
    is_migrated_to_payment_plan = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.full_name or ""
