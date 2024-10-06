import hashlib
import json
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union

from django import forms
from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField, IntegerRangeField
from django.contrib.postgres.validators import RangeMinValueValidator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models import (
    Count,
    JSONField,
    Q,
    QuerySet,
    Sum,
    UniqueConstraint,
    UUIDField,
)
from django.db.models.functions import Coalesce
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from dateutil.relativedelta import relativedelta
from django_fsm import FSMField, transition
from graphql import GraphQLError
from model_utils import Choices
from model_utils.models import SoftDeletableModel
from multiselectfield import MultiSelectField
from psycopg2._range import NumericRange

from hct_mis_api.apps.account.models import HorizontalChoiceArrayField
from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES, USDC
from hct_mis_api.apps.core.exchange_rates import ExchangeRates
from hct_mis_api.apps.core.field_attributes.core_fields_attributes import (
    CORE_FIELDS_ATTRIBUTES,
    FieldFactory,
    get_core_fields_attributes,
)
from hct_mis_api.apps.core.field_attributes.fields_types import (
    _DELIVERY_MECHANISM_DATA,
    _HOUSEHOLD,
    _INDIVIDUAL,
    TYPE_STRING,
    Scope,
)
from hct_mis_api.apps.core.mixins import LimitBusinessAreaModelMixin
from hct_mis_api.apps.core.models import BusinessArea, FileTemp, FlexibleAttribute
from hct_mis_api.apps.geo.models import Area, Country
from hct_mis_api.apps.household.models import FEMALE, MALE, Individual
from hct_mis_api.apps.payment.delivery_mechanisms import DeliveryMechanismChoices
from hct_mis_api.apps.payment.fields import DynamicChoiceArrayField
from hct_mis_api.apps.payment.managers import PaymentManager
from hct_mis_api.apps.payment.validators import payment_token_and_order_number_validator
from hct_mis_api.apps.steficon.models import RuleCommit
from hct_mis_api.apps.utils.models import (
    AdminUrlMixin,
    ConcurrencyModel,
    MergedManager,
    MergeStatusModel,
    PendingManager,
    SignatureMixin,
    TimeStampedUUIDModel,
    UnicefIdentifiedModel,
)

if TYPE_CHECKING:
    from hct_mis_api.apps.account.models import User
    from hct_mis_api.apps.core.exchange_rates.api import ExchangeRateClient
    from hct_mis_api.apps.grievance.models import GrievanceTicket
    from hct_mis_api.apps.program.models import Program

logger = logging.getLogger(__name__)


@dataclass
class ModifiedData:
    modified_date: datetime
    modified_by: Optional["User"] = None


class ChoiceArrayFieldDM(ArrayField):
    def formfield(self, form_class: Optional[Any] = ..., choices_form_class: Optional[Any] = ..., **kwargs: Any) -> Any:
        defaults = {
            "form_class": forms.TypedMultipleChoiceField,
            "choices": self.base_field.choices,
            "coerce": self.base_field.to_python,
            "widget": forms.SelectMultiple,
        }
        defaults.update(kwargs)

        return super().formfield(**defaults)


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
        # TODO: maybe 'ca_id' rename to 'unicef_id'?
        return self.ca_id if isinstance(self, CashPlan) else self.unicef_id

    def get_exchange_rate(self, exchange_rates_client: Optional["ExchangeRateClient"] = None) -> float:
        if self.currency == USDC:
            # TODO: is it good place for that?
            # exchange rate for Digital currency
            return 1.0

        if exchange_rates_client is None:
            exchange_rates_client = ExchangeRates()

        return exchange_rates_client.get_exchange_rate_for_currency_code(self.currency, self.currency_exchange_date)

    @property
    def get_payment_verification_summary(self) -> Optional["PaymentVerificationSummary"]:
        """PaymentPlan has only one payment_verification_summary"""
        c_type = ContentType.objects.get_for_model(self.__class__)
        try:
            verification_summary = PaymentVerificationSummary.objects.get(
                payment_plan_content_type_id=c_type.pk, payment_plan_object_id=self.pk
            )
        except PaymentVerificationSummary.DoesNotExist:
            return None
        return verification_summary

    @property
    def get_payment_verification_plans(self) -> QuerySet["PaymentVerificationPlan"]:
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
    delivery_type_choice = models.CharField(
        choices=DeliveryMechanismChoices.DELIVERY_TYPE_CHOICES, max_length=32, null=True
    )  # TODO MB drop later
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


class PaymentPlanSplitPayments(TimeStampedUUIDModel):
    payment_plan_split = models.ForeignKey(
        "payment.PaymentPlanSplit", on_delete=models.CASCADE, related_name="payment_plan_split"
    )
    payment = models.ForeignKey("payment.Payment", on_delete=models.CASCADE, related_name="payment_plan_split_payment")

    class Meta:
        unique_together = ("payment_plan_split", "payment")


class PaymentPlanSplit(TimeStampedUUIDModel):
    MAX_CHUNKS = 50
    MIN_NO_OF_PAYMENTS_IN_CHUNK = 10

    class SplitType(models.TextChoices):
        BY_RECORDS = "BY_RECORDS", "By Records"
        BY_COLLECTOR = "BY_COLLECTOR", "By Collector"
        BY_ADMIN_AREA1 = "BY_ADMIN_AREA1", "By Admin Area 1"
        BY_ADMIN_AREA2 = "BY_ADMIN_AREA2", "By Admin Area 2"
        BY_ADMIN_AREA3 = "BY_ADMIN_AREA3", "By Admin Area 3"

    payment_plan = models.ForeignKey(
        "payment.PaymentPlan",
        on_delete=models.CASCADE,
        related_name="splits",
    )
    split_type = models.CharField(choices=SplitType.choices, max_length=24)
    chunks_no = models.IntegerField(null=True, blank=True)
    payments = models.ManyToManyField(
        "payment.Payment",
        through="PaymentPlanSplitPayments",
        related_name="+",
    )
    sent_to_payment_gateway = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    @property
    def financial_service_provider(self) -> "FinancialServiceProvider":
        return self.payment_plan.delivery_mechanisms.first().financial_service_provider

    @property
    def chosen_configuration(self) -> Optional[str]:
        return self.payment_plan.delivery_mechanisms.first().chosen_configuration

    @property
    def delivery_mechanism(self) -> Optional[str]:
        return self.payment_plan.delivery_mechanisms.first().delivery_mechanism


