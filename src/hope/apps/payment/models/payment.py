import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING, Any, Callable, Optional

from dateutil.relativedelta import relativedelta
from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    ProhibitNullCharactersValidator,
)
from django.db import models, transaction
from django.db.models import Count, JSONField, Q, QuerySet, Sum, UniqueConstraint
from django.db.models.functions import Coalesce
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from model_utils import Choices
from model_utils.models import SoftDeletableModel
from multiselectfield import MultiSelectField
from psycopg2._range import NumericRange

from hope.apps.activity_log.utils import create_mapping_dict
from hope.apps.core.currencies import CURRENCY_CHOICES, USDC
from hope.apps.core.exchange_rates import ExchangeRates
from hope.apps.core.field_attributes.core_fields_attributes import (
    FieldFactory,
    get_core_fields_attributes,
)
from hope.apps.core.field_attributes.fields_types import _HOUSEHOLD, _INDIVIDUAL
from hope.apps.core.mixins import LimitBusinessAreaModelMixin
from hope.apps.core.models import FileTemp, FlexibleAttribute, StorageFile
from hope.apps.core.utils import map_unicef_ids_to_households_unicef_ids
from hope.apps.geo.models import Area, Country
from hope.apps.household.models import FEMALE, MALE, DocumentType, Household, Individual
from hope.apps.payment.fields import DynamicChoiceArrayField
from hope.apps.payment.managers import PaymentManager
from hope.apps.payment.validators import payment_token_and_order_number_validator
from hope.apps.steficon.models import Rule, RuleCommit
from hope.apps.targeting.services.targeting_service import TargetingCriteriaQueryingBase
from hope.apps.utils.models import (
    AdminUrlMixin,
    ConcurrencyModel,
    InternalDataFieldModel,
    MergedManager,
    MergeStatusModel,
    PendingManager,
    SignatureMixin,
    TimeStampedModel,
    TimeStampedUUIDModel,
    UnicefIdentifiedModel,
)
from hope.apps.utils.validators import DoubleSpaceValidator, StartEndSpaceValidator

if TYPE_CHECKING:  # pragma: no cover
    from hope.apps.account.models import User
    from hope.apps.core.exchange_rates.api import ExchangeRateClient
    from hope.apps.payment.models import (
        AcceptanceProcessThreshold,
        PaymentVerificationPlan,
    )
    from hope.apps.program.models import Program

logger = logging.getLogger(__name__)


@dataclass
class ModifiedData:
    modified_date: datetime
    modified_by: Optional["User"] = None


# TODO remove in 2 step
class PaymentPlanSplitPayments(TimeStampedUUIDModel):
    payment_plan_split = models.ForeignKey(
        "payment.PaymentPlanSplit",
        on_delete=models.CASCADE,
        related_name="payment_plan_split",
    )
    payment = models.ForeignKey(
        "payment.Payment",
        on_delete=models.CASCADE,
        related_name="payment_plan_split_payment",
    )

    class Meta:
        unique_together = ("payment_plan_split", "payment")


class PaymentPlanSplit(TimeStampedUUIDModel):
    MAX_CHUNKS = 50
    MIN_NO_OF_PAYMENTS_IN_CHUNK = 10

    class SplitType(models.TextChoices):
        NO_SPLIT = "NO_SPLIT", "No Split"
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
    split_type = models.CharField(choices=SplitType.choices, max_length=24, default=SplitType.NO_SPLIT)
    chunks_no = models.IntegerField(null=True, blank=True)
    sent_to_payment_gateway = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    @property
    def is_payment_gateway(self) -> bool:
        return self.payment_plan.is_payment_gateway  # pragma no cover

    @property
    def financial_service_provider(self) -> "FinancialServiceProvider":
        return self.payment_plan.financial_service_provider  # pragma no cover

    @property
    def delivery_mechanism(self) -> str | None:
        return self.payment_plan.delivery_mechanism  # pragma no cover


