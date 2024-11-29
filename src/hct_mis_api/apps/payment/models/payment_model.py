import logging
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import JSONField, Q, UniqueConstraint
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from model_utils import Choices
from model_utils.models import SoftDeletableModel

from hct_mis_api.apps.payment.managers import PaymentManager
from hct_mis_api.apps.payment.models.generic_payment_models import GenericPayment
from hct_mis_api.apps.payment.validators import payment_token_and_order_number_validator
from hct_mis_api.apps.utils.models import (
    AdminUrlMixin,
    InternalDataFieldModel,
    SignatureMixin,
    TimeStampedUUIDModel,
    UnicefIdentifiedModel,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class Payment(
    TimeStampedUUIDModel,
    InternalDataFieldModel,
    SoftDeletableModel,
    UnicefIdentifiedModel,
    AdminUrlMixin,
    SignatureMixin,
):
    # GenericPayment fields

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

    parent = models.ForeignKey(
        "payment.PaymentPlan",
        on_delete=models.CASCADE,
        related_name="payment_items",
    )
    conflicted = models.BooleanField(default=False)
    excluded = models.BooleanField(default=False)
    entitlement_date = models.DateTimeField(null=True, blank=True)
    financial_service_provider = models.ForeignKey(
        "payment.FinancialServiceProvider", on_delete=models.PROTECT, null=True
    )
    collector = models.ForeignKey("household.Individual", on_delete=models.CASCADE, related_name="collector_payments")
    source_payment = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="follow_ups"
    )
    is_follow_up = models.BooleanField(default=False)
    reason_for_unsuccessful_payment = models.CharField(max_length=255, null=True, blank=True)
    # use program_id in UniqueConstraint order_number and token_number per Program
    program = models.ForeignKey("program.Program", on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(100000000),
            MaxValueValidator(999999999),
            payment_token_and_order_number_validator,
        ],
    )  # 9 digits
    token_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1000000), MaxValueValidator(9999999), payment_token_and_order_number_validator],
    )  # 7 digits

    additional_collector_name = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Use this field for reconciliation data when funds are collected by someone other than the designated collector or the alternate collector",
    )
    additional_document_type = models.CharField(
        max_length=128, blank=True, null=True, help_text="Use this field for reconciliation data"
    )
    additional_document_number = models.CharField(
        max_length=128, blank=True, null=True, help_text="Use this field for reconciliation data"
    )
    fsp_auth_code = models.CharField(max_length=128, blank=True, null=True, help_text="FSP Auth Code")
    is_cash_assist = models.BooleanField(default=False)

    @property
    def full_name(self) -> str:
        return self.collector.full_name

    def get_revert_mark_as_failed_status(self, delivered_quantity: Decimal) -> str:
        if delivered_quantity == 0:
            return Payment.STATUS_NOT_DISTRIBUTED

        elif delivered_quantity < self.entitlement_quantity:
            return Payment.STATUS_DISTRIBUTION_PARTIAL

        elif delivered_quantity == self.entitlement_quantity:
            return Payment.STATUS_DISTRIBUTION_SUCCESS

        else:
            raise ValidationError(
                f"Wrong delivered quantity {delivered_quantity} for entitlement quantity {self.entitlement_quantity}"
            )

    objects = PaymentManager()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["parent", "household"],
                condition=Q(is_removed=False) & Q(is_cash_assist=False),
                name="payment_plan_and_household",
            ),
            UniqueConstraint(
                fields=["program_id", "order_number"],
                condition=Q(is_removed=False),
                name="order_number_unique_per_program",
            ),
            UniqueConstraint(
                fields=["program_id", "token_number"],
                condition=Q(is_removed=False),
                name="token_number_unique_per_program",
            ),
        ]

    signature_fields = (
        "parent_id",
        "conflicted",
        "excluded",
        "entitlement_date",
        "financial_service_provider_id",
        "collector_id",
        "source_payment_id",
        "is_follow_up",
        "reason_for_unsuccessful_payment",
        "program_id",
        "order_number",
        "token_number",
        "household_snapshot.snapshot_data",
        "business_area_id",
        "status",
        "status_date",
        "household_id",
        "head_of_household_id",
        "delivery_type",
        "currency",
        "entitlement_quantity",
        "entitlement_quantity_usd",
        "delivered_quantity",
        "delivered_quantity_usd",
        "delivery_date",
        "transaction_reference_id",
    )


class PaymentHouseholdSnapshot(TimeStampedUUIDModel):
    snapshot_data = JSONField(default=dict)
    household_id = models.UUIDField()
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name="household_snapshot")