class PaymentPlan(ConcurrencyModel, SoftDeletableModel, GenericPaymentPlan, UnicefIdentifiedModel, AdminUrlMixin):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "status",
            "status_date",
            "target_population",
            "currency",
            "dispersion_start_date",
            "dispersion_end_date",
            "name",
            "start_date",
            "end_date",
            "background_action_status",
            "imported_file_date",
            "imported_file",
            "export_file",
            "steficon_rule",
            "steficon_applied_date",
            "exclusion_reason",
        ]
    )

    class Status(models.TextChoices):
        PREPARING = "PREPARING", "Preparing"
        OPEN = "OPEN", "Open"
        LOCKED = "LOCKED", "Locked"
        LOCKED_FSP = "LOCKED_FSP", "Locked FSP"
        IN_APPROVAL = "IN_APPROVAL", "In Approval"
        IN_AUTHORIZATION = "IN_AUTHORIZATION", "In Authorization"
        IN_REVIEW = "IN_REVIEW", "In Review"
        ACCEPTED = "ACCEPTED", "Accepted"
        FINISHED = "FINISHED", "Finished"

    class BackgroundActionStatus(models.TextChoices):
        RULE_ENGINE_RUN = "RULE_ENGINE_RUN", "Rule Engine Running"
        RULE_ENGINE_ERROR = "RULE_ENGINE_ERROR", "Rule Engine Errored"
        XLSX_EXPORTING = "XLSX_EXPORTING", "Exporting XLSX file"
        XLSX_EXPORT_ERROR = "XLSX_EXPORT_ERROR", "Export XLSX file Error"
        XLSX_IMPORT_ERROR = "XLSX_IMPORT_ERROR", "Import XLSX file Error"
        XLSX_IMPORTING_ENTITLEMENTS = "XLSX_IMPORTING_ENTITLEMENTS", "Importing Entitlements XLSX file"
        XLSX_IMPORTING_RECONCILIATION = "XLSX_IMPORTING_RECONCILIATION", "Importing Reconciliation XLSX file"
        EXCLUDE_BENEFICIARIES = "EXCLUDE_BENEFICIARIES", "Exclude Beneficiaries Running"
        EXCLUDE_BENEFICIARIES_ERROR = "EXCLUDE_BENEFICIARIES_ERROR", "Exclude Beneficiaries Error"
        SEND_TO_PAYMENT_GATEWAY = "SEND_TO_PAYMENT_GATEWAY", "Sending to Payment Gateway"
        SEND_TO_PAYMENT_GATEWAY_ERROR = "SEND_TO_PAYMENT_GATEWAY_ERROR", "Send to Payment Gateway Error"

    BACKGROUND_ACTION_ERROR_STATES = [
        BackgroundActionStatus.XLSX_EXPORT_ERROR,
        BackgroundActionStatus.XLSX_IMPORT_ERROR,
        BackgroundActionStatus.RULE_ENGINE_ERROR,
        BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR,
        BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY_ERROR,
    ]

    class Action(models.TextChoices):
        LOCK = "LOCK", "Lock"
        LOCK_FSP = "LOCK_FSP", "Lock FSP"
        UNLOCK = "UNLOCK", "Unlock"
        UNLOCK_FSP = "UNLOCK_FSP", "Unlock FSP"
        SEND_FOR_APPROVAL = "SEND_FOR_APPROVAL", "Send For Approval"
        APPROVE = "APPROVE", "Approve"
        AUTHORIZE = "AUTHORIZE", "Authorize"
        REVIEW = "REVIEW", "Review"
        REJECT = "REJECT", "Reject"
        FINISH = "FINISH", "Finish"
        SEND_TO_PAYMENT_GATEWAY = "SEND_TO_PAYMENT_GATEWAY", "Send to Payment Gateway"

    program_cycle = models.ForeignKey(
        "program.ProgramCycle", related_name="payment_plans", null=True, blank=True, on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_payment_plans",
    )
    status = FSMField(default=Status.OPEN, protected=False, db_index=True, choices=Status.choices)
    background_action_status = FSMField(
        default=None,
        protected=False,
        db_index=True,
        blank=True,
        null=True,
        choices=BackgroundActionStatus.choices,
    )
    target_population = models.ForeignKey(
        "targeting.TargetPopulation",
        on_delete=models.CASCADE,
        related_name="payment_plans",
    )
    currency = models.CharField(max_length=4, choices=CURRENCY_CHOICES)
    dispersion_start_date = models.DateField()
    dispersion_end_date = models.DateField()
    female_children_count = models.PositiveIntegerField(default=0)
    male_children_count = models.PositiveIntegerField(default=0)
    female_adults_count = models.PositiveIntegerField(default=0)
    male_adults_count = models.PositiveIntegerField(default=0)
    total_households_count = models.PositiveIntegerField(default=0)
    total_individuals_count = models.PositiveIntegerField(default=0)
    imported_file_date = models.DateTimeField(blank=True, null=True)
    imported_file = models.ForeignKey(FileTemp, null=True, blank=True, related_name="+", on_delete=models.SET_NULL)
    export_file_entitlement = models.ForeignKey(
        FileTemp, null=True, blank=True, related_name="+", on_delete=models.SET_NULL
    )
    export_file_per_fsp = models.ForeignKey(
        FileTemp, null=True, blank=True, related_name="+", on_delete=models.SET_NULL
    )
    export_pdf_file_summary = models.ForeignKey(
        FileTemp, null=True, blank=True, related_name="+", on_delete=models.SET_NULL
    )
    steficon_rule = models.ForeignKey(
        RuleCommit,
        null=True,
        on_delete=models.PROTECT,
        related_name="payment_plans",
        blank=True,
    )
    steficon_applied_date = models.DateTimeField(blank=True, null=True)
    payment_verification_summary = GenericRelation(
        "payment.PaymentVerificationSummary",
        content_type_field="payment_plan_content_type",
        object_id_field="payment_plan_object_id",
        related_query_name="payment_plan",
    )
    payment_verification_plan = GenericRelation(
        "payment.PaymentVerificationPlan",
        content_type_field="payment_plan_content_type",
        object_id_field="payment_plan_object_id",
        related_query_name="payment_plan",
    )
    source_payment_plan = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="follow_ups"
    )
    is_follow_up = models.BooleanField(default=False)
    exclusion_reason = models.TextField(blank=True)
    exclude_household_error = models.TextField(blank=True)
    name = models.CharField(
        max_length=255,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(255),
        ],
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Payment Plan"
        ordering = ["created_at"]
        constraints = [
            UniqueConstraint(
                fields=["name", "program", "is_removed"], condition=Q(is_removed=False), name="name_unique_per_program"
            )
        ]

    def __str__(self) -> str:
        return self.unicef_id or ""

    @property
    def bank_reconciliation_success(self) -> int:
        return self.payment_items.filter(status__in=Payment.ALLOW_CREATE_VERIFICATION).count()

    @property
    def bank_reconciliation_error(self) -> int:
        return self.payment_items.filter(status=Payment.STATUS_ERROR).count()

    @property
    def is_social_worker_program(self) -> bool:
        return self.program.is_social_worker_program

    @property
    def excluded_beneficiaries_ids(self) -> List[str]:
        """based on Program DCT return HH or Ind IDs"""
        beneficiaries_ids = (
            list(self.payment_items.filter(excluded=True).values_list("household__individuals__unicef_id", flat=True))
            if self.is_social_worker_program
            else list(self.payment_items.filter(excluded=True).values_list("household__unicef_id", flat=True))
        )
        return beneficiaries_ids

    @transition(
        field=background_action_status,
        source=[None] + BACKGROUND_ACTION_ERROR_STATES,
        target=BackgroundActionStatus.XLSX_EXPORTING,
        conditions=[
            lambda obj: obj.status
            in [PaymentPlan.Status.LOCKED, PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED]
        ],
    )
    def background_action_status_xlsx_exporting(self) -> None:
        pass

    @transition(
        field=background_action_status,
        source=[BackgroundActionStatus.XLSX_EXPORTING, BackgroundActionStatus.XLSX_EXPORT_ERROR],
        target=BackgroundActionStatus.XLSX_EXPORT_ERROR,
        conditions=[
            lambda obj: obj.status
            in [PaymentPlan.Status.LOCKED, PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED]
        ],
    )
    def background_action_status_xlsx_export_error(self) -> None:
        pass

    @transition(
        field=background_action_status,
        source=[None] + BACKGROUND_ACTION_ERROR_STATES,
        target=BackgroundActionStatus.RULE_ENGINE_RUN,
        conditions=[lambda obj: obj.status == PaymentPlan.Status.LOCKED],
    )
    def background_action_status_steficon_run(self) -> None:
        pass

    @transition(
        field=background_action_status,
        source=[BackgroundActionStatus.RULE_ENGINE_RUN, BackgroundActionStatus.RULE_ENGINE_ERROR],
        target=BackgroundActionStatus.RULE_ENGINE_ERROR,
        conditions=[lambda obj: obj.status == PaymentPlan.Status.LOCKED],
    )
    def background_action_status_steficon_error(self) -> None:
        pass

    @transition(
        field=background_action_status,
        source=[None] + BACKGROUND_ACTION_ERROR_STATES,
        target=BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS,
        conditions=[lambda obj: obj.status == PaymentPlan.Status.LOCKED],
    )
    def background_action_status_xlsx_importing_entitlements(self) -> None:
        pass

    @transition(
        field=background_action_status,
        source=[None] + BACKGROUND_ACTION_ERROR_STATES,
        target=BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
        conditions=[
            lambda obj: obj.status
            in [PaymentPlan.Status.LOCKED, PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED]
        ],
    )
    def background_action_status_xlsx_importing_reconciliation(self) -> None:
        pass

    @transition(
        field=background_action_status,
        source=[
            BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS,
            BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
            BackgroundActionStatus.XLSX_IMPORT_ERROR,
        ],
        target=BackgroundActionStatus.XLSX_IMPORT_ERROR,
        conditions=[
            lambda obj: obj.status
            in [PaymentPlan.Status.LOCKED, PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED]
        ],
    )
    def background_action_status_xlsx_import_error(self) -> None:
        pass

    @transition(field=background_action_status, source="*", target=None)
    def background_action_status_none(self) -> None:
        self.background_action_status = None  # little hack

    @transition(
        field=background_action_status,
        source=[None, BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR],
        target=BackgroundActionStatus.EXCLUDE_BENEFICIARIES,
        conditions=[lambda obj: obj.status in [PaymentPlan.Status.OPEN, PaymentPlan.Status.LOCKED]],
    )
    def background_action_status_excluding_beneficiaries(self) -> None:
        pass

    @transition(
        field=background_action_status,
        source=[BackgroundActionStatus.EXCLUDE_BENEFICIARIES, BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR],
        target=BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR,
        conditions=[lambda obj: obj.status in [PaymentPlan.Status.OPEN, PaymentPlan.Status.LOCKED]],
    )
    def background_action_status_exclude_beneficiaries_error(self) -> None:
        pass

    @transition(
        field=background_action_status,
        source=[None, BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY_ERROR],
        target=BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY,
        conditions=[lambda obj: obj.status in [PaymentPlan.Status.ACCEPTED]],
    )
    def background_action_status_send_to_payment_gateway(self) -> None:
        pass

    @transition(
        field=background_action_status,
        source=[BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY, BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY_ERROR],
        target=BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY_ERROR,
        conditions=[lambda obj: obj.status in [PaymentPlan.Status.ACCEPTED]],
    )
    def background_action_status_send_to_payment_gateway_error(self) -> None:
        pass

    @transition(
        field=status,
        source=Status.OPEN,
        target=Status.LOCKED,
    )
    def status_lock(self) -> None:
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=Status.LOCKED,
        target=Status.OPEN,
    )
    def status_unlock(self) -> None:
        self.background_action_status_none()
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=Status.LOCKED_FSP,
        target=Status.LOCKED,
    )
    def status_unlock_fsp(self) -> None:
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=Status.LOCKED,
        target=Status.LOCKED_FSP,
    )
    def status_lock_fsp(self) -> None:
        self.background_action_status_none()
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=[Status.IN_APPROVAL, Status.IN_AUTHORIZATION, Status.IN_REVIEW],
        target=Status.LOCKED_FSP,
    )
    def status_reject(self) -> None:
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=Status.LOCKED_FSP,
        target=Status.IN_APPROVAL,
    )
    def status_send_to_approval(self) -> None:
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=Status.IN_APPROVAL,
        target=Status.IN_AUTHORIZATION,
    )
    def status_approve(self) -> None:
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=Status.IN_AUTHORIZATION,
        target=Status.IN_REVIEW,
    )
    def status_authorize(self) -> None:
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=Status.IN_REVIEW,
        target=Status.ACCEPTED,
    )
    def status_mark_as_reviewed(self) -> None:
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=[Status.ACCEPTED, Status.FINISHED],
        target=Status.FINISHED,
    )
    def status_finished(self) -> None:
        self.status_date = timezone.now()

        if not self.payment_verification_summary.exists():
            PaymentVerificationSummary.objects.create(
                payment_plan_obj=self,
            )

    @transition(
        field=status,
        source=Status.PREPARING,
        target=Status.OPEN,
    )
    def status_open(self) -> None:
        self.status_date = timezone.now()

    @property
    def currency_exchange_date(self) -> datetime:
        now = timezone.now().date()
        return self.dispersion_end_date if self.dispersion_end_date < now else now

    @property
    def eligible_payments(self) -> QuerySet:
        return self.payment_items.eligible()

    @property
    def can_be_locked(self) -> bool:
        return self.payment_items.filter(Q(payment_plan_hard_conflicted=False) & Q(excluded=False)).exists()

    def update_population_count_fields(self) -> None:
        households_ids = self.eligible_payments.values_list("household_id", flat=True)

        delta18 = relativedelta(years=+18)
        date18ago = datetime.now() - delta18

        targeted_individuals = Individual.objects.filter(household__id__in=households_ids).aggregate(
            male_children_count=Count("id", distinct=True, filter=Q(birth_date__gt=date18ago, sex=MALE)),
            female_children_count=Count("id", distinct=True, filter=Q(birth_date__gt=date18ago, sex=FEMALE)),
            male_adults_count=Count("id", distinct=True, filter=Q(birth_date__lte=date18ago, sex=MALE)),
            female_adults_count=Count("id", distinct=True, filter=Q(birth_date__lte=date18ago, sex=FEMALE)),
        )

        self.female_children_count = targeted_individuals.get("female_children_count", 0)
        self.male_children_count = targeted_individuals.get("male_children_count", 0)
        self.female_adults_count = targeted_individuals.get("female_adults_count", 0)
        self.male_adults_count = targeted_individuals.get("male_adults_count", 0)
        self.total_households_count = households_ids.count()
        self.total_individuals_count = (
            self.female_children_count + self.male_children_count + self.female_adults_count + self.male_adults_count
        )

        self.save(
            update_fields=[
                "female_children_count",
                "male_children_count",
                "female_adults_count",
                "male_adults_count",
                "total_households_count",
                "total_individuals_count",
            ]
        )

    def update_money_fields(self) -> None:
        self.exchange_rate = self.get_exchange_rate()
        payments = self.eligible_payments.aggregate(
            total_entitled_quantity=Coalesce(Sum("entitlement_quantity"), Decimal(0.0)),
            total_entitled_quantity_usd=Coalesce(Sum("entitlement_quantity_usd"), Decimal(0.0)),
            total_delivered_quantity=Coalesce(Sum("delivered_quantity"), Decimal(0.0)),
            total_delivered_quantity_usd=Coalesce(Sum("delivered_quantity_usd"), Decimal(0.0)),
        )

        self.total_entitled_quantity = payments.get("total_entitled_quantity", 0.00)
        self.total_entitled_quantity_usd = payments.get("total_entitled_quantity_usd", 0.00)
        self.total_delivered_quantity = payments.get("total_delivered_quantity", 0.00)
        self.total_delivered_quantity_usd = payments.get("total_delivered_quantity_usd", 0.00)

        self.total_undelivered_quantity = self.total_entitled_quantity - self.total_delivered_quantity
        self.total_undelivered_quantity_usd = self.total_entitled_quantity_usd - self.total_delivered_quantity_usd

        self.save(
            update_fields=[
                "exchange_rate",
                "total_entitled_quantity",
                "total_entitled_quantity_usd",
                "total_delivered_quantity",
                "total_delivered_quantity_usd",
                "total_undelivered_quantity",
                "total_undelivered_quantity_usd",
            ]
        )

    @property
    def has_export_file(self) -> bool:
        """
        for Locked plan return export_file_entitlement file
        for Accepted and Finished export_file_per_fsp file
        """
        try:
            if self.status == PaymentPlan.Status.LOCKED:
                return self.export_file_entitlement is not None
            elif self.status in (PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED):
                return self.export_file_per_fsp is not None
            else:
                return False
        except FileTemp.DoesNotExist:
            return False

    @property
    def payment_list_export_file_link(self) -> Optional[str]:
        """
        for Locked plan return export_file_entitlement file link
        for Accepted and Finished export_file_per_fsp file link
        """
        if self.status == PaymentPlan.Status.LOCKED:
            if self.export_file_entitlement and self.export_file_entitlement.file:
                return self.export_file_entitlement.file.url
            else:
                return None
        elif self.status in (PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED):
            if self.export_file_per_fsp and self.export_file_per_fsp.file:
                return self.export_file_per_fsp.file.url
            else:
                return None
        else:
            return None

    @property
    def imported_file_name(self) -> str:
        """used for import entitlements"""
        try:
            return self.imported_file.file.name if self.imported_file else ""
        except FileTemp.DoesNotExist:
            return ""

    @property
    def is_reconciled(self) -> bool:
        # TODO what in case of active grievance tickets?
        if not self.eligible_payments.exists():
            return False

        return (
            self.eligible_payments.exclude(status__in=GenericPayment.PENDING_STATUSES).count()
            == self.eligible_payments.count()
        )

    def remove_export_file_entitlement(self) -> None:
        self.export_file_entitlement.file.delete(save=False)
        self.export_file_entitlement.delete()
        self.export_file_entitlement = None

    def remove_export_file_per_fsp(self) -> None:
        self.export_file_per_fsp.file.delete(save=False)
        self.export_file_per_fsp.delete()
        self.export_file_per_fsp = None

    def remove_export_files(self) -> None:
        # remove export_file_entitlement
        if self.status == PaymentPlan.Status.LOCKED and self.export_file_entitlement:
            self.remove_export_file_entitlement()
        # remove export_file_per_fsp
        if self.status in (PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED) and self.export_file_per_fsp:
            self.remove_export_file_per_fsp()

    def remove_imported_file(self) -> None:
        if self.imported_file:
            self.imported_file.file.delete(save=False)
            self.imported_file.delete()
            self.imported_file = None
            self.imported_file_date = None

    @cached_property
    def acceptance_process_threshold(self) -> Optional["AcceptanceProcessThreshold"]:
        total_entitled_quantity_usd = int(self.total_entitled_quantity_usd or 0)

        return self.business_area.acceptance_process_thresholds.filter(
            payments_range_usd__contains=NumericRange(
                total_entitled_quantity_usd, total_entitled_quantity_usd, bounds="[]"
            )
        ).first()

    @property
    def approval_number_required(self) -> int:
        if not self.acceptance_process_threshold:
            return 1

        return self.acceptance_process_threshold.approval_number_required

    @property
    def authorization_number_required(self) -> int:
        if not self.acceptance_process_threshold:
            return 1

        return self.acceptance_process_threshold.authorization_number_required

    @property
    def finance_release_number_required(self) -> int:
        if not self.acceptance_process_threshold:
            return 1

        return self.acceptance_process_threshold.finance_release_number_required

    def unsuccessful_payments(self) -> "QuerySet":
        return self.eligible_payments.filter(
            status__in=[
                Payment.STATUS_ERROR,  # delivered_quantity < 0 (-1)
                Payment.STATUS_NOT_DISTRIBUTED,  # delivered_quantity == 0
                Payment.STATUS_FORCE_FAILED,  # TODO remove force failed?
            ]
        )

    def unsuccessful_payments_for_follow_up(self) -> "QuerySet":
        """
        used for creation FPP
        need to call from source_payment_plan level
        like payment_plan.source_payment_plan.unsuccessful_payments_for_follow_up()
        """
        payments_qs = (
            self.unsuccessful_payments()
            .exclude(household__withdrawn=True)  # Exclude beneficiaries who have been withdrawn
            .exclude(
                # Exclude beneficiaries who are currently in different follow-up Payment Plan within the same cycle (contains excluded from other follow-ups)
                household_id__in=Payment.objects.filter(
                    is_follow_up=True,
                    parent__source_payment_plan=self,
                    parent__program_cycle=self.program_cycle,
                    excluded=False,
                )
                .exclude(parent=self)
                .values_list("household_id", flat=True)
            )
        )
        return payments_qs

    def payments_used_in_follow_payment_plans(self) -> "QuerySet":
        return Payment.objects.filter(parent__source_payment_plan_id=self.id, excluded=False)

    @property
    def get_program(self) -> "Program":
        # TODO will update after add feature with 'program_cycle' and migrate all data
        return self.program_cycle.program if self.program_cycle else self.program

    def _get_last_approval_process_data(self) -> ModifiedData:
        approval_process = hasattr(self, "approval_process") and self.approval_process.first()
        if approval_process:
            if self.status == PaymentPlan.Status.IN_APPROVAL:
                return ModifiedData(approval_process.sent_for_approval_date, approval_process.sent_for_approval_by)
            if self.status == PaymentPlan.Status.IN_AUTHORIZATION:
                if approval := approval_process.approvals.filter(type=Approval.APPROVAL).order_by("created_at").last():
                    return ModifiedData(approval.created_at, approval.created_by)
            if self.status == PaymentPlan.Status.IN_REVIEW:
                if (
                    approval := approval_process.approvals.filter(type=Approval.AUTHORIZATION)
                    .order_by("created_at")
                    .last()
                ):
                    return ModifiedData(approval.created_at, approval.created_by)
            if self.status == PaymentPlan.Status.ACCEPTED:
                if (
                    approval := approval_process.approvals.filter(type=Approval.FINANCE_RELEASE)
                    .order_by("created_at")
                    .last()
                ):
                    return ModifiedData(approval.created_at, approval.created_by)
        return ModifiedData(self.updated_at)

    @property
    def last_approval_process_date(self) -> Optional[datetime]:
        return self._get_last_approval_process_data().modified_date

    @property
    def last_approval_process_by(self) -> Optional[str]:
        return self._get_last_approval_process_data().modified_by

    @property
    def can_send_to_payment_gateway(self) -> bool:
        status_accepted = self.status == PaymentPlan.Status.ACCEPTED
        if self.splits.exists():
            has_payment_gateway_fsp = self.delivery_mechanisms.filter(
                financial_service_provider__communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
                financial_service_provider__payment_gateway_id__isnull=False,
            ).exists()
            has_not_sent_to_payment_gateway_splits = self.splits.filter(
                sent_to_payment_gateway=False,
            ).exists()
            return status_accepted and has_payment_gateway_fsp and has_not_sent_to_payment_gateway_splits
        else:
            return (
                status_accepted
                and self.delivery_mechanisms.filter(
                    sent_to_payment_gateway=False,
                    financial_service_provider__communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
                    financial_service_provider__payment_gateway_id__isnull=False,
                ).exists()
            )