class PaymentPlan(
    TimeStampedUUIDModel,
    InternalDataFieldModel,
    ConcurrencyModel,
    SoftDeletableModel,
    UnicefIdentifiedModel,
    AdminUrlMixin,
    TargetingCriteriaQueryingBase,
):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "name",
            "created_by",
            "status",
            "status_date",
            "currency",
            "dispersion_start_date",
            "dispersion_end_date",
            "start_date",
            "end_date",
            "background_action_status",
            "imported_file_date",
            "imported_file",
            "export_file",
            "steficon_rule",
            "steficon_applied_date",
            "steficon_rule_targeting",
            "steficon_targeting_applied_date",
            "exclusion_reason",
            "male_children_count",
            "female_children_count",
            "male_adults_count",
            "female_adults_count",
            "total_households_count",
            "total_individuals_count",
            "targeting_criteria_string",
            "excluded_ids",
        ],
        {
            "steficon_rule": "additional_formula",
            "steficon_applied_date": "additional_formula_applied_date",
            "steficon_rule_targeting": "additional_formula_targeting",
            "steficon_targeting_applied_date": "additional_formula_targeting_applied_date",
            "vulnerability_score_min": "score_min",
            "vulnerability_score_max": "score_max",
        },
    )

    class Status(models.TextChoices):
        # new from TP
        TP_OPEN = "TP_OPEN", "Open"
        TP_LOCKED = "TP_LOCKED", "Locked"
        TP_PROCESSING = "PROCESSING", "Processing"  # TODO: do we need this one?
        TP_STEFICON_WAIT = "STEFICON_WAIT", "Steficon Wait"
        TP_STEFICON_RUN = "STEFICON_RUN", "Steficon Run"
        TP_STEFICON_COMPLETED = "STEFICON_COMPLETED", "Steficon Completed"
        TP_STEFICON_ERROR = "STEFICON_ERROR", "Steficon Error"
        DRAFT = "DRAFT", "Draft"  # like ready for PP create

        PREPARING = (
            "PREPARING",
            "Preparing",
        )  # deprecated will remove it after data migrations

        OPEN = "OPEN", "Open"
        LOCKED = "LOCKED", "Locked"
        LOCKED_FSP = "LOCKED_FSP", "Locked FSP"
        IN_APPROVAL = "IN_APPROVAL", "In Approval"
        IN_AUTHORIZATION = "IN_AUTHORIZATION", "In Authorization"
        IN_REVIEW = "IN_REVIEW", "In Review"
        ACCEPTED = "ACCEPTED", "Accepted"
        FINISHED = "FINISHED", "Finished"

    PRE_PAYMENT_PLAN_STATUSES = (
        Status.TP_OPEN,
        Status.TP_LOCKED,
        Status.TP_PROCESSING,
        Status.TP_STEFICON_WAIT,
        Status.TP_STEFICON_RUN,
        Status.TP_STEFICON_COMPLETED,
        Status.TP_STEFICON_ERROR,
        Status.DRAFT,
    )

    HARD_CONFLICT_STATUSES = (
        Status.LOCKED,
        Status.LOCKED_FSP,
        Status.IN_APPROVAL,
        Status.IN_AUTHORIZATION,
        Status.IN_REVIEW,
        Status.ACCEPTED,
        Status.FINISHED,
    )

    CAN_RUN_ENGINE_FORMULA_FOR_ENTITLEMENT = (Status.LOCKED,)
    CAN_RUN_ENGINE_FORMULA_FOR_VULNERABILITY_SCORE = (
        Status.TP_LOCKED,
        Status.TP_STEFICON_COMPLETED,
        Status.TP_STEFICON_ERROR,
    )
    CAN_RUN_ENGINE_FORMULA = CAN_RUN_ENGINE_FORMULA_FOR_ENTITLEMENT + CAN_RUN_ENGINE_FORMULA_FOR_VULNERABILITY_SCORE

    class BuildStatus(models.TextChoices):
        BUILD_STATUS_PENDING = "PENDING", "Pending"
        BUILD_STATUS_BUILDING = "BUILDING", "Building"
        BUILD_STATUS_FAILED = "FAILED", "Failed"
        BUILD_STATUS_OK = "OK", "Ok"

    class BackgroundActionStatus(models.TextChoices):
        RULE_ENGINE_RUN = "RULE_ENGINE_RUN", "Rule Engine Running"
        RULE_ENGINE_ERROR = "RULE_ENGINE_ERROR", "Rule Engine Errored"
        XLSX_EXPORTING = "XLSX_EXPORTING", "Exporting XLSX file"
        XLSX_EXPORT_ERROR = "XLSX_EXPORT_ERROR", "Export XLSX file Error"
        XLSX_IMPORT_ERROR = "XLSX_IMPORT_ERROR", "Import XLSX file Error"
        XLSX_IMPORTING_ENTITLEMENTS = (
            "XLSX_IMPORTING_ENTITLEMENTS",
            "Importing Entitlements XLSX file",
        )
        XLSX_IMPORTING_RECONCILIATION = (
            "XLSX_IMPORTING_RECONCILIATION",
            "Importing Reconciliation XLSX file",
        )
        EXCLUDE_BENEFICIARIES = "EXCLUDE_BENEFICIARIES", "Exclude Beneficiaries Running"
        EXCLUDE_BENEFICIARIES_ERROR = (
            "EXCLUDE_BENEFICIARIES_ERROR",
            "Exclude Beneficiaries Error",
        )
        SEND_TO_PAYMENT_GATEWAY = (
            "SEND_TO_PAYMENT_GATEWAY",
            "Sending to Payment Gateway",
        )
        SEND_TO_PAYMENT_GATEWAY_ERROR = (
            "SEND_TO_PAYMENT_GATEWAY_ERROR",
            "Send to Payment Gateway Error",
        )

    BACKGROUND_ACTION_ERROR_STATES = [
        BackgroundActionStatus.XLSX_EXPORT_ERROR,
        BackgroundActionStatus.XLSX_IMPORT_ERROR,
        BackgroundActionStatus.RULE_ENGINE_ERROR,
        BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR,
        BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY_ERROR,
    ]

    class Action(models.TextChoices):
        TP_LOCK = "TP_LOCK", "Population Lock"
        TP_UNLOCK = "TP_UNLOCK", "Population Unlock"
        TP_REBUILD = "TP_REBUILD", "Population Rebuild"
        DRAFT = "DRAFT", "Draft"
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
        SEND_XLSX_PASSWORD = "SEND_XLSX_PASSWORD", "Send XLSX Password"

    usd_fields = [
        "total_entitled_quantity_usd",
        "total_entitled_quantity_revised_usd",
        "total_delivered_quantity_usd",
        "total_undelivered_quantity_usd",
    ]

    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE, help_text="Business Area")
    program_cycle = models.ForeignKey(
        "program.ProgramCycle",
        related_name="payment_plans",
        on_delete=models.CASCADE,
        help_text="Program Cycle",
    )
    delivery_mechanism = models.ForeignKey("payment.DeliveryMechanism", blank=True, null=True, on_delete=models.PROTECT)
    financial_service_provider = models.ForeignKey(
        "payment.FinancialServiceProvider",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    imported_file = models.ForeignKey(
        FileTemp,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
        help_text="Imported File",
    )
    export_file_entitlement = models.ForeignKey(
        FileTemp,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
        help_text="Export File Entitlement",
    )
    export_file_per_fsp = models.ForeignKey(
        FileTemp,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
        help_text="Export File per FSP",
    )  # save xlsx with auth code for API communication channel FSP, and just xlsx for others
    export_pdf_file_summary = models.ForeignKey(
        FileTemp,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
        help_text="Export PDF File Summary",
    )
    reconciliation_import_file = models.ForeignKey(
        FileTemp,
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
        help_text="Reconciliation Import File",
    )
    steficon_rule = models.ForeignKey(
        RuleCommit,
        null=True,
        on_delete=models.PROTECT,
        related_name="payment_plans",
        blank=True,
        help_text="Engine Formula for calculation entitlement value",
    )
    steficon_rule_targeting = models.ForeignKey(
        RuleCommit,
        null=True,
        on_delete=models.PROTECT,
        related_name="payment_plans_target",
        blank=True,
        help_text="Engine Formula for calculation vulnerability score value",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_payment_plans",
        help_text="Created by user",
    )
    source_payment_plan = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="follow_ups",
        help_text="Source Payment Plan (applicable for follow Up Payment Plan)",
    )

    storage_file = models.OneToOneField(
        StorageFile,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Storage File",
    )

    name = models.CharField(
        max_length=255,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(255),
            DoubleSpaceValidator,
            StartEndSpaceValidator,
            ProhibitNullCharactersValidator(),
        ],
        null=True,
        blank=True,
        help_text="Name",
    )
    start_date = models.DateTimeField(
        db_index=True,
        blank=True,
        null=True,
        help_text="Payment Plan start date",
    )
    end_date = models.DateTimeField(
        db_index=True,
        blank=True,
        null=True,
        help_text="Payment Plan end date",
    )
    currency = models.CharField(
        max_length=4,
        choices=CURRENCY_CHOICES,
        blank=True,
        null=True,
        help_text="Currency",
    )
    dispersion_start_date = models.DateField(blank=True, null=True, help_text="Dispersion Start Date")
    dispersion_end_date = models.DateField(blank=True, null=True, help_text="Dispersion End Date")
    excluded_ids = models.TextField(blank=True, null=True, help_text="Targeting level exclusion IDs")
    exclusion_reason = models.TextField(blank=True, null=True, help_text="Exclusion reason (Targeting level)")
    vulnerability_score_min = models.DecimalField(
        null=True,
        decimal_places=3,
        max_digits=6,
        help_text="Written by a tool such as Engine Formula",
        blank=True,
    )
    vulnerability_score_max = models.DecimalField(
        null=True,
        decimal_places=3,
        max_digits=6,
        help_text="Written by a tool such as Engine Formula",
        blank=True,
    )
    # System fields
    status = FSMField(
        default=Status.TP_OPEN,
        protected=False,
        db_index=True,
        choices=Status.choices,
        help_text="Status [sys]",
    )
    background_action_status = FSMField(
        default=None,
        protected=False,
        db_index=True,
        blank=True,
        null=True,
        choices=BackgroundActionStatus.choices,
        help_text="Background Action Status for celery task [sys]",
    )
    build_status = FSMField(
        choices=BuildStatus.choices,
        default=None,
        protected=False,
        db_index=True,
        null=True,
        blank=True,
        help_text="Build Status for celery task [sys]",
    )
    built_at = models.DateTimeField(null=True, blank=True, help_text="Built at [sys]")
    exchange_rate = models.DecimalField(
        decimal_places=8,
        blank=True,
        null=True,
        max_digits=15,
        help_text="Exchange Rate [sys]",
    )
    female_children_count = models.PositiveIntegerField(default=0, help_text="Female Children Count [sys]")
    male_children_count = models.PositiveIntegerField(default=0, help_text="Male Children Count [sys]")
    female_adults_count = models.PositiveIntegerField(default=0, help_text="Female Adults Count [sys]")
    male_adults_count = models.PositiveIntegerField(default=0, help_text="Male Adults Count [sys]")
    total_households_count = models.PositiveIntegerField(default=0, help_text="Total Households Count [sys]")
    total_individuals_count = models.PositiveIntegerField(default=0, help_text="Total Individuals Count [sys]")
    imported_file_date = models.DateTimeField(blank=True, null=True, help_text="Imported File Date [sys]")
    total_entitled_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        validators=[MinValueValidator(Decimal(0))],
        db_index=True,
        null=True,
        help_text="Total Entitled Quantity [sys]",
    )
    total_entitled_quantity_usd = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        validators=[MinValueValidator(Decimal(0))],
        null=True,
        blank=True,
        help_text="Total Entitled Quantity USD [sys]",
    )
    total_entitled_quantity_revised = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        validators=[MinValueValidator(Decimal(0))],
        db_index=True,
        null=True,
        blank=True,
        help_text="Total Entitled Quantity Revised [sys]",
    )
    total_entitled_quantity_revised_usd = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        validators=[MinValueValidator(Decimal(0))],
        null=True,
        blank=True,
        help_text="Total Entitled Quantity Revised USD [sys]",
    )
    total_delivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        validators=[MinValueValidator(Decimal(0))],
        db_index=True,
        null=True,
        blank=True,
        help_text="Total Delivered Quantity [sys]",
    )
    total_delivered_quantity_usd = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        validators=[MinValueValidator(Decimal(0))],
        null=True,
        blank=True,
        help_text="Total Delivered Quantity USD [sys]",
    )
    total_undelivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        validators=[MinValueValidator(Decimal(0))],
        db_index=True,
        null=True,
        blank=True,
        help_text="Total Undelivered Quantity [sys]",
    )
    total_undelivered_quantity_usd = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        validators=[MinValueValidator(Decimal(0))],
        null=True,
        blank=True,
        help_text="Total Undelivered Quantity USD [sys]",
    )
    steficon_targeting_applied_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Engine Formula applied date for targeting [sys]",
    )
    steficon_applied_date = models.DateTimeField(blank=True, null=True, help_text="Engine Formula applied date [sys]")
    is_follow_up = models.BooleanField(default=False, help_text="Follow Up Payment Plan flag [sys]")
    exclude_household_error = models.TextField(
        blank=True, null=True, help_text="Exclusion reason (Targeting level) [sys]"
    )
    status_date = models.DateTimeField(help_text="Date and time of Payment Plan status [sys]")
    is_cash_assist = models.BooleanField(default=False, help_text="Cash Assist Flag [sys]")

    """
    Filtering criteria flags and a set of ORed Rules. Rules are either applied for a candidate list
    (against Golden Record) or for a final list (against the approved candidate list).
    If flag is applied, target population needs to be filtered by it as an AND condition to the existing set of rules.
    """
    flag_exclude_if_active_adjudication_ticket = models.BooleanField(
        default=False,
        help_text=_(
            "Exclude households with individuals (members or collectors) that have active adjudication ticket(s)."
        ),
    )
    flag_exclude_if_on_sanction_list = models.BooleanField(
        default=False,
        help_text=_("Exclude households with individuals (members or collectors) on sanction list."),
    )

    class Meta:
        verbose_name = "Payment Plan"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return self.unicef_id or ""

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.steficon_rule_targeting and self.steficon_rule_targeting.rule.type != Rule.TYPE_TARGETING:
            raise ValidationError(
                f"The selected RuleCommit must be associated with a Rule of type {Rule.TYPE_TARGETING}."
            )
        if self.steficon_rule and self.steficon_rule.rule.type != Rule.TYPE_PAYMENT_PLAN:
            raise ValidationError(
                f"The selected RuleCommit must be associated with a Rule of type {Rule.TYPE_PAYMENT_PLAN}."
            )
        super().save(*args, **kwargs)

    def update_population_count_fields(self) -> None:
        households_ids = self.eligible_payments.values_list("household_id", flat=True)

        delta18 = relativedelta(years=+18)
        date18ago = datetime.now() - delta18

        targeted_individuals = Individual.objects.filter(household__id__in=households_ids).aggregate(
            male_children_count=Count("id", distinct=True, filter=Q(birth_date__gt=date18ago, sex=MALE)),
            female_children_count=Count("id", distinct=True, filter=Q(birth_date__gt=date18ago, sex=FEMALE)),
            male_adults_count=Count("id", distinct=True, filter=Q(birth_date__lte=date18ago, sex=MALE)),
            female_adults_count=Count("id", distinct=True, filter=Q(birth_date__lte=date18ago, sex=FEMALE)),
            total_individuals_count=Count("id", distinct=True),
        )

        self.female_children_count = targeted_individuals.get("female_children_count", 0)
        self.male_children_count = targeted_individuals.get("male_children_count", 0)
        self.female_adults_count = targeted_individuals.get("female_adults_count", 0)
        self.male_adults_count = targeted_individuals.get("male_adults_count", 0)
        self.total_households_count = households_ids.count()
        self.total_individuals_count = targeted_individuals.get("total_individuals_count", 0)

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
        """Update money fields only for PaymentPlan with currency."""
        if self.status not in self.PRE_PAYMENT_PLAN_STATUSES:
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
                    "total_entitled_quantity",
                    "total_entitled_quantity_usd",
                    "total_delivered_quantity",
                    "total_delivered_quantity_usd",
                    "total_undelivered_quantity",
                    "total_undelivered_quantity_usd",
                ]
            )

    def is_population_open(self) -> bool:
        return self.status in (self.Status.TP_OPEN,)

    def is_population_finalized(self) -> bool:
        return self.status in (self.Status.TP_PROCESSING,)

    def is_population_locked(self) -> bool:
        return self.status in (
            self.Status.TP_LOCKED,
            self.Status.TP_STEFICON_COMPLETED,
            self.Status.TP_STEFICON_ERROR,
        )

    def get_criteria_string(self) -> str:
        try:
            return self.get_criteria_string()
        except Exception:
            return ""

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

    def unsuccessful_payments(self) -> "QuerySet":
        return self.eligible_payments.filter(status__in=Payment.FAILED_STATUSES)

    def unsuccessful_payments_for_follow_up(self) -> "QuerySet":
        """Select unsuccessful payments to create FPP.

        Need to call from source_payment_plan level
        like payment_plan.source_payment_plan.unsuccessful_payments_for_follow_up()
        """
        return (
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

    def payments_used_in_follow_payment_plans(self) -> "QuerySet":
        return Payment.objects.filter(parent__source_payment_plan_id=self.id, excluded=False)

    def _get_last_approval_process_data(self) -> ModifiedData:
        from hope.apps.payment.models import Approval

        approval_process = hasattr(self, "approval_process") and self.approval_process.first()
        if approval_process:
            if self.status == PaymentPlan.Status.IN_APPROVAL:
                return ModifiedData(
                    approval_process.sent_for_approval_date,
                    approval_process.sent_for_approval_by,
                )
            if self.status == PaymentPlan.Status.IN_AUTHORIZATION:
                approval = approval_process.approvals.filter(type=Approval.APPROVAL).order_by("created_at").last()
                if approval:
                    return ModifiedData(approval.created_at, approval.created_by)
            if self.status == PaymentPlan.Status.IN_REVIEW:
                approval = approval_process.approvals.filter(type=Approval.AUTHORIZATION).order_by("created_at").last()
                if approval:
                    return ModifiedData(approval.created_at, approval.created_by)
            if self.status == PaymentPlan.Status.ACCEPTED and (
                approval := approval_process.approvals.filter(type=Approval.FINANCE_RELEASE)
                .order_by("created_at")
                .last()
            ):
                return ModifiedData(approval.created_at, approval.created_by)
        return ModifiedData(self.updated_at)

    # from generic pp
    def get_exchange_rate(self, exchange_rates_client: Optional["ExchangeRateClient"] = None) -> float:
        if self.currency == USDC:
            # exchange rate for Digital currency USDC to USD
            return 1.0

        if exchange_rates_client is None:
            exchange_rates_client = ExchangeRates()

        return exchange_rates_client.get_exchange_rate_for_currency_code(self.currency, self.currency_exchange_date)

    def available_payment_records(
        self,
        payment_verification_plan: Optional["PaymentVerificationPlan"] = None,
        extra_validation: Callable | None = None,
    ) -> QuerySet:
        params = Q(
            status__in=Payment.ALLOW_CREATE_VERIFICATION + Payment.PENDING_STATUSES,
            delivered_quantity__gt=0,
        )

        if payment_verification_plan:
            params &= Q(
                Q(payment_verifications__isnull=True)
                | Q(payment_verifications__payment_verification_plan=payment_verification_plan)
            )
        else:
            params &= Q(payment_verifications__isnull=True)

        payment_records = self.payment_items.select_related("head_of_household").filter(params).distinct()

        if extra_validation:
            payment_records = [pr.pk for pr in filter(extra_validation, payment_records)]

        return Payment.objects.filter(pk__in=payment_records)

    @property
    def program(self) -> "Program":
        return self.program_cycle.program

    @property
    def is_social_worker_program(self) -> bool:
        return self.program_cycle.program.is_social_worker_program

    @property
    def household_list(self) -> "QuerySet":
        """Get household list.

        Copied from TP and used in:
        1) create PP.create_payments() all list just filter by targeting_criteria, PaymentPlan.Status.TP_OPEN
        """
        all_households = Household.objects.filter(business_area=self.business_area, program=self.program_cycle.program)
        households = all_households.filter(self.get_query()).order_by("unicef_id")
        return households.distinct()

    @property
    def household_count(self) -> int:
        return self.household_list.count()

    @property
    def eligible_payments(self) -> QuerySet:
        return self.payment_items.eligible()

    @property
    def can_be_locked(self) -> bool:
        return self.payment_items.filter(Q(payment_plan_hard_conflicted=False) & Q(excluded=False)).exists()

    @property
    def can_create_xlsx_with_fsp_auth_code(self) -> bool:
        """Export MTCN file - xlsx file with password."""
        all_sent_to_fsp = not self.eligible_payments.filter(status=Payment.STATUS_PENDING).exists()
        return self.is_payment_gateway and all_sent_to_fsp

    @property
    def is_payment_gateway(self) -> bool:  # pragma: no cover
        if not getattr(self, "financial_service_provider", None):
            return False
        return self.financial_service_provider.is_payment_gateway

    @property
    def fsp_communication_channel(self) -> str:
        return (
            FinancialServiceProvider.COMMUNICATION_CHANNEL_API
            if self.is_payment_gateway
            else FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX
        )

    @property
    def bank_reconciliation_success(self) -> int:
        return self.payment_items.filter(status__in=Payment.ALLOW_CREATE_VERIFICATION).count()

    @property
    def bank_reconciliation_error(self) -> int:
        return self.payment_items.filter(status=Payment.STATUS_ERROR).count()

    @property
    def excluded_household_ids_targeting_level(self) -> list:
        return map_unicef_ids_to_households_unicef_ids(self.excluded_ids)

    @property
    def targeting_criteria_string(self) -> str:
        return Truncator(self.get_criteria_string()).chars(390, "...")

    def get_excluded_household_ids(self) -> list[str]:
        if not self.excluded_ids:
            return []
        hh_ids_list = []
        hh_ids_list.extend(hh_id.strip() for hh_id in self.excluded_ids.split(",") if hh_id.strip())
        return hh_ids_list

    def get_query(self) -> Q:
        query = super().get_query()
        if self.status != PaymentPlan.Status.TP_OPEN:
            query &= Q(size__gt=0)
        return query

    @property
    def has_empty_criteria(self) -> bool:
        return self.rules.count() == 0

    @property
    def has_empty_ids_criteria(self) -> bool:
        has_hh_ids, has_ind_ids = False, False
        for rule in self.rules.all():
            if rule.household_ids:
                has_hh_ids = True
            if rule.individual_ids:
                has_ind_ids = True

        return not has_hh_ids and not has_ind_ids

    @property
    def excluded_beneficiaries_ids(self) -> list[str]:
        """Return HH or Ind IDs based on Program DCT."""
        return (
            list(self.payment_items.filter(excluded=True).values_list("household__individuals__unicef_id", flat=True))
            if self.is_social_worker_program
            else list(self.payment_items.filter(excluded=True).values_list("household__unicef_id", flat=True))
        )

    @property
    def currency_exchange_date(self) -> datetime:
        now = timezone.now().date()
        return min(now, self.dispersion_end_date)

    @property
    def can_create_payment_verification_plan(self) -> int:
        return self.available_payment_records().count() > 0

    @property
    def has_export_file(self) -> bool:
        """Check if export file exists.

        for Locked plan return export_file_entitlement file
        for Accepted and Finished export_file_per_fsp file
        """
        try:
            if self.status == PaymentPlan.Status.LOCKED:
                return self.export_file_entitlement is not None
            if self.status in (
                PaymentPlan.Status.ACCEPTED,
                PaymentPlan.Status.FINISHED,
            ):
                return self.export_file_per_fsp is not None
            return False
        except FileTemp.DoesNotExist:
            return False

    @property
    def payment_list_export_file_link(self) -> str | None:
        """Return expor file which is different in various statues.

        for Locked plan return export_file_entitlement file link
        for Accepted and Finished export_file_per_fsp file link
        """
        pp_status_to_file_field = {
            PaymentPlan.Status.LOCKED: "export_file_entitlement",
            PaymentPlan.Status.ACCEPTED: "export_file_per_fsp",
            PaymentPlan.Status.FINISHED: "export_file_per_fsp",
        }

        file_field = pp_status_to_file_field.get(self.status)
        if file_field:
            file_obj = getattr(self, file_field, None)
            return file_obj.file.url if file_obj and file_obj.file else None
        return None

    @property
    def imported_file_name(self) -> str:
        """Get file to import entitlements."""
        try:
            return self.imported_file.file.name if self.imported_file else ""
        except FileTemp.DoesNotExist:
            return ""

    @property
    def is_reconciled(self) -> bool:
        if not self.eligible_payments.exists():
            return False

        return (
            self.eligible_payments.exclude(status__in=Payment.PENDING_STATUSES).count()
            == self.eligible_payments.count()
        )

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

    @property
    def last_approval_process_date(self) -> datetime | None:
        return self._get_last_approval_process_data().modified_date

    @property
    def last_approval_process_by(self) -> str | None:
        return self._get_last_approval_process_data().modified_by

    @property
    def can_send_to_payment_gateway(self) -> bool:
        status_accepted = self.status == PaymentPlan.Status.ACCEPTED
        has_payment_gateway_fsp = self.financial_service_provider and self.financial_service_provider.is_payment_gateway
        has_not_sent_to_payment_gateway_splits = self.splits.filter(
            sent_to_payment_gateway=False,
        ).exists()
        return status_accepted and has_payment_gateway_fsp and has_not_sent_to_payment_gateway_splits

    # @transitions #####################################################################

    @transition(
        field=background_action_status,
        source=[None] + BACKGROUND_ACTION_ERROR_STATES,
        target=BackgroundActionStatus.XLSX_EXPORTING,
        conditions=[
            lambda obj: obj.status
            in [
                PaymentPlan.Status.LOCKED,
                PaymentPlan.Status.ACCEPTED,
                PaymentPlan.Status.FINISHED,
            ]
        ],
    )
    def background_action_status_xlsx_exporting(self) -> None:
        pass

    @transition(
        field=background_action_status,
        source=[
            BackgroundActionStatus.XLSX_EXPORTING,
            BackgroundActionStatus.XLSX_EXPORT_ERROR,
        ],
        target=BackgroundActionStatus.XLSX_EXPORT_ERROR,
        conditions=[
            lambda obj: obj.status
            in [
                PaymentPlan.Status.LOCKED,
                PaymentPlan.Status.ACCEPTED,
                PaymentPlan.Status.FINISHED,
            ]
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
        source=[
            BackgroundActionStatus.RULE_ENGINE_RUN,
            BackgroundActionStatus.RULE_ENGINE_ERROR,
        ],
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
            in [
                PaymentPlan.Status.LOCKED,
                PaymentPlan.Status.ACCEPTED,
                PaymentPlan.Status.FINISHED,
            ]
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
            in [
                PaymentPlan.Status.LOCKED,
                PaymentPlan.Status.ACCEPTED,
                PaymentPlan.Status.FINISHED,
            ]
        ],
    )
    def background_action_status_xlsx_import_error(self) -> None:
        pass

    @transition(field=background_action_status, source="*", target=None)
    def background_action_status_none(self) -> None:
        self.background_action_status = None  # little hack

    @transition(
        field=build_status,
        source="*",
        target=BuildStatus.BUILD_STATUS_PENDING,
        conditions=[
            lambda obj: obj.status
            in [
                PaymentPlan.Status.TP_OPEN,
                PaymentPlan.Status.TP_LOCKED,
                PaymentPlan.Status.TP_STEFICON_COMPLETED,
                PaymentPlan.Status.TP_STEFICON_ERROR,
                PaymentPlan.Status.DRAFT,
                PaymentPlan.Status.OPEN,
            ]
        ],
    )
    def build_status_pending(self) -> None:
        self.built_at = timezone.now()

    @transition(
        field=build_status,
        source=[
            BuildStatus.BUILD_STATUS_PENDING,
            BuildStatus.BUILD_STATUS_FAILED,
            BuildStatus.BUILD_STATUS_OK,
        ],
        target=BuildStatus.BUILD_STATUS_BUILDING,
        conditions=[
            lambda obj: obj.status
            in [
                PaymentPlan.Status.TP_OPEN,
                PaymentPlan.Status.TP_LOCKED,
                PaymentPlan.Status.TP_STEFICON_WAIT,
                PaymentPlan.Status.TP_STEFICON_COMPLETED,
                PaymentPlan.Status.TP_STEFICON_ERROR,
            ]
        ],
    )
    def build_status_building(self) -> None:
        self.built_at = timezone.now()

    @transition(
        field=build_status,
        source=BuildStatus.BUILD_STATUS_BUILDING,
        target=BuildStatus.BUILD_STATUS_FAILED,
        conditions=[
            lambda obj: obj.status
            in [
                PaymentPlan.Status.TP_OPEN,
                PaymentPlan.Status.TP_LOCKED,
                PaymentPlan.Status.TP_STEFICON_WAIT,
                PaymentPlan.Status.TP_STEFICON_COMPLETED,
                PaymentPlan.Status.TP_STEFICON_ERROR,
            ]
        ],
    )
    def build_status_failed(self) -> None:
        self.built_at = timezone.now()

    @transition(
        field=build_status,
        source=BuildStatus.BUILD_STATUS_BUILDING,
        target=BuildStatus.BUILD_STATUS_OK,
        conditions=[
            lambda obj: obj.status
            in [
                PaymentPlan.Status.TP_OPEN,
                PaymentPlan.Status.TP_LOCKED,
                PaymentPlan.Status.TP_STEFICON_COMPLETED,
                PaymentPlan.Status.TP_STEFICON_ERROR,
                PaymentPlan.Status.TP_STEFICON_WAIT,
            ]
        ],
    )
    def build_status_ok(self) -> None:
        self.built_at = timezone.now()

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
        source=[
            BackgroundActionStatus.EXCLUDE_BENEFICIARIES,
            BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR,
        ],
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
        source=[
            BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY,
            BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY_ERROR,
        ],
        target=BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY_ERROR,
        conditions=[lambda obj: obj.status in [PaymentPlan.Status.ACCEPTED]],
    )
    def background_action_status_send_to_payment_gateway_error(self) -> None:
        pass

    @transition(
        field=status,
        source=Status.TP_OPEN,
        target=Status.TP_LOCKED,
    )
    def status_tp_lock(self) -> None:
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=[
            Status.TP_LOCKED,
            Status.TP_STEFICON_COMPLETED,
            Status.TP_STEFICON_ERROR,
        ],
        target=Status.TP_OPEN,
    )
    def status_tp_open(self) -> None:
        # revert all soft deleted by vulnerability_score filter
        self.payment_items(manager="all_objects").filter(is_removed=True).update(is_removed=False)
        self.status_date = timezone.now()

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
        from hope.apps.payment.models import PaymentVerificationSummary

        self.status_date = timezone.now()

        if not hasattr(self, "payment_verification_summary"):
            PaymentVerificationSummary.objects.create(payment_plan=self)

    @transition(
        field=status,
        source=[Status.ACCEPTED, Status.FINISHED],
        target=Status.FINISHED,
    )
    def status_finished(self) -> None:
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=[
            Status.TP_LOCKED,
            Status.TP_STEFICON_COMPLETED,
            Status.TP_STEFICON_ERROR,
            Status.OPEN,
        ],
        target=Status.DRAFT,
    )
    def status_draft(self) -> None:
        self.status_date = timezone.now()

    @transition(
        field=status,
        source=Status.DRAFT,
        target=Status.OPEN,
    )
    def status_open(self) -> None:
        self.status_date = timezone.now()


