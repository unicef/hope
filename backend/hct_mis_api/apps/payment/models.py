import logging
from datetime import datetime
from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Union

from django import forms
from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField, IntegerRangeField
from django.contrib.postgres.validators import RangeMinValueValidator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
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
from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES
from hct_mis_api.apps.core.exchange_rates import ExchangeRates
from hct_mis_api.apps.core.field_attributes.core_fields_attributes import (
    CORE_FIELDS_ATTRIBUTES,
    FieldFactory,
)
from hct_mis_api.apps.core.field_attributes.fields_types import _HOUSEHOLD, _INDIVIDUAL
from hct_mis_api.apps.core.models import BusinessArea, FileTemp
from hct_mis_api.apps.core.utils import nested_getattr
from hct_mis_api.apps.household.models import FEMALE, MALE, Individual
from hct_mis_api.apps.payment.managers import PaymentManager
from hct_mis_api.apps.steficon.models import RuleCommit
from hct_mis_api.apps.utils.models import (
    ConcurrencyModel,
    TimeStampedUUIDModel,
    UnicefIdentifiedModel,
)

if TYPE_CHECKING:
    from hct_mis_api.apps.account.models import User
    from hct_mis_api.apps.core.exchange_rates.api import ExchangeRateClient

logger = logging.getLogger(__name__)


class ChoiceArrayFieldDM(ArrayField):
    def formfield(self, form_class: Optional[Any] = ..., choices_form_class: Optional[Any] = ..., **kwargs: Any) -> Any:
        defaults = {
            "form_class": forms.TypedMultipleChoiceField,
            "choices": self.base_field.choices,
            "coerce": self.base_field.to_python,
            "widget": forms.SelectMultiple,
        }
        defaults.update(kwargs)

        return super(ArrayField, self).formfield(**defaults)


class GenericPaymentPlan(TimeStampedUUIDModel):
    usd_fields = [
        "total_entitled_quantity_usd",
        "total_entitled_quantity_revised_usd",
        "total_delivered_quantity_usd",
        "total_undelivered_quantity_usd",
    ]

    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    status_date = models.DateTimeField()
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(db_index=True)
    program = models.ForeignKey("program.Program", on_delete=models.CASCADE)
    exchange_rate = models.DecimalField(decimal_places=8, blank=True, null=True, max_digits=14)

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

    @property
    def get_unicef_id(self) -> str:
        # TODO: MB 'ca_id' rename to 'unicef_id'?
        return self.ca_id if isinstance(self, CashPlan) else self.unicef_id

    def get_exchange_rate(self, exchange_rates_client: Optional["ExchangeRateClient"] = None) -> float:
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

    STATUS_CHOICE = (
        (STATUS_DISTRIBUTION_SUCCESS, _("Distribution Successful")),
        (STATUS_NOT_DISTRIBUTED, _("Not Distributed")),
        (STATUS_SUCCESS, _("Transaction Successful")),
        (STATUS_ERROR, _("Transaction Erroneous")),
        (STATUS_FORCE_FAILED, _("Force failed")),
        (STATUS_DISTRIBUTION_PARTIAL, _("Partially Distributed")),
        (STATUS_PENDING, _("Pending")),
    )

    ALLOW_CREATE_VERIFICATION = (STATUS_SUCCESS, STATUS_DISTRIBUTION_SUCCESS, STATUS_DISTRIBUTION_PARTIAL)

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
        default=STATUS_PENDING,
    )
    status_date = models.DateTimeField()
    household = models.ForeignKey("household.Household", on_delete=models.CASCADE)
    head_of_household = models.ForeignKey("household.Individual", on_delete=models.CASCADE, null=True)
    delivery_type = models.CharField(choices=DELIVERY_TYPE_CHOICE, max_length=24, null=True)
    currency = models.CharField(
        max_length=4,
    )
    entitlement_quantity = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.00"))], null=True
    )
    entitlement_quantity_usd = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.00"))], null=True
    )
    delivered_quantity = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.00"))], null=True
    )
    delivered_quantity_usd = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal("0.00"))], null=True
    )
    delivery_date = models.DateTimeField(null=True, blank=True)
    transaction_reference_id = models.CharField(max_length=255, null=True)  # transaction_id

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