class FlexFieldArrayField(ArrayField):
    def formfield(self, form_class: Optional[Any] = ..., choices_form_class: Optional[Any] = ..., **kwargs: Any) -> Any:
        widget = FilteredSelectMultiple(self.verbose_name, False)
        # TODO exclude PDU here
        flexible_attributes = FlexibleAttribute.objects.values_list("name", flat=True)
        flexible_choices = ((x, x) for x in flexible_attributes)
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "widget": widget,
            "choices": flexible_choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


class FinancialServiceProviderXlsxTemplate(TimeStampedUUIDModel):
    COLUMNS_CHOICES = (
        ("payment_id", _("Payment ID")),
        ("household_id", _("Household ID")),
        ("individual_id", _("Individual ID")),
        ("household_size", _("Household Size")),
        ("collector_name", _("Collector Name")),
        ("alternate_collector_full_name", _("Alternate collector Full Name")),
        ("alternate_collector_given_name", _("Alternate collector Given Name")),
        ("alternate_collector_middle_name", _("Alternate collector Middle Name")),
        ("alternate_collector_phone_no", _("Alternate collector phone number")),
        ("alternate_collector_document_numbers", _("Alternate collector Document numbers")),
        ("alternate_collector_sex", _("Alternate collector Gender")),
        ("payment_channel", _("Payment Channel")),
        ("fsp_name", _("FSP Name")),
        ("currency", _("Currency")),
        ("entitlement_quantity", _("Entitlement Quantity")),
        ("entitlement_quantity_usd", _("Entitlement Quantity USD")),
        ("delivered_quantity", _("Delivered Quantity")),
        ("delivery_date", _("Delivery Date")),
        ("reference_id", _("Reference id")),
        ("reason_for_unsuccessful_payment", _("Reason for unsuccessful payment")),
        ("order_number", _("Order Number")),
        ("token_number", _("Token Number")),
        ("additional_collector_name", _("Additional Collector Name")),
        ("additional_document_type", _("Additional Document Type")),
        ("additional_document_number", _("Additional Document Number")),
        ("registration_token", _("Registration Token")),
        ("status", _("Status")),
        ("transaction_status_blockchain_link", _("Transaction Status on the Blockchain")),
    )

    DEFAULT_COLUMNS = [col[0] for col in COLUMNS_CHOICES]

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
        max_length=1000,
        choices=COLUMNS_CHOICES,
        default=DEFAULT_COLUMNS,
        verbose_name=_("Columns"),
        help_text=_("Select the columns to include in the report"),
    )

    core_fields = DynamicChoiceArrayField(
        models.CharField(max_length=255, blank=True),
        choices_callable=FieldFactory.get_all_core_fields_choices,
        default=list,
        blank=True,
    )

    flex_fields = FlexFieldArrayField(
        models.CharField(max_length=255, blank=True),
        default=list,
        blank=True,
    )

    @staticmethod
    def get_data_from_payment_snapshot(
        household_data: Dict[str, Any],
        core_field: Dict[str, Any],
        delivery_mechanism_data: Optional["DeliveryMechanismData"] = None,
    ) -> Optional[str]:
        core_field_name = core_field["name"]
        collector_data = household_data.get("primary_collector") or household_data.get("alternate_collector") or dict()
        primary_collector = household_data.get("primary_collector", {})
        alternate_collector = household_data.get("alternate_collector", {})

        if delivery_mechanism_data and core_field["associated_with"] == _DELIVERY_MECHANISM_DATA:
            delivery_mech_data = collector_data.get("delivery_mechanisms_data", {}).get(
                delivery_mechanism_data.delivery_mechanism.code, {}
            )
            return delivery_mech_data.get(core_field_name, None)

        lookup = core_field["lookup"]
        main_key = None  # just help find specific field from snapshot
        snapshot_field_path = core_field.get("snapshot_field")
        if snapshot_field_path:
            snapshot_field_path_split = snapshot_field_path.split("__")
            main_key = snapshot_field_path.split("__")[0] if len(snapshot_field_path_split) > 0 else None

            if main_key in {"country_origin_id", "country_id"}:
                country = Country.objects.filter(pk=household_data.get(main_key)).first()
                return country.iso_code3 if country else None

            if main_key in {"admin1_id", "admin2_id", "admin3_id", "admin4_id", "admin_area_id"}:
                area = Area.objects.filter(pk=household_data.get(main_key)).first()
                return area.p_code if area else None

            if main_key == "roles":
                lookup_id = primary_collector.get("id") or alternate_collector.get("id")
                if not lookup_id:
                    return None

                for role in household_data.get("roles", []):
                    individual = role.get("individual", {})
                    if individual.get("id") == lookup_id:
                        return role.get("role")
                # return None if role not found
                return None

            if main_key in {"primary_collector", "alternate_collector"}:
                return household_data.get(main_key, {}).get("id")

            if main_key == "bank_account_info":
                bank_account_info_lookup = snapshot_field_path_split[1]
                return collector_data.get("bank_account_info", {}).get(bank_account_info_lookup)

            if main_key == "documents":
                doc_type, doc_lookup = snapshot_field_path_split[1], snapshot_field_path_split[2]
                documents_list = collector_data.get("documents", [])
                documents_dict = {doc.get("type"): doc for doc in documents_list}
                return documents_dict.get(doc_type, {}).get(doc_lookup)

        if core_field["associated_with"] == _INDIVIDUAL:
            return collector_data.get(lookup, None) or collector_data.get(main_key, None)

        if core_field["associated_with"] == _HOUSEHOLD:
            return household_data.get(lookup, None)

        return None

    @staticmethod
    def get_column_from_core_field(
        payment: "Payment",
        core_field_name: str,
        delivery_mechanism_data: Optional["DeliveryMechanismData"] = None,
    ) -> Any:
        core_fields_attributes = FieldFactory(get_core_fields_attributes()).to_dict_by("name")
        core_field = core_fields_attributes.get(core_field_name)
        if not core_field:
            # Some fields can be added to the template, such as 'size' or 'collect_individual_data'
            # which are not applicable to "People" export.
            return None

        snapshot = getattr(payment, "household_snapshot", None)
        if not snapshot:
            logger.error(f"Not found snapshot for Payment {payment.unicef_id}")
            return None

        snapshot_data = FinancialServiceProviderXlsxTemplate.get_data_from_payment_snapshot(
            snapshot.snapshot_data, core_field, delivery_mechanism_data
        )

        return snapshot_data

    @classmethod
    def get_column_value_from_payment(cls, payment: "Payment", column_name: str) -> Union[str, float, list, None]:
        # we can get if needed payment.parent.program.is_social_worker_program
        snapshot = getattr(payment, "household_snapshot", None)
        if not snapshot:
            logger.error(f"Not found snapshot for Payment {payment.unicef_id}")
            return None
        snapshot_data = snapshot.snapshot_data
        primary_collector = snapshot_data.get("primary_collector", {})
        alternate_collector = snapshot_data.get("alternate_collector", {})
        collector_data = primary_collector or alternate_collector or dict()

        map_obj_name_column = {
            "payment_id": (payment, "unicef_id"),
            "individual_id": (collector_data, "unicef_id"),  # add for people export
            "household_id": (snapshot_data, "unicef_id"),  # remove for people export
            "household_size": (snapshot_data, "size"),  # remove for people export
            "admin_level_2": (snapshot_data, "admin2"),
            "village": (snapshot_data, "village"),
            "collector_name": (collector_data, "full_name"),
            "alternate_collector_full_name": (alternate_collector, "full_name"),
            "alternate_collector_given_name": (alternate_collector, "given_name"),
            "alternate_collector_middle_name": (alternate_collector, "middle_name"),
            "alternate_collector_sex": (alternate_collector, "sex"),
            "alternate_collector_phone_no": (alternate_collector, "phone_no"),
            "alternate_collector_document_numbers": (alternate_collector, "document_number"),
            "payment_channel": (payment.delivery_type, "name"),
            "fsp_name": (payment.financial_service_provider, "name"),
            "currency": (payment, "currency"),
            "entitlement_quantity": (payment, "entitlement_quantity"),
            "entitlement_quantity_usd": (payment, "entitlement_quantity_usd"),
            "delivered_quantity": (payment, "delivered_quantity"),
            "delivery_date": (payment, "delivery_date"),
            "reference_id": (payment, "transaction_reference_id"),
            "reason_for_unsuccessful_payment": (payment, "reason_for_unsuccessful_payment"),
            "order_number": (payment, "order_number"),
            "token_number": (payment, "token_number"),
            "additional_collector_name": (payment, "additional_collector_name"),
            "additional_document_type": (payment, "additional_document_type"),
            "additional_document_number": (payment, "additional_document_number"),
            "status": (payment, "payment_status"),
            "transaction_status_blockchain_link": (
                payment,
                "transaction_status_blockchain_link",
            ),
        }
        additional_columns = {
            "registration_token": cls.get_registration_token_doc_number,
            "national_id": cls.get_national_id_doc_number,
            "admin_level_2": cls.get_admin_level_2,
            "alternate_collector_document_numbers": cls.get_alternate_collector_doc_numbers,
        }
        if column_name in additional_columns:
            method = additional_columns[column_name]
            return method(snapshot_data)

        if column_name not in map_obj_name_column:
            return "wrong_column_name"
        if column_name == "delivered_quantity" and payment.status == Payment.STATUS_ERROR:  # Unsuccessful Payment
            return float(-1)
        if column_name == "delivery_date" and payment.delivery_date is not None:
            return str(payment.delivery_date)

        obj, nested_field = map_obj_name_column[column_name]
        # return if obj is dictionary from snapshot
        if isinstance(obj, dict):
            return obj.get(nested_field, "")
        # return if obj is model
        return getattr(obj, nested_field, None) or ""

    @staticmethod
    def get_registration_token_doc_number(snapshot_data: Dict[str, Any]) -> str:
        collector_data = (
            snapshot_data.get("primary_collector", {}) or snapshot_data.get("alternate_collector", {}) or dict()
        )
        documents_list = collector_data.get("documents", [])
        documents_dict = {doc.get("type"): doc for doc in documents_list}
        return documents_dict.get("registration_token", {}).get("document_number", "")

    @staticmethod
    def get_national_id_doc_number(snapshot_data: Dict[str, Any]) -> str:
        collector_data = (
            snapshot_data.get("primary_collector", {}) or snapshot_data.get("alternate_collector", {}) or dict()
        )
        documents_list = collector_data.get("documents", [])
        documents_dict = {doc.get("type"): doc for doc in documents_list}
        return documents_dict.get("national_id", {}).get("document_number", "")

    @staticmethod
    def get_alternate_collector_doc_numbers(snapshot_data: Dict[str, Any]) -> str:
        alternate_collector_data = snapshot_data.get("alternate_collector", {}) or dict()
        doc_list = alternate_collector_data.get("documents", [])
        doc_numbers = [doc.get("document_number", "") for doc in doc_list]
        return ", ".join(doc_numbers)

    @staticmethod
    def get_admin_level_2(snapshot_data: Dict[str, Any]) -> str:
        area = Area.objects.filter(pk=snapshot_data.get("admin2_id")).first()
        return area.name if area else ""

    def __str__(self) -> str:
        return f"{self.name} ({len(self.columns) + len(self.core_fields)})"


