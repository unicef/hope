import logging
from datetime import datetime
from decimal import Decimal
from functools import cached_property
from typing import Optional

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils import Choices

from hct_mis_api.apps.payment.delivery_mechanisms import DeliveryMechanismChoices
from hct_mis_api.apps.payment.models.generic_payment_models import (
    GenericPayment,
    GenericPaymentPlan,
)
from hct_mis_api.apps.utils.models import (
    AdminUrlMixin,
    ConcurrencyModel,
    TimeStampedUUIDModel,
)

logger = logging.getLogger(__name__)


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