class FlexFieldArrayField(ArrayField):
    def formfield(
        self,
        form_class: Any | None = ...,
        choices_form_class: Any | None = ...,
        **kwargs: Any,
    ) -> Any:
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
        ("alternate_collector_family_name", _("Alternate collector Family Name")),
        ("alternate_collector_middle_name", _("Alternate collector Middle Name")),
        ("alternate_collector_phone_no", _("Alternate collector phone number")),
        (
            "alternate_collector_document_numbers",
            _("Alternate collector Document numbers"),
        ),
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
        (
            "transaction_status_blockchain_link",
            _("Transaction Status on the Blockchain"),
        ),
        ("fsp_auth_code", _("Auth Code")),
        ("account_data", _("Account Data")),
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
    document_types = DynamicChoiceArrayField(
        models.CharField(max_length=255, blank=True),
        choices_callable=DocumentType.get_all_doc_types_choices,
        default=list,
        blank=True,
    )

    @staticmethod
    def get_data_from_payment_snapshot(
        household_data: dict[str, Any],
        core_field: dict[str, Any],
    ) -> str | None:
        collector_data = household_data.get("primary_collector") or household_data.get("alternate_collector") or {}
        primary_collector = household_data.get("primary_collector", {})
        alternate_collector = household_data.get("alternate_collector", {})

        lookup = core_field["lookup"]
        main_key = None  # just help find specific field from snapshot
        snapshot_field_path = core_field.get("snapshot_field")
        if snapshot_field_path:
            snapshot_field_path_split = snapshot_field_path.split("__")
            main_key = snapshot_field_path.split("__")[0] if len(snapshot_field_path_split) > 0 else None

            if main_key in {"country_origin_id", "country_id"}:
                country = Country.objects.filter(pk=household_data.get(main_key)).first()
                return country.iso_code3 if country else None

            if main_key in {"admin1_id", "admin2_id", "admin3_id", "admin4_id"}:
                area = Area.objects.filter(pk=household_data.get(main_key)).first()
                return f"{area.p_code} - {area.name}" if area else "" if area else None

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

            if main_key == "documents":
                doc_type, doc_lookup = (
                    snapshot_field_path_split[1],
                    snapshot_field_path_split[2],
                )
                documents_list = collector_data.get("documents", [])
                documents_dict = {doc.get("type"): doc for doc in documents_list}
                return documents_dict.get(doc_type, {}).get(doc_lookup)

        if core_field["associated_with"] == _INDIVIDUAL:
            return collector_data.get(lookup, None) or collector_data.get(main_key, None)

        if core_field["associated_with"] == _HOUSEHOLD:
            return household_data.get(lookup)

        return None

    @staticmethod
    def get_column_from_core_field(
        payment: "Payment",
        core_field_name: str,
    ) -> Any:
        core_fields_attributes = FieldFactory(get_core_fields_attributes()).to_dict_by("name")
        core_field = core_fields_attributes.get(core_field_name)
        if not core_field:
            # Some fields can be added to the template, such as 'size'
            # which are not applicable to "People" export.
            return None

        snapshot = getattr(payment, "household_snapshot", None)
        if not snapshot:
            logger.warning(f"Not found snapshot for Payment {payment.unicef_id}")
            return None

        return FinancialServiceProviderXlsxTemplate.get_data_from_payment_snapshot(snapshot.snapshot_data, core_field)

    @classmethod
    def get_column_value_from_payment(cls, payment: "Payment", column_name: str) -> str | float | list | None:
        # we can get if needed payment.parent.program.is_social_worker_program
        snapshot = getattr(payment, "household_snapshot", None)
        if not snapshot:
            logger.warning(f"Not found snapshot for Payment {payment.unicef_id}")
            return None
        snapshot_data = snapshot.snapshot_data
        primary_collector = snapshot_data.get("primary_collector", {})
        alternate_collector = snapshot_data.get("alternate_collector", {})
        collector_data = primary_collector or alternate_collector or {}

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
            "alternate_collector_family_name": (alternate_collector, "family_name"),
            "alternate_collector_sex": (alternate_collector, "sex"),
            "alternate_collector_phone_no": (alternate_collector, "phone_no"),
            "alternate_collector_document_numbers": (
                alternate_collector,
                "document_number",
            ),
            "payment_channel": (payment.delivery_type, "name"),
            "fsp_name": (payment.financial_service_provider, "name"),
            "currency": (payment, "currency"),
            "entitlement_quantity": (payment, "entitlement_quantity"),
            "entitlement_quantity_usd": (payment, "entitlement_quantity_usd"),
            "delivered_quantity": (payment, "delivered_quantity"),
            "delivery_date": (payment, "delivery_date"),
            "reference_id": (payment, "transaction_reference_id"),
            "reason_for_unsuccessful_payment": (
                payment,
                "reason_for_unsuccessful_payment",
            ),
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
            "fsp_auth_code": (payment, "fsp_auth_code"),
        }
        additional_columns = {
            "admin_level_2": (cls.get_admin_level_2, [snapshot_data]),
            "alternate_collector_document_numbers": (
                cls.get_alternate_collector_doc_numbers,
                [snapshot_data],
            ),
        }
        if column_name in DocumentType.get_all_doc_types():
            return cls.get_document_number_by_doc_type_key(snapshot_data, column_name)

        if column_name in additional_columns:
            method, args = additional_columns[column_name]
            return method(*args)

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

    @classmethod
    def get_account_value_from_payment(cls, payment: "Payment", key_name: str) -> str | float | list | None:
        """Get Account values from Collector's Account.data."""
        snapshot = getattr(payment, "household_snapshot", None)
        if not snapshot:
            logger.warning(f"Not found snapshot for Payment {payment.unicef_id}")
            return None
        snapshot_data = snapshot.snapshot_data
        collector_data = (
            snapshot_data.get("primary_collector", {}) or snapshot_data.get("alternate_collector", {}) or {}
        )
        account_data = collector_data.get("account_data", {})
        return account_data.get(key_name, "")

    @staticmethod
    def get_document_number_by_doc_type_key(snapshot_data: dict[str, Any], document_type_key: str) -> str:
        collector_data = (
            snapshot_data.get("primary_collector", {}) or snapshot_data.get("alternate_collector", {}) or {}
        )
        documents_list = collector_data.get("documents", [])
        documents_dict = {doc.get("type"): doc for doc in documents_list}
        return documents_dict.get(document_type_key, {}).get("document_number", "")

    @staticmethod
    def get_alternate_collector_doc_numbers(snapshot_data: dict[str, Any]) -> str:
        alternate_collector_data = snapshot_data.get("alternate_collector", {}) or {}
        doc_list = alternate_collector_data.get("documents", [])
        doc_numbers = [doc.get("document_number", "") for doc in doc_list]
        return ", ".join(doc_numbers)

    @staticmethod
    def get_admin_level_2(snapshot_data: dict[str, Any]) -> str:
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
        "payment.FinancialServiceProvider",
        on_delete=models.CASCADE,
        related_name="fsp_xlsx_template_per_delivery_mechanisms",
    )
    delivery_mechanism = models.ForeignKey("DeliveryMechanism", on_delete=models.SET_NULL, null=True)
    xlsx_template = models.ForeignKey(
        "payment.FinancialServiceProviderXlsxTemplate",
        on_delete=models.CASCADE,
        related_name="fsp_xlsx_template_per_delivery_mechanisms",
    )

    class Meta:
        unique_together = ("financial_service_provider", "delivery_mechanism")

    def __str__(self) -> str:
        return f"{self.financial_service_provider.name} - {self.xlsx_template} - {self.delivery_mechanism}"