class FspXlsxTemplatePerDeliveryMechanism(TimeStampedUUIDModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_fsp_xlsx_template_per_delivery_mechanisms",
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    financial_service_provider = models.ForeignKey(
        "FinancialServiceProvider", on_delete=models.CASCADE, related_name="fsp_xlsx_template_per_delivery_mechanisms"
    )
    delivery_mechanism_choice = models.CharField(
        max_length=255, verbose_name=_("Delivery Mechanism"), choices=DeliveryMechanismChoices.DELIVERY_TYPE_CHOICES
    )  # TODO MB drop later
    delivery_mechanism = models.ForeignKey("DeliveryMechanism", on_delete=models.SET_NULL, null=True)
    xlsx_template = models.ForeignKey(
        "FinancialServiceProviderXlsxTemplate",
        on_delete=models.CASCADE,
        related_name="fsp_xlsx_template_per_delivery_mechanisms",
    )

    class Meta:
        unique_together = ("financial_service_provider", "delivery_mechanism")

    def __str__(self) -> str:
        return f"{self.financial_service_provider.name} - {self.xlsx_template} - {self.delivery_mechanism}"  # pragma: no cover


class FinancialServiceProvider(LimitBusinessAreaModelMixin, TimeStampedUUIDModel):
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
    delivery_mechanisms_choices = HorizontalChoiceArrayField(
        models.CharField(choices=DeliveryMechanismChoices.DELIVERY_TYPE_CHOICES, max_length=32), null=True
    )  # TODO MB drop later
    delivery_mechanisms = models.ManyToManyField("payment.DeliveryMechanism")
    distribution_limit = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        null=True,
        blank=True,
        help_text="The maximum amount of money in USD that can be distributed or unlimited if null",
        db_index=True,
    )
    communication_channel = models.CharField(max_length=6, choices=COMMUNICATION_CHANNEL_CHOICES, db_index=True)
    data_transfer_configuration = models.JSONField(
        help_text="JSON configuration for the data transfer mechanism",
        null=True,
        blank=True,
        default=dict,
    )
    xlsx_templates = models.ManyToManyField(
        "payment.FinancialServiceProviderXlsxTemplate",
        through="FspXlsxTemplatePerDeliveryMechanism",
        related_name="financial_service_providers",
    )
    payment_gateway_id = models.CharField(max_length=255, null=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.vision_vendor_number}): {self.communication_channel}"

    def get_xlsx_template(self, delivery_mechanism: str) -> Optional["FinancialServiceProviderXlsxTemplate"]:
        try:
            return self.xlsx_templates.get(
                fsp_xlsx_template_per_delivery_mechanisms__delivery_mechanism=delivery_mechanism
            )
        except FinancialServiceProviderXlsxTemplate.DoesNotExist:
            return None

    def can_accept_any_volume(self) -> bool:
        if (
            self.distribution_limit is not None
            and self.delivery_mechanisms_per_payment_plan.filter(
                payment_plan__status__in=[
                    PaymentPlan.Status.LOCKED_FSP,
                    PaymentPlan.Status.IN_APPROVAL,
                    PaymentPlan.Status.IN_AUTHORIZATION,
                    PaymentPlan.Status.IN_REVIEW,
                    PaymentPlan.Status.ACCEPTED,
                ]
            ).exists()
        ):
            return False

        if self.distribution_limit == 0.0:
            return False

        return True

    def can_accept_volume(self, volume: Decimal) -> bool:
        if self.distribution_limit is None:
            return True

        return volume <= self.distribution_limit

    @property
    def is_payment_gateway(self) -> bool:
        return self.communication_channel == self.COMMUNICATION_CHANNEL_API and self.payment_gateway_id is not None

    @property
    def configurations(self) -> List[Optional[dict]]:
        return []  # temporary disabled
        if not self.is_payment_gateway:
            return []
        return [
            {"key": config.get("key", None), "label": config.get("label", None), "id": config.get("id", None)}
            for config in self.data_transfer_configuration
        ]


