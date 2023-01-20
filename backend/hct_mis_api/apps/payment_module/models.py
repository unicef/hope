from decimal import Decimal
from typing import TYPE_CHECKING, Any, List, Optional

from django import forms
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_fsm import FSMField
from multiselectfield import MultiSelectField

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.core.field_attributes.core_fields_attributes import FieldFactory, Scope
from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES
from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.core.utils import map_unicef_ids_to_households_unicef_ids
from hct_mis_api.apps.steficon.models import RuleCommit
from hct_mis_api.apps.targeting.models import TargetingCriteria
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel, UnicefIdentifiedModel

if TYPE_CHECKING:
    from uuid import UUID


class PaymentCycle(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        NEW = "NEW", "New"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"

    title = models.CharField(max_length=255)
    program = models.ForeignKey("program.Program", null=True, on_delete=models.CASCADE, related_name="payment_cycles")
    start_date = models.DateField()
    end_date = models.DateField()
    female_children_count = models.PositiveSmallIntegerField(default=0)
    male_children_count = models.PositiveSmallIntegerField(default=0)
    female_adults_count = models.PositiveSmallIntegerField(default=0)
    male_adults_count = models.PositiveSmallIntegerField(default=0)
    total_households_count = models.PositiveSmallIntegerField(default=0)
    total_individuals_count = models.PositiveSmallIntegerField(default=0)
    status = FSMField(default=Status.NEW, protected=False, db_index=True, choices=Status.choices)
    total_entitled_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    total_entitled_quantity_usd = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    total_delivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    total_delivered_quantity_usd = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )

    @property
    def total_undelivered_quantity(self):
        return self.total_entitled_quantity - self.total_delivered_quantity

    @property
    def total_undelivered_quantity_usd(self):
        return self.total_entitled_quantity_usd - self.total_delivered_quantity_usd