class FinancialServiceProvider(InternalDataFieldModel, LimitBusinessAreaModelMixin, TimeStampedUUIDModel):
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
    payment_gateway_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.vision_vendor_number}): {self.communication_channel}"

    def get_xlsx_template(self, delivery_mechanism: str) -> Optional["FinancialServiceProviderXlsxTemplate"]:
        try:
            return self.xlsx_templates.get(
                fsp_xlsx_template_per_delivery_mechanisms__delivery_mechanism=delivery_mechanism
            )
        except FinancialServiceProviderXlsxTemplate.DoesNotExist:
            return None

    @property
    def is_payment_gateway(self) -> bool:
        return self.communication_channel == self.COMMUNICATION_CHANNEL_API and self.payment_gateway_id is not None


# TODO MB remove in step 2
class DeliveryMechanismPerPaymentPlan(TimeStampedUUIDModel):
    payment_plan = models.OneToOneField(
        "payment.PaymentPlan",
        on_delete=models.CASCADE,
        related_name="delivery_mechanism_per_payment_plan",
    )
    financial_service_provider = models.ForeignKey(
        "payment.FinancialServiceProvider",
        on_delete=models.PROTECT,
        related_name="delivery_mechanisms_per_payment_plan",
        null=True,
    )
    delivery_mechanism = models.ForeignKey("DeliveryMechanism", on_delete=models.SET_NULL, null=True)
    delivery_mechanism_order = models.PositiveIntegerField()
    sent_to_payment_gateway = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "payment_plan",
                    "delivery_mechanism",
                    "delivery_mechanism_order",
                ],
                name="unique payment_plan_delivery_mechanism",
            ),
        ]