class DeliveryMechanismPerPaymentPlan(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        NOT_SENT = "NOT_SENT"
        SENT = "SENT"

    payment_plan = models.ForeignKey(
        "payment.PaymentPlan",
        on_delete=models.CASCADE,
        related_name="delivery_mechanisms",
    )
    financial_service_provider = models.ForeignKey(
        "payment.FinancialServiceProvider",
        on_delete=models.PROTECT,
        related_name="delivery_mechanisms_per_payment_plan",
        null=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_delivery_mechanisms",
    )
    sent_date = models.DateTimeField()
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sent_delivery_mechanisms",
        null=True,
    )
    status = FSMField(default=Status.NOT_SENT, protected=False, db_index=True)
    delivery_mechanism_choice = models.CharField(
        max_length=255, choices=DeliveryMechanismChoices.DELIVERY_TYPE_CHOICES, db_index=True, null=True
    )  # TODO MB drop later
    delivery_mechanism = models.ForeignKey("DeliveryMechanism", on_delete=models.SET_NULL, null=True)
    delivery_mechanism_order = models.PositiveIntegerField()

    sent_to_payment_gateway = models.BooleanField(default=False)
    chosen_configuration = models.CharField(max_length=50, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["payment_plan", "delivery_mechanism", "delivery_mechanism_order"],
                name="unique payment_plan_delivery_mechanism",
            ),
        ]

    @transition(
        field=status,
        source=Status.NOT_SENT,
        target=Status.SENT,
    )
    def status_send(self, sent_by: "User") -> None:
        self.sent_date = timezone.now()
        self.sent_by = sent_by


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
        # TODO: maybe 'ca_id' rename to 'unicef_id'?
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