class PaymentPlan(TimeStampedUUIDModel):
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
        ]
    )

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        LOCKED = "LOCKED", "Locked"
        IN_APPROVAL = "IN_APPROVAL", "In Approval"
        APPROVED = "APPROVED", "Approved"
        ONGOING = "ONGOING", "Ongoing"
        RECONCILED = "RECONCILED", "Reconciled"

    class BackgroundActionStatus(models.TextChoices):
        TARGETING_BUILDING = "TARGETING_BUILDING", "Targeting building"
        STEFICON_RUN = "STEFICON_RUN", "Rule Engine Running"
        STEFICON_ERROR = "STEFICON_ERROR", "Rule Engine Errored"
        XLSX_EXPORTING = "XLSX_EXPORTING", "Exporting XLSX file"
        XLSX_EXPORT_ERROR = "XLSX_EXPORT_ERROR", "Export XLSX file Error"
        XLSX_IMPORT_ERROR = "XLSX_IMPORT_ERROR", "Import XLSX file Error"
        XLSX_IMPORTING_ENTITLEMENTS = "XLSX_IMPORTING_ENTITLEMENTS", "Importing Entitlements XLSX file"
        XLSX_IMPORTING_RECONCILIATION = "XLSX_IMPORTING_RECONCILIATION", "Importing Reconciliation XLSX file"

    class PaymentPlanType(models.TextChoices):
        HOUSEHOLD = "HOUSEHOLD", "Household"
        INDIVIDUAL = "INDIVIDUAL", "Individual"

    BACKGROUND_ACTION_ERROR_STATES = [
        BackgroundActionStatus.XLSX_EXPORT_ERROR,
        BackgroundActionStatus.XLSX_IMPORT_ERROR,
        BackgroundActionStatus.STEFICON_ERROR,
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

    payment_cycle = models.ForeignKey(
        "payment_module.PaymentCycle",
        on_delete=models.CASCADE,
        related_name="payment_plans",
        null=True,
        blank=True,
    )
    plan_type = models.CharField(max_length=20, choices=PaymentPlanType.choices)

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

    female_children_count = models.PositiveSmallIntegerField(default=0)
    male_children_count = models.PositiveSmallIntegerField(default=0)
    female_adults_count = models.PositiveSmallIntegerField(default=0)
    male_adults_count = models.PositiveSmallIntegerField(default=0)
    total_households_count = models.PositiveSmallIntegerField(default=0)
    total_individuals_count = models.PositiveSmallIntegerField(default=0)
    maximum_entitlement_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    minimum_entitlement_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    avg_entitlement_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    median_entitlement_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    maximum_entitlement_quantity_usd = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    minimum_entitlement_quantity_usd = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    avg_entitlement_quantity_usd = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    median_entitlement_quantity_usd = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    total_entitled_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    total_delivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    total_entitled_quantity_usd = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    total_delivered_quantity_usd = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    imported_entitlement_file_date = models.DateTimeField(blank=True, null=True)
    imported_entitlement_file = models.ForeignKey(
        FileTemp, null=True, blank=True, related_name="+", on_delete=models.SET_NULL
    )
    exported_entitlement_file = models.ForeignKey(
        FileTemp, null=True, blank=True, related_name="+", on_delete=models.SET_NULL
    )
    rule_engine_rule_commit = models.ForeignKey(
        RuleCommit,
        null=True,
        on_delete=models.PROTECT,
        related_name="payment_plans",
        blank=True,
    )
    rule_engine_applied_date = models.DateTimeField(blank=True, null=True)
    excluded_ids = models.ArrayField(models.CharField(max_length=255), blank=True, default=list)

    # TODO: total number of payments
    # and reconciled

    delivered_fully = models.PositiveIntegerField(default=0)
    delivered_partially = models.PositiveIntegerField(default=0)
    not_delivered = models.PositiveIntegerField(default=0)
    failed = models.PositiveIntegerField(default=0)
    pending = models.PositiveIntegerField(default=0)


class PaymentPlanTargetingCriteria(TargetingCriteria):
    """
    Proxy model for TargetingCriteria to be used in PaymentPlan
    """

    class Meta:
        proxy = True

    def get_excluded_household_ids(self) -> List["UUID"]:
        return map_unicef_ids_to_households_unicef_ids(self.payment_plan.excluded_ids)


class PaymentInstructionTargetingCriteria(TargetingCriteria):
    """
    Proxy model for TargetingCriteria to be used in PaymentInstruction
    """

    class Meta:
        proxy = True

    def get_excluded_household_ids(self) -> List["UUID"]:
        return map_unicef_ids_to_households_unicef_ids(self.payment_instruction.excluded_ids)


class PaymentInstruction(TimeStampedUUIDModel):
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

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        AUTHORIZED = "AUTHORIZED", _("Authorized")
        RELEASED = "RELEASED", _("Released")

    payment_plan = models.ForeignKey(
        "payment_module.PaymentPlan", on_delete=models.CASCADE, related_name="payment_instructions"
    )
    fsp = models.ForeignKey(
        "payment_module.FinancialServiceProvider", on_delete=models.CASCADE, related_name="payment_instructions"
    )
    delivery_mechanism = models.CharField(max_length=255, choices=DELIVERY_TYPE_CHOICE, db_index=True, null=True)
    status = FSMField(default=Status.PENDING, protected=False, db_index=True)
    targeting_criteria = models.OneToOneField(
        "PaymentInstructionTargetingCriteria",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="payment_instruction",
    )

    total = models.PositiveBigIntegerField(default=0)
    correct = models.PositiveBigIntegerField(default=0)
    missing = models.PositiveBigIntegerField(default=0)

    total_entitled_quantity = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_entitled_quantity_usd = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    class Meta:
        unique_together = ("fsp", "delivery_mechanism")


class PaymentList(TimeStampedUUIDModel):
    payment_instruction = models.ForeignKey(
        "payment_module.PaymentInstruction", on_delete=models.CASCADE, related_name="payment_lists"
    )
    count = models.PositiveIntegerField(default=0)


class Payment(TimeStampedUUIDModel, UnicefIdentifiedModel):
    class EntitlementType(models.TextChoices):
        CASH = "RULE_ENGINE", _("Rule Engine")
        XLSX = "XLSX", _("XLSX")

    payment_plan = models.ForeignKey("payment_module.PaymentPlan", on_delete=models.CASCADE, related_name="payments")
    payment_list = models.ForeignKey("payment_module.PaymentList", on_delete=models.CASCADE, related_name="payments")
    payment_instruction = models.ForeignKey(
        "payment_module.PaymentInstruction", on_delete=models.CASCADE, related_name="payments"
    )
    household = models.ForeignKey("household.Household", on_delete=models.CASCADE, related_name="payments")
    entitlement_type = models.CharField(max_length=50, choices=EntitlementType.choices, db_index=True)

    entitlement_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    entitlement_quantity_usd = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    delivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )
    delivered_quantity_usd = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.00"))],
        default="0.00",
    )


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
    fsp_xlsx_template = models.ForeignKey(
        "payment_module.FinancialServiceProviderXlsxTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("XLSX Template"),
    )

    def __str__(self) -> str:
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
        "payment_module.FinancialServiceProvider",
        on_delete=models.CASCADE,
        verbose_name=_("Financial Service Provider"),
    )
    file = models.FileField(blank=True, null=True, editable=False)
    status = models.IntegerField(choices=STATUSES, blank=True, null=True, editable=False, db_index=True)

    def __str__(self) -> str:
        return f"{self.template.name} ({self.status})"