class Payment(
    TimeStampedUUIDModel,
    InternalDataFieldModel,
    SoftDeletableModel,
    UnicefIdentifiedModel,
    AdminUrlMixin,
    SignatureMixin,
):
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
        (
            STATUS_DISTRIBUTION_PARTIAL,
            _("Partially Distributed"),
        ),  # Delivered Partially
        (STATUS_PENDING, _("Pending")),  # Pending
        (STATUS_SENT_TO_PG, _("Sent to Payment Gateway")),
        (STATUS_SENT_TO_FSP, _("Sent to FSP")),
        (STATUS_MANUALLY_CANCELLED, _("Manually Cancelled")),
    )

    ALLOW_CREATE_VERIFICATION = (
        STATUS_SUCCESS,
        STATUS_DISTRIBUTION_SUCCESS,
        STATUS_DISTRIBUTION_PARTIAL,
        STATUS_NOT_DISTRIBUTED,
    )
    PENDING_STATUSES = (STATUS_PENDING, STATUS_SENT_TO_PG, STATUS_SENT_TO_FSP)
    DELIVERED_STATUSES = (
        STATUS_SUCCESS,
        STATUS_DISTRIBUTION_SUCCESS,
        STATUS_DISTRIBUTION_PARTIAL,
    )
    FAILED_STATUSES = (
        STATUS_FORCE_FAILED,
        STATUS_ERROR,
        STATUS_MANUALLY_CANCELLED,
        STATUS_NOT_DISTRIBUTED,
    )

    ENTITLEMENT_CARD_STATUS_ACTIVE = "ACTIVE"
    ENTITLEMENT_CARD_STATUS_INACTIVE = "INACTIVE"
    ENTITLEMENT_CARD_STATUS_CHOICE = Choices(
        (ENTITLEMENT_CARD_STATUS_ACTIVE, _("Active")),
        (ENTITLEMENT_CARD_STATUS_INACTIVE, _("Inactive")),
    )

    parent = models.ForeignKey(
        "payment.PaymentPlan",
        on_delete=models.CASCADE,
        related_name="payment_items",
    )
    parent_split = models.ForeignKey(
        "payment.PaymentPlanSplit",
        on_delete=models.SET_NULL,
        related_name="split_payment_items",
        null=True,
        blank=True,
    )
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    # use program_id in UniqueConstraint order_number and token_number per Program
    program = models.ForeignKey("program.Program", on_delete=models.SET_NULL, null=True, blank=True)
    household = models.ForeignKey("household.Household", on_delete=models.CASCADE)
    head_of_household = models.ForeignKey("household.Individual", on_delete=models.CASCADE, null=True)
    delivery_type = models.ForeignKey("payment.DeliveryMechanism", on_delete=models.SET_NULL, null=True)
    financial_service_provider = models.ForeignKey(
        "payment.FinancialServiceProvider", on_delete=models.PROTECT, null=True
    )
    collector = models.ForeignKey(
        "household.Individual",
        on_delete=models.CASCADE,
        related_name="collector_payments",
    )
    source_payment = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="follow_ups",
    )
    is_follow_up = models.BooleanField(default=False)
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICE,
        default=STATUS_PENDING,
    )
    status_date = models.DateTimeField()
    currency = models.CharField(
        max_length=4,
        null=True,
        blank=True,
    )
    entitlement_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        null=True,
        blank=True,
    )
    entitlement_quantity_usd = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        null=True,
        blank=True,
    )
    entitlement_date = models.DateTimeField(null=True, blank=True)
    delivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        null=True,
        blank=True,
    )
    delivered_quantity_usd = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        null=True,
        blank=True,
    )
    delivery_date = models.DateTimeField(null=True, blank=True)
    transaction_reference_id = models.CharField(max_length=255, null=True, blank=True)  # transaction_id
    transaction_status_blockchain_link = models.CharField(max_length=255, null=True, blank=True)
    conflicted = models.BooleanField(default=False)
    excluded = models.BooleanField(default=False)
    has_valid_wallet = models.BooleanField(default=True)
    reason_for_unsuccessful_payment = models.CharField(max_length=255, null=True, blank=True)
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
        validators=[
            MinValueValidator(1000000),
            MaxValueValidator(9999999),
            payment_token_and_order_number_validator,
        ],
    )  # 7 digits

    additional_collector_name = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Use this field for reconciliation data when funds are collected by someone other than the designated collector or the alternate collector",
    )
    additional_document_type = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Use this field for reconciliation data",
    )
    additional_document_number = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Use this field for reconciliation data",
    )
    fsp_auth_code = models.CharField(max_length=128, blank=True, null=True, help_text="FSP Auth Code")

    vulnerability_score = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        help_text="Written by Steficon",
        db_index=True,
    )
    is_cash_assist = models.BooleanField(default=False)

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

    def mark_as_failed(self) -> None:  # pragma: no cover
        if self.status is self.STATUS_FORCE_FAILED:
            raise ValidationError("Status shouldn't be failed")
        self.status = self.STATUS_FORCE_FAILED
        self.status_date = timezone.now()
        self.delivered_quantity = 0
        self.delivered_quantity_usd = 0
        self.delivery_date = None

    def revert_mark_as_failed(self, delivered_quantity: Decimal, delivery_date: datetime) -> None:  # pragma: no cover
        if self.status != self.STATUS_FORCE_FAILED:
            raise ValidationError("Only payment marked as force failed can be reverted")
        if self.entitlement_quantity is None:
            raise ValidationError("Entitlement quantity need to be set in order to revert")

        self.status = self.get_revert_mark_as_failed_status(delivered_quantity)
        self.status_date = timezone.now()
        self.delivered_quantity = delivered_quantity
        self.delivery_date = delivery_date

    @property
    def household_admin2(self) -> str:
        return self.household.admin2.name if self.household.admin2 else ""

    @property
    def payment_status(self) -> str:  # pragma: no cover
        status = "-"
        if self.status == Payment.STATUS_PENDING:
            status = "Pending"

        elif self.status in (
            Payment.STATUS_DISTRIBUTION_SUCCESS,
            Payment.STATUS_SUCCESS,
        ):
            status = "Delivered Fully"

        elif self.status == Payment.STATUS_DISTRIBUTION_PARTIAL:
            status = "Delivered Partially"

        elif self.status == Payment.STATUS_NOT_DISTRIBUTED:
            status = "Not Delivered"

        elif self.status == Payment.STATUS_ERROR:
            status = "Unsuccessful"

        elif self.status == Payment.STATUS_FORCE_FAILED:
            status = "Force Failed"

        return status

    @property
    def full_name(self) -> str:
        return self.collector.full_name

    @property
    def people_individual(self) -> Individual | None:
        """Return first Individual from Household for DCT social worker."""
        return self.household.individuals.first() if self.parent.is_social_worker_program else None

    def get_revert_mark_as_failed_status(self, delivered_quantity: Decimal) -> str:  # pragma: no cover
        if delivered_quantity == 0:
            return Payment.STATUS_NOT_DISTRIBUTED

        if delivered_quantity < self.entitlement_quantity:
            return Payment.STATUS_DISTRIBUTION_PARTIAL

        if delivered_quantity == self.entitlement_quantity:
            return Payment.STATUS_DISTRIBUTION_SUCCESS

        raise ValidationError(
            f"Wrong delivered quantity {delivered_quantity} for entitlement quantity {self.entitlement_quantity}"
        )


