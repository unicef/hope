import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING, Callable, List, Optional

from django.conf import settings
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models import Count, Q, QuerySet, Sum, UniqueConstraint
from django.db.models.functions import Coalesce
from django.utils import timezone

from dateutil.relativedelta import relativedelta
from django_fsm import FSMField, transition
from model_utils.models import SoftDeletableModel
from psycopg2._range import NumericRange

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES, USDC
from hct_mis_api.apps.core.exchange_rates import ExchangeRates
from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.household.models import FEMALE, MALE, Individual
from hct_mis_api.apps.payment.models.financial_service_provider_models import (
    FinancialServiceProvider,
)
from hct_mis_api.apps.payment.models.generic_payment_models import GenericPayment
from hct_mis_api.apps.payment.models.payment_acceptance_process_models import (
    AcceptanceProcessThreshold,
    Approval,
)
from hct_mis_api.apps.payment.models.payment_model import Payment
from hct_mis_api.apps.steficon.models import RuleCommit
from hct_mis_api.apps.utils.models import (
    AdminUrlMixin,
    ConcurrencyModel,
    InternalDataFieldModel,
    TimeStampedUUIDModel,
    UnicefIdentifiedModel,
)

if TYPE_CHECKING:
    from hct_mis_api.apps.account.models import User
    from hct_mis_api.apps.core.exchange_rates.api import ExchangeRateClient
    from hct_mis_api.apps.payment.models.payment_verification_models import (
        PaymentVerificationPlan,
    )
    from hct_mis_api.apps.program.models import Program

logger = logging.getLogger(__name__)


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
):
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

    program_cycle = models.ForeignKey("program.ProgramCycle", related_name="payment_plans", on_delete=models.CASCADE)
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
    is_cash_assist = models.BooleanField(default=False)

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
        from hct_mis_api.apps.payment.models.payment_verification_models import (
            PaymentVerificationSummary,
        )

        self.status_date = timezone.now()

        if not hasattr(self, "payment_verification_summary"):
            PaymentVerificationSummary.objects.create(payment_plan=self)

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
                Payment.STATUS_FORCE_FAILED,
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
    def program(self) -> "Program":
        return self.program_cycle.program

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

        qs = Payment.objects.filter(pk__in=payment_records)

        return qs

    @property
    def can_create_payment_verification_plan(self) -> int:
        return self.available_payment_records().count() > 0


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