class Payment(SoftDeletableModel, GenericPayment, UnicefIdentifiedModel, AdminUrlMixin, SignatureMixin):
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
    payment_verification = GenericRelation(
        "payment.PaymentVerification",
        content_type_field="payment_content_type",
        object_id_field="payment_object_id",
        related_query_name="payment",
    )

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
    ticket_complaint_details = GenericRelation(
        "grievance.TicketComplaintDetails",
        content_type_field="payment_content_type",
        object_id_field="payment_object_id",
        related_query_name="payment",
    )

    ticket_sensitive_details = GenericRelation(
        "grievance.TicketSensitiveDetails",
        content_type_field="payment_content_type",
        object_id_field="payment_object_id",
        related_query_name="payment",
    )
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
                condition=Q(is_removed=False),
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


class ServiceProvider(TimeStampedUUIDModel):
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    ca_id = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, null=True)
    short_name = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=3)
    vision_id = models.CharField(max_length=255, null=True)

    def __str__(self) -> str:
        return self.full_name or ""


class PaymentVerificationPlan(TimeStampedUUIDModel, ConcurrencyModel, UnicefIdentifiedModel, AdminUrlMixin):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "status",
            "payment_plan",
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
    payment_plan_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    payment_plan_object_id = UUIDField()
    payment_plan_obj: "Union[PaymentPlan, CashPlan]" = GenericForeignKey(
        "payment_plan_content_type", "payment_plan_object_id"
    )  # type: ignore
    sampling = models.CharField(max_length=50, choices=SAMPLING_CHOICES)
    verification_channel = models.CharField(max_length=50, choices=VERIFICATION_CHANNEL_CHOICES)
    sample_size = models.PositiveIntegerField(null=True, blank=True)
    responded_count = models.PositiveIntegerField(null=True, blank=True)
    received_count = models.PositiveIntegerField(null=True, blank=True)
    not_received_count = models.PositiveIntegerField(null=True, blank=True)
    received_with_problems_count = models.PositiveIntegerField(null=True, blank=True)
    confidence_interval = models.FloatField(null=True, blank=True)
    margin_of_error = models.FloatField(null=True, blank=True)
    rapid_pro_flow_id = models.CharField(max_length=255, blank=True)
    rapid_pro_flow_start_uuids = ArrayField(models.CharField(max_length=255, blank=True), default=list)
    age_filter = JSONField(null=True, blank=True)
    excluded_admin_areas_filter = JSONField(null=True, blank=True)
    sex_filter = models.CharField(null=True, max_length=10, blank=True)
    activation_date = models.DateTimeField(null=True)
    completion_date = models.DateTimeField(null=True)
    xlsx_file_exporting = models.BooleanField(default=False)
    xlsx_file_imported = models.BooleanField(default=False)
    error = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=["payment_plan_content_type", "payment_plan_object_id"]),
        ]

    @property
    def business_area(self) -> BusinessArea:
        return self.payment_plan_obj.business_area

    @property
    def get_xlsx_verification_file(self) -> FileTemp:
        try:
            return FileTemp.objects.get(object_id=self.pk, content_type=get_content_type_for_model(self))
        except FileTemp.DoesNotExist:
            raise GraphQLError("Xlsx Verification File does not exist.")
        except FileTemp.MultipleObjectsReturned as e:
            logger.exception(e)
            raise GraphQLError("Query returned multiple Xlsx Verification Files when only one was expected.")

    @property
    def has_xlsx_payment_verification_plan_file(self) -> bool:
        return all(
            [
                self.verification_channel == self.VERIFICATION_CHANNEL_XLSX,
                FileTemp.objects.filter(object_id=self.pk, content_type=get_content_type_for_model(self)).count() == 1,
            ]
        )

    @property
    def xlsx_payment_verification_plan_file_link(self) -> Optional[str]:
        return self.get_xlsx_verification_file.file.url if self.has_xlsx_payment_verification_plan_file else None

    @property
    def xlsx_payment_verification_plan_file_was_downloaded(self) -> bool:
        return self.get_xlsx_verification_file.was_downloaded if self.has_xlsx_payment_verification_plan_file else False

    def set_active(self) -> None:
        self.status = PaymentVerificationPlan.STATUS_ACTIVE
        self.activation_date = timezone.now()
        self.error = None

    def set_pending(self) -> None:
        self.status = PaymentVerificationPlan.STATUS_PENDING
        self.responded_count = None
        self.received_count = None
        self.not_received_count = None
        self.received_with_problems_count = None
        self.activation_date = None
        self.rapid_pro_flow_start_uuids = []

    def can_activate(self) -> bool:
        return self.status not in (
            PaymentVerificationPlan.STATUS_PENDING,
            PaymentVerificationPlan.STATUS_RAPID_PRO_ERROR,
        )

    @property
    def get_payment_plan(self) -> Union["PaymentPlan", "CashPlan", None]:
        try:
            # use GFK instead of self.payment_plan_content_type.model_class().objects.get(pk=self.payment_plan_object_id)
            return self.payment_plan_obj
        except ObjectDoesNotExist:
            return None

    @property
    def get_program(self) -> Optional["Program"]:
        if payment_plan := self.get_payment_plan:
            program = (
                payment_plan.program_cycle.program
                if isinstance(payment_plan, PaymentPlan) and payment_plan.program_cycle
                else payment_plan.program
            )
            return program
        return None


def build_summary(payment_plan: Optional[Any]) -> None:
    statuses_count = payment_plan.get_payment_verification_plans.aggregate(
        active=Count("pk", filter=Q(status=PaymentVerificationSummary.STATUS_ACTIVE)),
        pending=Count("pk", filter=Q(status=PaymentVerificationSummary.STATUS_PENDING)),
        finished=Count("pk", filter=Q(status=PaymentVerificationSummary.STATUS_FINISHED)),
    )
    summary = payment_plan.get_payment_verification_summary
    if statuses_count["active"] >= 1:
        summary.mark_as_active()
    elif statuses_count["finished"] >= 1 and statuses_count["active"] == 0 and statuses_count["pending"] == 0:
        summary.mark_as_finished()
    else:
        summary.status = PaymentVerificationSummary.STATUS_PENDING
        summary.completion_date = None
        summary.activation_date = None
        summary.mark_as_pending()
    summary.save()