class PaymentHouseholdSnapshot(TimeStampedUUIDModel):
    snapshot_data = JSONField(default=dict)
    household_id = models.UUIDField()
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name="household_snapshot")


class FinancialInstitution(TimeStampedModel):
    class FinancialInstitutionType(models.TextChoices):
        BANK = "bank", "Bank"
        TELCO = "telco", "Telco"
        OTHER = "other", "Other"

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=30, choices=FinancialInstitutionType.choices)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True)
    swift_code = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.id} {self.name}: {self.type}"  # pragma: no cover


class FinancialInstitutionMapping(TimeStampedModel):
    financial_service_provider = models.ForeignKey(FinancialServiceProvider, on_delete=models.CASCADE)
    financial_institution = models.ForeignKey(FinancialInstitution, on_delete=models.CASCADE)
    code = models.CharField(max_length=30)

    class Meta:
        unique_together = ("financial_service_provider", "financial_institution")

    def __str__(self) -> str:
        return f"{self.financial_institution} to {self.financial_service_provider}: {self.code}"


class Account(MergeStatusModel, TimeStampedUUIDModel, SignatureMixin):
    ACCOUNT_FIELD_PREFIX = "account__"

    individual = models.ForeignKey(
        "household.Individual",
        on_delete=models.CASCADE,
        related_name="accounts",
    )
    account_type = models.ForeignKey(
        "payment.AccountType",
        on_delete=models.PROTECT,
    )
    financial_institution = models.ForeignKey(
        "payment.FinancialInstitution",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    number = models.CharField(max_length=256, blank=True, null=True, db_index=True)
    data = JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    unique_key = models.CharField(max_length=256, blank=True, null=True, editable=False)  # type: ignore
    is_unique = models.BooleanField(default=True, db_index=True)
    active = models.BooleanField(default=True, db_index=True)  # False for duplicated/withdrawn individual

    signature_fields = (
        "data",
        "account_type",
    )

    objects = MergedManager()
    all_objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("unique_key", "active", "is_unique"),
                condition=Q(active=True) & Q(unique_key__isnull=False) & Q(is_unique=True),
                name="unique_active_wallet",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.individual} - {self.account_type}"

    @property
    def account_data(self) -> dict:
        data = self.data.copy()
        if self.number:
            data["number"] = self.number
        if self.financial_institution:
            data["financial_institution"] = str(self.financial_institution.id)
        return data

    @account_data.setter
    def account_data(self, account_values: dict) -> None:
        for field_name, value in account_values.items():
            if field_name == "number":
                self.number = value
            elif field_name == "financial_institution":
                self.financial_institution = FinancialInstitution.objects.filter(id=value).first()
            else:
                self.data[field_name] = value

    @cached_property
    def unique_delivery_data_for_account_type(self) -> dict:
        delivery_data = {}
        unique_fields = self.account_type.unique_fields

        for field in unique_fields:
            delivery_data[field] = self.data.get(field, None)

        if self.number:
            delivery_data["number"] = self.number

        return delivery_data

    @property
    def unique_fields(self) -> list[str]:
        return self.account_type.unique_fields

    def update_unique_field(self) -> None:
        if hasattr(self, "unique_fields") and isinstance(self.unique_fields, list | tuple):
            if not self.unique_fields:
                self.is_unique = True
                self.unique_key = None
                self.save(update_fields=["unique_key", "is_unique"])
                return

            sha256 = hashlib.sha256()
            sha256.update(self.individual.program.name.encode("utf-8"))
            sha256.update(self.account_type.key.encode("utf-8"))

            for field_name in self.unique_fields:
                if value := self.unique_delivery_data_for_account_type.get(field_name, None):
                    sha256.update(str(value).encode("utf-8"))

            self.unique_key = sha256.hexdigest()
            try:
                with transaction.atomic():
                    self.is_unique = True
                    self.save(update_fields=["unique_key", "is_unique"])
            except IntegrityError:
                with transaction.atomic():
                    self.is_unique = False
                    self.save(update_fields=["unique_key", "is_unique"])

    @classmethod
    def validate_uniqueness(cls, qs: QuerySet["Account"] | list["Account"]) -> None:
        for dmd in qs:
            dmd.update_unique_field()


