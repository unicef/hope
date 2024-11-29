import logging
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Callable, Optional

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
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel

if TYPE_CHECKING:
    from hct_mis_api.apps.core.exchange_rates.api import ExchangeRateClient
    from hct_mis_api.apps.payment.models.payment_verification_models import (
        PaymentVerification,
        PaymentVerificationPlan,
        PaymentVerificationSummary,
    )

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
        from hct_mis_api.apps.payment.models import CashPlan

        return self.ca_id if isinstance(self, CashPlan) else self.unicef_id

    def get_exchange_rate(self, exchange_rates_client: Optional["ExchangeRateClient"] = None) -> float:
        if self.currency == USDC:
            # exchange rate for Digital currency
            return 1.0

        if exchange_rates_client is None:
            exchange_rates_client = ExchangeRates()

        return exchange_rates_client.get_exchange_rate_for_currency_code(self.currency, self.currency_exchange_date)

    @property
    def get_payment_verification_summary(self) -> Optional["PaymentVerificationSummary"]:
        """PaymentPlan has only one payment_verification_summary"""
        c_type = ContentType.objects.get_for_model(self.__class__)
        from hct_mis_api.apps.payment.models.payment_verification_models import (
            PaymentVerificationSummary,
        )

        try:
            verification_summary = PaymentVerificationSummary.objects.get(
                payment_plan_content_type_id=c_type.pk, payment_plan_object_id=self.pk
            )
        except PaymentVerificationSummary.DoesNotExist:
            return None
        return verification_summary

    @property
    def get_payment_verification_plans(self) -> QuerySet["PaymentVerificationPlan"]:
        from hct_mis_api.apps.payment.models.payment_verification_models import (
            PaymentVerificationPlan,
        )

        c_type = ContentType.objects.get_for_model(self.__class__)
        payment_verification_plans = PaymentVerificationPlan.objects.filter(
            payment_plan_content_type_id=c_type.pk, payment_plan_object_id=self.pk
        )
        return payment_verification_plans

    def available_payment_records(
        self,
        payment_verification_plan: Optional["PaymentVerificationPlan"] = None,
        extra_validation: Optional[Callable] = None,
    ) -> QuerySet:
        from hct_mis_api.apps.payment.models.deprecated_cash_assist_models import (
            PaymentRecord,
        )

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

        from hct_mis_api.apps.payment.models.payment_model import Payment

        qs = (PaymentRecord if self.__class__.__name__ == "CashPlan" else Payment).objects.filter(
            pk__in=payment_records
        )

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
    def verification(self) -> Optional["PaymentVerification"]:
        from hct_mis_api.apps.payment.models.payment_verification_models import (
            PaymentVerification,
        )

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
        from hct_mis_api.apps.payment.models.deprecated_cash_assist_models import (
            PaymentRecord,
        )

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