@receiver(
    post_save,
    sender=PaymentVerificationPlan,
    dispatch_uid="update_verification_status_in_cash_plan",
)
def update_verification_status_in_cash_plan(sender: Any, instance: PaymentVerificationPlan, **kwargs: Any) -> None:
    build_summary(instance.payment_plan_obj)


@receiver(
    post_delete,
    sender=PaymentVerificationPlan,
    dispatch_uid="update_verification_status_in_cash_plan_on_delete",
)
def update_verification_status_in_cash_plan_on_delete(
    sender: Any, instance: PaymentVerificationPlan, **kwargs: Any
) -> None:
    build_summary(instance.payment_plan_obj)


class PaymentVerification(TimeStampedUUIDModel, ConcurrencyModel, AdminUrlMixin):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "payment_verification_plan",
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
    payment_verification_plan = models.ForeignKey(
        "payment.PaymentVerificationPlan",
        on_delete=models.CASCADE,
        related_name="payment_record_verifications",
    )
    payment_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    payment_object_id = UUIDField()
    payment_obj = GenericForeignKey("payment_content_type", "payment_object_id")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_PENDING)
    status_date = models.DateTimeField(null=True)
    received_amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=True,
    )
    sent_to_rapid_pro = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["payment_content_type", "payment_object_id"]),
        ]
        constraints = [
            UniqueConstraint(
                fields=["payment_content_type", "payment_object_id"],
                name="payment_content_type_and_payment_id",
            )
        ]

    @property
    def get_payment(self) -> Union[Payment, PaymentRecord, None]:
        try:
            return self.payment_content_type.model_class().objects.get(pk=self.payment_object_id)
        except ObjectDoesNotExist:
            return None

    @property
    def is_manually_editable(self) -> bool:
        if self.payment_verification_plan.verification_channel != PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL:
            return False
        minutes_elapsed = (timezone.now() - self.status_date).total_seconds() / 60
        return not (self.status != PaymentVerification.STATUS_PENDING and minutes_elapsed > 10)

    @property
    def business_area(self) -> BusinessArea:
        return self.payment_verification_plan.payment_plan_obj.business_area

    def set_pending(self) -> None:
        self.status_date = timezone.now()
        self.status = PaymentVerification.STATUS_PENDING
        self.received_amount = None


class PaymentVerificationSummary(TimeStampedUUIDModel):
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
    payment_plan_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    payment_plan_object_id = UUIDField()
    payment_plan_obj = GenericForeignKey("payment_plan_content_type", "payment_plan_object_id")

    class Meta:
        indexes = [
            models.Index(fields=["payment_plan_content_type", "payment_plan_object_id"]),
        ]
        constraints = [
            UniqueConstraint(
                fields=["payment_plan_content_type", "payment_plan_object_id"],
                name="payment_plan_content_type_and_payment_plan_id",
            )
        ]

    def mark_as_active(self) -> None:
        self.status = self.STATUS_ACTIVE
        self.completion_date = None
        if self.activation_date is None:
            self.activation_date = timezone.now()

    def mark_as_finished(self) -> None:
        self.status = self.STATUS_FINISHED
        if self.completion_date is None:
            self.completion_date = timezone.now()

    def mark_as_pending(self) -> None:
        self.status = self.STATUS_PENDING
        self.completion_date = None
        self.activation_date = None


class ApprovalProcess(TimeStampedUUIDModel):
    sent_for_approval_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True
    )
    sent_for_approval_date = models.DateTimeField(null=True)
    sent_for_authorization_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True
    )
    sent_for_authorization_date = models.DateTimeField(null=True)
    sent_for_finance_release_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True
    )
    sent_for_finance_release_date = models.DateTimeField(null=True)
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name="approval_process")

    approval_number_required = models.PositiveIntegerField(default=1)
    authorization_number_required = models.PositiveIntegerField(default=1)
    finance_release_number_required = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "Approval Processes"


class Approval(TimeStampedUUIDModel):
    APPROVAL = "APPROVAL"
    AUTHORIZATION = "AUTHORIZATION"
    FINANCE_RELEASE = "FINANCE_RELEASE"
    REJECT = "REJECT"
    TYPE_CHOICES = (
        (APPROVAL, "Approval"),
        (AUTHORIZATION, "Authorization"),
        (FINANCE_RELEASE, "Finance Release"),
        (REJECT, "Reject"),
    )

    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default=APPROVAL, verbose_name=_("Approval type"))
    comment = models.CharField(max_length=500, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    approval_process = models.ForeignKey(ApprovalProcess, on_delete=models.CASCADE, related_name="approvals")

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.type or ""

    @property
    def info(self) -> str:
        types_map = {
            self.APPROVAL: "Approved",
            self.AUTHORIZATION: "Authorized",
            self.FINANCE_RELEASE: "Released",
            self.REJECT: "Rejected",
        }

        return f"{types_map.get(self.type)} by {self.created_by}" if self.created_by else types_map.get(self.type, "")


class AcceptanceProcessThreshold(TimeStampedUUIDModel):
    business_area = models.ForeignKey(
        "core.BusinessArea", on_delete=models.PROTECT, related_name="acceptance_process_thresholds"
    )
    payments_range_usd = IntegerRangeField(
        default=NumericRange(0, None),
        validators=[
            RangeMinValueValidator(0),
        ],
    )
    approval_number_required = models.PositiveIntegerField(default=1)
    authorization_number_required = models.PositiveIntegerField(default=1)
    finance_release_number_required = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ("payments_range_usd",)

    def __str__(self) -> str:
        return (
            f"{self.payments_range_usd} USD, "
            f"Approvals: {self.approval_number_required} "
            f"Authorization: {self.authorization_number_required} "
            f"Finance Releases: {self.finance_release_number_required}"
        )


class PaymentHouseholdSnapshot(TimeStampedUUIDModel):
    snapshot_data = JSONField(default=dict)
    household_id = models.UUIDField()
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name="household_snapshot")