class PaymentPlan(SoftDeletableModel, GenericPaymentPlan, UnicefIdentifiedModel):
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

    BACKGROUND_ACTION_ERROR_STATES = [
        BackgroundActionStatus.XLSX_EXPORT_ERROR,
        BackgroundActionStatus.XLSX_IMPORT_ERROR,
        BackgroundActionStatus.RULE_ENGINE_ERROR,
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

    program_cycle = models.ForeignKey("program.ProgramCycle", null=True, blank=True, on_delete=models.CASCADE)
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

    class Meta:
        verbose_name = "Payment Plan"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return self.unicef_id or ""

    @property
    def bank_reconciliation_success(self) -> int:
        return self.payment_items.filter(status__in=Payment.ALLOW_CREATE_VERIFICATION).count()

    @property
    def bank_reconciliation_error(self) -> int:
        return self.payment_items.filter(status=Payment.STATUS_ERROR).count()

    @property
    def excluded_households_ids(self) -> List[str]:
        return list(self.payment_items.filter(excluded=True).values_list("household__unicef_id", flat=True))

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
        source=BackgroundActionStatus.XLSX_EXPORTING,
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
        source=[BackgroundActionStatus.RULE_ENGINE_RUN],
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
        return self.payment_items.filter(payment_plan_hard_conflicted=False).exists()

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
        try:
            if self.status == PaymentPlan.Status.LOCKED and not self.is_follow_up:
                return self.export_file_entitlement is not None
            elif self.status in (PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED):
                return self.export_file_per_fsp is not None
            else:
                return False
        except FileTemp.DoesNotExist:
            return False

    @property
    def payment_list_export_file_link(self) -> Optional[str]:
        if self.status == PaymentPlan.Status.LOCKED and not self.is_follow_up:
            return self.export_file_entitlement.file.url
        elif self.status in (PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED):
            return self.export_file_per_fsp.file.url
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
        return (
            self.eligible_payments.exclude(status=GenericPayment.STATUS_PENDING).count()
            == self.eligible_payments.count()
        )

    def remove_export_file(self) -> None:
        # remove export_file_entitlement
        if self.status == PaymentPlan.Status.LOCKED and self.export_file_entitlement:
            self.export_file_entitlement.file.delete(save=False)
            self.export_file_entitlement.delete()
            self.export_file_entitlement = None
        # remove export_file_per_fsp
        if self.status in (PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED) and self.export_file_per_fsp:
            self.export_file_per_fsp.file.delete(save=False)
            self.export_file_per_fsp.delete()
            self.export_file_per_fsp = None

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
        return self.payment_items.eligible().filter(
            status__in=[
                Payment.STATUS_ERROR,
                Payment.STATUS_NOT_DISTRIBUTED,
                Payment.STATUS_FORCE_FAILED,  # TODO remove force failed?
            ]
        )

    def payments_used_in_follow_payment_plans(self) -> "QuerySet":
        return Payment.objects.filter(parent__source_payment_plan_id=self.id, excluded=False)


class FinancialServiceProviderXlsxTemplate(TimeStampedUUIDModel):
    COLUMNS_CHOICES = (
        ("payment_id", _("Payment ID")),
        ("household_id", _("Household ID")),
        ("household_size", _("Household Size")),
        ("collector_name", _("Collector Name")),
        ("payment_channel", _("Payment Channel")),
        ("fsp_name", _("FSP Name")),
        ("currency", _("Currency")),
        ("entitlement_quantity", _("Entitlement Quantity")),
        ("entitlement_quantity_usd", _("Entitlement Quantity USD")),
        ("delivered_quantity", _("Delivered Quantity")),
        ("delivery_date", _("Delivery Date")),
        ("reason_for_unsuccessful_payment", _("Reason for unsuccessful payment")),
        ("order_number", _("Order Number")),
        ("token_number", _("Token Number")),
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
        max_length=250,
        choices=COLUMNS_CHOICES,
        default=DEFAULT_COLUMNS,
        verbose_name=_("Columns"),
        help_text=_("Select the columns to include in the report"),
    )

    core_fields = HorizontalChoiceArrayField(
        models.CharField(max_length=255, blank=True, choices=FieldFactory(CORE_FIELDS_ATTRIBUTES).to_choices()),
        default=list,
        blank=True,
    )

    @classmethod
    def get_column_from_core_field(cls, payment: "Payment", core_field_name: str) -> Any:
        collector = payment.collector
        household = payment.household
        core_fields_attributes = FieldFactory(CORE_FIELDS_ATTRIBUTES).to_dict_by("name")
        attr = core_fields_attributes[core_field_name]
        lookup = attr["lookup"]
        lookup = lookup.replace("__", ".")
        if attr["associated_with"] == _INDIVIDUAL:
            return nested_getattr(collector, lookup, None)
        if attr["associated_with"] == _HOUSEHOLD:
            return nested_getattr(household, lookup, None)
        return None

    @classmethod
    def get_column_value_from_payment(cls, payment: "Payment", column_name: str) -> Union[str, float]:
        map_obj_name_column = {
            "payment_id": (payment, "unicef_id"),
            "household_id": (payment.household, "unicef_id"),
            "household_size": (payment.household, "size"),
            "admin_level_2": (payment.household.admin2, "name"),
            "collector_name": (payment.collector, "full_name"),
            "payment_channel": (payment, "delivery_type"),
            "fsp_name": (payment.financial_service_provider, "name"),
            "currency": (payment, "currency"),
            "entitlement_quantity": (payment, "entitlement_quantity"),
            "entitlement_quantity_usd": (payment, "entitlement_quantity_usd"),
            "delivered_quantity": (payment, "delivered_quantity"),
            "delivery_date": (payment, "delivery_date"),
            "reason_for_unsuccessful_payment": (payment, "reason_for_unsuccessful_payment"),
            "order_number": (payment, "order_number"),
            "token_number": (payment, "token_number"),
        }
        if column_name not in map_obj_name_column:
            return "wrong_column_name"
        if column_name == "delivered_quantity" and payment.status == Payment.STATUS_ERROR:  # Unsuccessful Payment
            return float(-1)
        if column_name == "delivery_date" and payment.delivery_date is not None:
            return str(payment.delivery_date)
        obj, nested_field = map_obj_name_column[column_name]
        return getattr(obj, nested_field, None) or ""

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
    delivery_mechanism = models.CharField(
        max_length=255, verbose_name=_("Delivery Mechanism"), choices=GenericPayment.DELIVERY_TYPE_CHOICE
    )
    xlsx_template = models.ForeignKey(
        "FinancialServiceProviderXlsxTemplate",
        on_delete=models.CASCADE,
        related_name="fsp_xlsx_template_per_delivery_mechanisms",
    )

    class Meta:
        unique_together = ("financial_service_provider", "delivery_mechanism")

    def __str__(self) -> str:
        return f"{self.financial_service_provider.name} - {self.xlsx_template} - {self.delivery_mechanism}"


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
    delivery_mechanisms = HorizontalChoiceArrayField(
        models.CharField(choices=GenericPayment.DELIVERY_TYPE_CHOICE, max_length=24)
    )
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
        "payment.FinancialServiceProvider",
        on_delete=models.CASCADE,
        verbose_name=_("Financial Service Provider"),
    )
    file = models.FileField(blank=True, null=True, editable=False)
    status = models.IntegerField(choices=STATUSES, blank=True, null=True, editable=False, db_index=True)

    def __str__(self) -> str:
        name_ = (
            self.financial_service_provider.fsp_xlsx_template.name
            if self.financial_service_provider.fsp_xlsx_template
            else self.financial_service_provider.name
        )
        return f"{name_} ({self.status})"


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
    delivery_mechanism = models.CharField(
        max_length=255, choices=GenericPayment.DELIVERY_TYPE_CHOICE, db_index=True, null=True
    )
    delivery_mechanism_order = models.PositiveIntegerField()

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
    payment_verification_summary = GenericRelation(
        "payment.PaymentVerificationSummary",
        content_type_field="payment_content_type",
        object_id_field="payment_object_id",
        related_query_name="payment_record",
    )

    @property
    def unicef_id(self) -> str:
        return self.ca_id

    def get_revert_mark_as_failed_status(self, delivered_quantity: Decimal) -> str:
        return self.STATUS_SUCCESS


