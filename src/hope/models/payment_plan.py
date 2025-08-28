from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from functools import cached_property
from typing import Optional, Any, Callable

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    ProhibitNullCharactersValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models import Count, Q, Sum, QuerySet
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from model_utils.models import SoftDeletableModel

from hope.apps.targeting.services.targeting_service import TargetingCriteriaQueryingBase

from hope.apps.activity_log.utils import create_mapping_dict

from hope.apps.utils.validators import DoubleSpaceValidator, StartEndSpaceValidator

from hope.apps.core.currencies import CURRENCY_CHOICES, USDC
from psycopg2._range import NumericRange

from hope.apps.core.exchange_rates import ExchangeRates
from hope.apps.core.utils import map_unicef_ids_to_households_unicef_ids
from hope.models.file_temp import FileTemp
from hope.models.financial_service_provider import FinancialServiceProvider
from hope.models.household import MALE, FEMALE, Household
from hope.models.individual import Individual
from hope.models.payment import Payment
from hope.models.rule import RuleCommit
from hope.models.rule import Rule
from hope.models.storage_file import StorageFile
from hope.models.utils import (
    TimeStampedUUIDModel,
    InternalDataFieldModel,
    ConcurrencyModel,
    UnicefIdentifiedModel,
    AdminUrlMixin,
)


@dataclass
class ModifiedData:
    modified_date: datetime
    modified_by: Optional["User"] = None


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
        app_label = "payment"
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
        from hope.models.approval import Approval

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
        from hope.models.payment_verification_summary import PaymentVerificationSummary

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