class DeliveryMechanismData(MergeStatusModel, TimeStampedUUIDModel, SignatureMixin):
    VALIDATION_ERROR_DATA_NOT_UNIQUE = _("Payment data not unique across Program")
    VALIDATION_ERROR_MISSING_DATA = _("Missing required payment data")

    individual = models.ForeignKey(
        "household.Individual", on_delete=models.CASCADE, related_name="delivery_mechanisms_data"
    )
    delivery_mechanism_choice = models.CharField(
        max_length=255,
        verbose_name=_("Delivery Mechanism"),
        choices=DeliveryMechanismChoices.DELIVERY_TYPE_CHOICES,
        null=True,
        blank=True,
    )  # TODO MB drop later
    delivery_mechanism = models.ForeignKey("DeliveryMechanism", on_delete=models.PROTECT)
    data = JSONField(default=dict, blank=True)

    is_valid: bool = models.BooleanField(default=False)  # type: ignore
    validation_errors: dict = JSONField(default=dict)  # type: ignore
    possible_duplicate_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="possible_duplicates",
        null=True,
        blank=True,
    )
    unique_key = models.CharField(max_length=256, blank=True, null=True, unique=True, editable=False)  # type: ignore

    signature_fields = (
        "data",
        "delivery_mechanism",
    )

    objects = MergedManager()
    all_objects = models.Manager()

    def __str__(self) -> str:
        return f"{self.individual} - {self.delivery_mechanism}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["individual", "delivery_mechanism"],
                name="unique_individual_delivery_mechanism",
            ),
        ]

    def get_associated_object(self, associated_with: str) -> Any:
        from hct_mis_api.apps.core.field_attributes.fields_types import (
            _DELIVERY_MECHANISM_DATA,
            _HOUSEHOLD,
            _INDIVIDUAL,
        )

        associated_objects = {
            _INDIVIDUAL: self.individual,
            _HOUSEHOLD: self.individual.household,
            _DELIVERY_MECHANISM_DATA: self._data,
        }
        return associated_objects.get(associated_with)

    @property
    def _data(self) -> Dict:
        return json.loads(self.data) if not isinstance(self.data, dict) else self.data

    @cached_property
    def delivery_data(self) -> Dict:
        delivery_data = {}
        for field in self.delivery_mechanism_all_fields_definitions:
            associated_object = self.get_associated_object(field["associated_with"])
            if isinstance(associated_object, dict):
                delivery_data[field["name"]] = associated_object.get(field["name"], None)
            else:
                delivery_data[field["name"]] = getattr(associated_object, field["name"], None)

        return delivery_data

    def validate(self) -> None:
        self.validation_errors = {}
        for required_field in self.delivery_mechanism_required_fields_definitions:
            associated_object = self.get_associated_object(required_field["associated_with"])
            if isinstance(associated_object, dict):
                value = associated_object.get(required_field["name"], None)
            else:
                value = getattr(associated_object, required_field["name"], None)
            if value in [None, ""]:
                self.validation_errors[required_field["name"]] = str(self.VALIDATION_ERROR_MISSING_DATA)
                self.is_valid = False
        if not self.validation_errors:
            self.is_valid = True

    def update_unique_field(self) -> None:
        if self.is_valid and hasattr(self, "unique_fields") and isinstance(self.unique_fields, (list, tuple)):
            sha256 = hashlib.sha256()
            sha256.update(self.individual.program.name.encode("utf-8"))

            for field_name in self.unique_fields:
                value = self.delivery_data.get(field_name, None)
                sha256.update(str(value).encode("utf-8"))

            unique_key = sha256.hexdigest()
            possible_duplicates = self.__class__.all_objects.filter(
                rdi_merge_status=MergeStatusModel.MERGED,
                is_valid=True,
                unique_key__isnull=False,
                unique_key=unique_key,
                individual__program=self.individual.program,
                individual__withdrawn=False,
                individual__duplicate=False,
            ).exclude(pk=self.pk)

            if possible_duplicates.exists():
                self.unique_key = None
                self.is_valid = False
                for field_name in self.unique_fields:
                    self.validation_errors[field_name] = str(self.VALIDATION_ERROR_DATA_NOT_UNIQUE)
                self.possible_duplicate_of = possible_duplicates.first()
            else:
                self.unique_key = unique_key

    @property
    def delivery_mechanism_all_fields_definitions(self) -> List[dict]:
        all_core_fields = get_core_fields_attributes()
        return [field for field in all_core_fields if field["name"] in self.all_fields]

    @property
    def delivery_mechanism_required_fields_definitions(self) -> List[dict]:
        all_core_fields = get_core_fields_attributes()
        return [field for field in all_core_fields if field["name"] in self.required_fields]

    @property
    def all_fields(self) -> List[dict]:
        return self.delivery_mechanism.all_fields

    @property
    def all_dm_fields(self) -> List[dict]:
        return self.delivery_mechanism.all_dm_fields

    @property
    def unique_fields(self) -> List[str]:
        return self.delivery_mechanism.unique_fields

    @property
    def required_fields(self) -> List[str]:
        return self.delivery_mechanism.required_fields

    @classmethod
    def get_all_delivery_mechanisms_fields(cls, by_xlsx_name: bool = False) -> List[str]:
        fields = []
        for dm in DeliveryMechanism.objects.filter(is_active=True):
            fields.extend([f for f in dm.all_dm_fields if f not in fields])

        if by_xlsx_name:
            return [f"{field}_i_c" for field in fields]

        return fields

    @classmethod
    def get_scope_delivery_mechanisms_fields(cls, by: str = "name") -> List[str]:
        from hct_mis_api.apps.core.field_attributes.core_fields_attributes import (
            FieldFactory,
        )
        from hct_mis_api.apps.core.field_attributes.fields_types import Scope

        delivery_mechanisms_fields = list(FieldFactory.from_scope(Scope.DELIVERY_MECHANISM).to_dict_by(by).keys())

        return delivery_mechanisms_fields

    def get_grievance_ticket_payload_for_errors(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "label": self.delivery_mechanism.name,
            "approve_status": False,
            "data_fields": [
                {
                    "name": field,
                    "value": None,
                    "previous_value": self.delivery_data.get(field),
                }
                for field, value in self.validation_errors.items()
            ],
        }

    def revalidate_for_grievance_ticket(self, grievance_ticket: "GrievanceTicket") -> None:
        from hct_mis_api.apps.grievance.models import GrievanceTicket

        self.refresh_from_db()
        self.validate()
        if not self.is_valid:
            grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
            description = (
                f"Missing required fields {list(self.validation_errors.keys())}"
                f" values for delivery mechanism {self.delivery_mechanism.name}"
            )
            grievance_ticket.description = description
            individual_data_with_approve_status = self.get_grievance_ticket_payload_for_errors()
            grievance_ticket.individual_data_update_ticket_details.individual_data = {
                "delivery_mechanism_data_to_edit": [individual_data_with_approve_status]
            }
            grievance_ticket.individual_data_update_ticket_details.save()
            grievance_ticket.save()
        else:
            self.update_unique_field()
            if not self.is_valid:
                grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
                description = (
                    f"Fields not unique {list(self.validation_errors.keys())} across program"
                    f" for delivery mechanism {self.delivery_mechanism.name}, possible duplicate of {self.possible_duplicate_of}"
                )
                grievance_ticket.description = description
                individual_data_with_approve_status = self.get_grievance_ticket_payload_for_errors()
                grievance_ticket.individual_data_update_ticket_details.individual_data = {
                    "delivery_mechanism_data_to_edit": [individual_data_with_approve_status]
                }
                grievance_ticket.individual_data_update_ticket_details.save()
                grievance_ticket.save()


class PendingDeliveryMechanismData(DeliveryMechanismData):
    objects: PendingManager = PendingManager()  # type: ignore

    class Meta:
        proxy = True
        verbose_name = "Imported Delivery Mechanism Data"
        verbose_name_plural = "Imported Delivery Mechanism Datas"


class DeliveryMechanism(TimeStampedUUIDModel):
    class TransferType(models.TextChoices):
        CASH = "CASH", "Cash"
        VOUCHER = "VOUCHER", "Voucher"
        DIGITAL = "DIGITAL", "Digital"

    payment_gateway_id = models.CharField(max_length=255, unique=True, null=True)
    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    optional_fields = ArrayField(default=list, base_field=models.CharField(max_length=255))
    required_fields = ArrayField(default=list, base_field=models.CharField(max_length=255))
    unique_fields = ArrayField(default=list, base_field=models.CharField(max_length=255))
    is_active = models.BooleanField(default=True)
    transfer_type = models.CharField(max_length=255, choices=TransferType.choices, default=TransferType.CASH)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["code"]
        verbose_name = "Delivery Mechanism"
        verbose_name_plural = "Delivery Mechanisms"

    def get_label_for_field(self, field: str) -> str:
        return (
            " ".join(word.capitalize() for word in field.replace("__", "_").split("_"))
            + f" ({self.name} Delivery Mechanism)"
        )

    @property
    def all_fields(self) -> List[str]:
        return self.required_fields + self.optional_fields

    @property
    def all_dm_fields(self) -> List[str]:
        core_fields = [cf["name"] for cf in CORE_FIELDS_ATTRIBUTES]
        return [field for field in self.all_fields if field not in core_fields]

    def get_core_fields_definitions(self) -> List[dict]:
        core_fields = [cf["name"] for cf in CORE_FIELDS_ATTRIBUTES]
        return [
            {
                "id": str(uuid.uuid4()),
                "type": TYPE_STRING,
                "name": field,
                "lookup": field,
                "required": False,
                "label": {"English(EN)": self.get_label_for_field(field)},
                "hint": "",
                "choices": [],
                "associated_with": _DELIVERY_MECHANISM_DATA,
                "required_for_payment": field in self.required_fields,
                "unique_for_payment": field in self.unique_fields,
                "xlsx_field": f"{field}_i_c",
                "scope": [Scope.XLSX, Scope.XLSX_PEOPLE, Scope.DELIVERY_MECHANISM],
            }
            for field in self.all_fields
            if field not in core_fields
        ]

    @classmethod
    def get_all_core_fields_definitions(cls) -> List[dict]:
        definitions = []
        for delivery_mechanism in cls.objects.filter(is_active=True).order_by("code"):
            definitions.extend(delivery_mechanism.get_core_fields_definitions())
        return definitions

    @classmethod
    def get_choices(cls, only_active: bool = True) -> List[Tuple[str, str]]:
        dms = cls.objects.all().values_list("code", "name")
        if only_active:
            dms.filter(is_active=True)
        return list(dms)

    @classmethod
    def get_delivery_mechanisms_to_xlsx_fields_mapping(cls) -> Dict[str, List[str]]:
        required_fields_map = defaultdict(list)
        for dm in cls.objects.filter(is_active=True):
            required_fields_map[dm.code].extend([f"{field}_i_c" for field in dm.required_fields])

        return required_fields_map


class PaymentPlanSupportingDocument(models.Model):
    FILE_LIMIT = 10  # max 10 files per Payment Plan
    FILE_SIZE_LIMIT = 10 * 1024 * 1024  # 10 MB

    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255)
    file = models.FileField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")

    class Meta:
        ordering = ["uploaded_at"]

    def __str__(self) -> str:
        return self.title