class PaymentDataCollector(Account):
    @classmethod
    def get_associated_object(
        cls,
        associated_with: str,
        collector: Individual,
        account: Account | None = None,
    ) -> Any:
        associated_objects = {
            FspNameMapping.SourceModel.INDIVIDUAL.value: collector,
            FspNameMapping.SourceModel.HOUSEHOLD.value: collector.household,
            FspNameMapping.SourceModel.ACCOUNT.value: account.account_data if account else {},
        }
        return associated_objects.get(associated_with)

    @classmethod
    def delivery_data(
        cls,
        fsp: "FinancialServiceProvider",
        delivery_mechanism: "DeliveryMechanism",
        collector: "Individual",
    ) -> dict:
        delivery_data = {}
        account = collector.accounts.filter(account_type=delivery_mechanism.account_type).first()

        dm_configs = DeliveryMechanismConfig.objects.filter(fsp=fsp, delivery_mechanism=delivery_mechanism)
        collector_country = collector.household and collector.household.country
        if collector_country and (country_config := dm_configs.filter(country=collector_country).first()):
            dm_config = country_config
        else:
            dm_config = dm_configs.first()
        if not dm_config:
            return account.account_data if account else {}

        fsp_names_mappings = {x.external_name: x for x in fsp.names_mappings.all()}

        for field in dm_config.required_fields:
            if fsp_name_mapping := fsp_names_mappings.get(field):
                internal_field = fsp_name_mapping.hope_name
                associated_object = cls.get_associated_object(fsp_name_mapping.source, collector, account)
            else:
                internal_field = field
                associated_object = account.account_data if account else {}
            if isinstance(associated_object, dict):
                value = associated_object.get(internal_field, None)
                delivery_data[field] = value and str(value)
            else:
                delivery_data[field] = getattr(associated_object, internal_field, None)

        if account:
            if account.number:
                delivery_data["number"] = account.number
            if account.financial_institution:
                delivery_data["financial_institution"] = str(account.financial_institution.id)

        return delivery_data

    @classmethod
    def validate_account(
        cls,
        fsp: "FinancialServiceProvider",
        delivery_mechanism: "DeliveryMechanism",
        collector: Individual,
    ) -> bool:
        if not delivery_mechanism.account_type:
            # ex. "cash" - doesn't need any validation
            return True

        account = collector.accounts.filter(account_type=delivery_mechanism.account_type).first()

        fsp_names_mappings = {x.external_name: x for x in fsp.names_mappings.all()}
        dm_configs = DeliveryMechanismConfig.objects.filter(fsp=fsp, delivery_mechanism=delivery_mechanism)

        collector_country = collector.household and collector.household.country
        if collector_country and (country_config := dm_configs.filter(country=collector_country).first()):
            dm_config = country_config
        else:
            dm_config = dm_configs.first()
        if not dm_config:
            return True

        for field in dm_config.required_fields:
            if fsp_name_mapping := fsp_names_mappings.get(field):
                field = fsp_name_mapping.hope_name
                associated_object = cls.get_associated_object(fsp_name_mapping.source, collector, account)
            else:
                associated_object = account.account_data if account else {}
            if isinstance(associated_object, dict):
                value = associated_object.get(field, None)
            else:
                value = getattr(associated_object, field, None)

            if value in [None, ""]:
                return False

        return True

    class Meta:
        proxy = True
        verbose_name = "Payment Data Collector"
        verbose_name_plural = "Payment Data Collectors"