class FinancialServiceProviderXlsxTemplate(TimeStampedUUIDModel):
    # TODO: add/remove fields after finalizing the fields
    # after updating COLUMNS_TO_CHOOSE please update XlsxPaymentPlanExportService.export_per_fsp as well
    COLUMNS_TO_CHOOSE = (
        ("payment_id", _("Payment ID")),
        ("household_id", _("Household ID")),
        ("admin_leve_2", _("Admin Level 2")),
        ("collector_name", _("Collector Name")),
        ("payment_channel", _("Payment Channel (Delivery mechanism)")),
        ("fsp_name", _("FSP Name")),
        ("entitlement_quantity", _("Entitlement Quantity")),
        ("delivered_quantity", _("Delivered Quantity")),
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
        "delivered_quantity",
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

    def __str__(self) -> str:
        return f"{self.name} ({len(self.columns)})"


class AuthorizationProcess(TimeStampedUUIDModel):
    payment_instruction = models.ForeignKey(
        "payment_module.PaymentInstruction",
        on_delete=models.CASCADE,
        related_name="authorization_processes",
    )


class Authorization(TimeStampedUUIDModel):
    AUTHORIZATION = "AUTHORIZATION"
    RELEASE = "RELEASE"
    REJECT_AUTH = "REJECT_AUTH"
    REJECT_RELEASE = "REJECT_RELEASE"
    TYPE_CHOICES = (
        (AUTHORIZATION, "Authorization"),
        (RELEASE, "Release"),
        (REJECT_AUTH, "Reject Authorization"),
        (REJECT_RELEASE, "Reject Release"),
    )

    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default=REJECT_AUTH, verbose_name=_("Approval type"))
    comment = models.CharField(max_length=500, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    authorization_process = models.ForeignKey(
        AuthorizationProcess, on_delete=models.CASCADE, related_name="authorizations"
    )


class ChoiceArrayFieldDeliveryMechanism(ArrayField):
    def formfield(self, form_class: Optional[Any] = ..., choices_form_class: Optional[Any] = ..., **kwargs: Any) -> Any:
        defaults = {
            "form_class": forms.TypedMultipleChoiceField,
            "choices": self.base_field.choices,
            "coerce": self.base_field.to_python,
            "widget": forms.SelectMultiple,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


class FspDeliveryMechanism(TimeStampedUUIDModel):
    financial_service_provider = models.ForeignKey(
        FinancialServiceProvider, on_delete=models.CASCADE, related_name="fsp_delivery_mechanisms"
    )
    delivery_mechanism = models.CharField(
        max_length=255, choices=PaymentInstruction.DELIVERY_TYPE_CHOICE, db_index=True, null=True
    )

    global_core_fields = ChoiceArrayFieldDeliveryMechanism(
        models.CharField(max_length=255, blank=True, choices=FieldFactory.from_scope(Scope.GLOBAL).to_choices()),
        default=list,
    )
    # TODO: flex fields
    # TODO: payment plan scope fields

    class Meta:
        unique_together = ("financial_service_provider", "delivery_mechanism")