class Payment(SoftDeletableModel, GenericPayment, UnicefIdentifiedModel):
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
    payment_verification_summary = GenericRelation(
        "payment.PaymentVerificationSummary",
        content_type_field="payment_content_type",
        object_id_field="payment_object_id",
        related_query_name="payment",
    )

    source_payment = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="follow_ups"
    )
    is_follow_up = models.BooleanField(default=False)
    reason_for_unsuccessful_payment = models.CharField(max_length=255, null=True, blank=True)
    order_number = models.PositiveIntegerField(
        blank=True, null=True, validators=[MinValueValidator(100000000), MaxValueValidator(999999999)]
    )  # 9 digits
    token_number = models.PositiveIntegerField(
        blank=True, null=True, validators=[MinValueValidator(1000000), MaxValueValidator(9999999)]
    )  # 7 digits

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

    def clean(self) -> None:
        if self.parent.status in (PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED):
            # Check for existing Payment objects with the same token_number and the same Program
            existing_payments = Payment.objects.filter(
                parent__program=self.parent.program,
                token_number=self.token_number,
            )
            if self.pk:
                existing_payments = existing_payments.exclude(pk=self.pk)
            if existing_payments.exists():
                raise ValidationError("Token number must be unique per Program.")

            # Check for existing Payment objects with the same order_number and the same Program
            existing_payments = Payment.objects.filter(
                parent__program=self.parent.program,
                order_number=self.order_number,
            )
            if self.pk:
                existing_payments = existing_payments.exclude(pk=self.pk)
            if existing_payments.exists():
                raise ValidationError("Order number must be unique per Program.")

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["parent", "household"],
                condition=Q(is_removed=False),
                name="payment_plan_and_household",
            ),
        ]


class ServiceProvider(TimeStampedUUIDModel):
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    ca_id = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, null=True)
    short_name = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=3)
    vision_id = models.CharField(max_length=255, null=True)

    def __str__(self) -> str:
        return self.full_name or ""


class PaymentVerificationPlan(TimeStampedUUIDModel, ConcurrencyModel, UnicefIdentifiedModel):
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
    payment_plan_obj: "Union[PaymentPlan, CashPlan]" = GenericForeignKey("payment_plan_content_type", "payment_plan_object_id")  # type: ignore
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
            return self.payment_plan_content_type.model_class().objects.get(pk=self.payment_plan_object_id)
        except ObjectDoesNotExist:
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


class PaymentVerification(TimeStampedUUIDModel, ConcurrencyModel):
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