class PendingAccount(Account):
    objects: PendingManager = PendingManager()  # type: ignore

    class Meta:
        proxy = True
        verbose_name = "Imported Account"
        verbose_name_plural = "Imported Accounts"


class DeliveryMechanism(TimeStampedUUIDModel):
    class TransferType(models.TextChoices):
        CASH = "CASH", "Cash"
        VOUCHER = "VOUCHER", "Voucher"
        DIGITAL = "DIGITAL", "Digital"

    payment_gateway_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    transfer_type = models.CharField(max_length=255, choices=TransferType.choices, default=TransferType.CASH)
    account_type = models.ForeignKey(
        "payment.AccountType",
        on_delete=models.PROTECT,
        related_name="delivery_mechanisms",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["code"]
        verbose_name = "Delivery Mechanism"
        verbose_name_plural = "Delivery Mechanisms"

    @classmethod
    def get_choices(cls, only_active: bool = True) -> list[tuple[str, str]]:
        dms = cls.objects.all().values_list("code", "name")
        if only_active:
            dms.filter(is_active=True)
        return list(dms)


class DeliveryMechanismConfig(models.Model):
    delivery_mechanism = models.ForeignKey(DeliveryMechanism, on_delete=models.PROTECT)
    fsp = models.ForeignKey(FinancialServiceProvider, on_delete=models.PROTECT)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, blank=True)
    required_fields = ArrayField(default=list, base_field=models.CharField(max_length=255))

    def __str__(self) -> str:
        return f"{self.delivery_mechanism.code} - {self.fsp.name}"  # pragma: no cover


class AccountType(models.Model):
    key = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=255)
    unique_fields = ArrayField(default=list, base_field=models.CharField(max_length=255))
    payment_gateway_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return self.key

    @classmethod
    def get_targeting_field_names(cls) -> list[str]:
        return [
            f"{_account_type.key}__{field_name}"
            for _account_type in cls.objects.all()
            for field_name in _account_type.unique_fields
        ]


class FspNameMapping(models.Model):
    class SourceModel(models.TextChoices):
        INDIVIDUAL = "Individual"
        HOUSEHOLD = "Household"
        ACCOUNT = "Account"

    external_name = models.CharField(max_length=255)
    # this is a python attribute / db field name of source model (possibly mixin with all FSP names mapping attributes):
    hope_name = models.CharField(max_length=255)  # default copy of external name
    source = models.CharField(max_length=30, choices=SourceModel.choices, default=SourceModel.ACCOUNT)
    fsp = models.ForeignKey(
        FinancialServiceProvider,
        on_delete=models.CASCADE,
        related_name="names_mappings",
    )

    def __str__(self) -> str:
        return self.external_name  # pragma: no cover


class PaymentPlanSupportingDocument(models.Model):
    FILE_LIMIT = 10  # max 10 files per Payment Plan
    FILE_SIZE_LIMIT = 10 * 1024 * 1024  # 10 MB

    title = models.CharField(max_length=255)
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")

    class Meta:
        ordering = ["uploaded_at"]

    def __str__(self) -> str:
        return self.title
