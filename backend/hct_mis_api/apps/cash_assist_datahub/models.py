from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from model_utils import Choices
from model_utils.fields import UUIDField
from model_utils.models import UUIDModel

from household.models import (
    RELATIONSHIP_CHOICE,
    ROLE_CHOICE,
    MARITAL_STATUS_CHOICE,
)
from utils.models import TimeStampedUUIDModel


class Session(models.Model):
    timestamp = models.DateTimeField()
    source = models.CharField(
        max_length=3, choices=(("MIS", "HCT-MIS"), ("CA", "Cash Assist")),
    )
    status = models.CharField(
        max_length=11,
        choices=(
            ("NEW", "New"),
            ("READY", "Ready"),
            ("PROCESSING", "Processing"),
            ("COMPLETED", "Completed"),
            ("FAILED", "Failed"),
        ),
    )
    last_modified_date = models.DateTimeField(auto_now=True)


class SessionModel(models.Model):
    last_sync_on = models.DateTimeField(null=True)
    session_id = models.ForeignKey("cash_assist_datahub.Session",on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Household(SessionModel):
    household_id = UUIDField(primary_key=True, version=4,)
    status = models.CharField(
        max_length=50, choices=(("INACTIVE", "Inactive"), ("ACTIVE", "Active")),
    )
    household_size = models.PositiveIntegerField()
    # head of household document id
    government_form_number = models.CharField(max_length=255, blank=True)
    # registration household id
    form_number = models.CharField(max_length=255, blank=True)
    agency_id = models.CharField(max_length=255, blank=True)
    #  individual_id head of household
    focal_point = models.ForeignKey(
        "cash_assist_datahub.Individual",
        db_column="focal_point",
        on_delete=models.CASCADE,
    )
    address = models.CharField(max_length=255, blank=True)
    admin1 = models.CharField(max_length=255, blank=True)
    admin2 = models.CharField(max_length=255, blank=True)
    country = CountryField(blank=True)


class Individual(SessionModel):
    individual_id = UUIDField(primary_key=True, version=4,)
    household = models.ForeignKey(
        "cash_assist_datahub.Household",
        db_column="household_id",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=50,
        choices=(("INACTIVE", "Inactive"), ("ACTIVE", "Active")),
        blank=True,
    )
    SEX_CHOICE = (
        ("MALE", _("Male")),
        ("FEMALE", _("Female")),
    )
    full_name = models.CharField(max_length=255)
    family_name = models.CharField(max_length=255, blank=True)
    given_name = models.CharField(max_length=255, blank=True)
    middle_name = models.CharField(max_length=255, blank=True)
    sex = models.CharField(max_length=255, choices=SEX_CHOICE,)
    date_of_birth = models.DateField()
    estimated_date_of_birth = models.BooleanField()
    relationship = models.CharField(
        max_length=255, blank=True, choices=RELATIONSHIP_CHOICE,
    )
    role = models.CharField(max_length=255, blank=True, choices=ROLE_CHOICE,)
    marital_status = models.CharField(
        max_length=255, choices=MARITAL_STATUS_CHOICE,
    )
    phone_number = models.CharField(max_length=14, blank=True)

    def __str__(self):
        return self.family_name


class TargetPopulation(SessionModel):
    tp_unicef_id = UUIDField(primary_key=True, version=4,)
    name = models.CharField(max_length=255)
    population_type = models.CharField(default="HOUSEHOLD")
    targeting_criteria = models.TextField()

    active_households = models.PositiveIntegerField(default=0)
    inactive_households = models.PositiveIntegerField(default=0)
    program = models.ForeignKey(
        "cash_assist_datahub.Program",
        db_column="program_id",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class TargetPopulationEntries(SessionModel):
    target_population = models.ForeignKey(
        "cash_assist_datahub.TargetPopulation", on_delete=models.CASCADE,
    )
    household = models.ForeignKey(
        "cash_assist_datahub.Household", on_delete=models.CASCADE, null=True
    )
    individual = models.ForeignKey(
        "cash_assist_datahub.Individual", on_delete=models.CASCADE, null=True
    )
    unhcr_household_id = models.CharField(max_length=255)


class Program(SessionModel):
    program_id = UUIDField(primary_key=True, version=4,)
    business_area = models.CharField(max_length=20)
    STATUS_CHOICE = (
        ("NOT_STARTED", _("NOT_STARTED")),
        ("STARTED", _("STARTED")),
        ("COMPLETE", _("COMPLETE")),
    )
    SCOPE_CHOICE = (
        ("FULL", _("Full")),
        ("PARTIAL", _("Partial")),
        ("NO_INTEGRATION", _("No Integration")),
    )
    program_unhcr_id = models.CharField(max_length=255)
    program_hash_id = models.CharField(max_length=255)
    programme_name = models.CharField(max_length=255)
    scope = models.PositiveIntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.CharField(max_length=255, blank=True)


class CashPlan(TimeStampedUUIDModel):
    program = models.ForeignKey(
        "Program", on_delete=models.CASCADE, related_name="cash_plans"
    )
    cash_assist_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    distribution_level = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    dispersion_date = models.DateTimeField()
    coverage_date = models.DateTimeField(auto_now_add=True)
    coverage_duration = models.PositiveIntegerField()
    coverage_unit = models.CharField(max_length=255)
    program_ca_id = models.CharField(max_length=255)


class PaymentRecord(TimeStampedUUIDModel):
    STATUS_CHOICE = (
        ("SUCCESS", _("Sucess")),
        ("PENDING", _("Pending")),
        ("ERROR", _("Error")),
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICE,)
    name = models.CharField(max_length=255)
    status_date = models.DateTimeField()
    cash_assist_id = models.CharField(max_length=255)
    cash_plan = models.ForeignKey(
        "CashPlan", on_delete=models.CASCADE, related_name="payment_records",
    )

    household = models.ForeignKey(
        "Household", on_delete=models.CASCADE, related_name="payment_records",
    )
    head_of_household = models.CharField(max_length=255)
    total_person_covered = models.PositiveIntegerField()

    distribution_modality = models.CharField(max_length=255,)

    target_population = models.ForeignKey(
        "TargetPopulation",
        related_name="payment_records",
        on_delete=models.CASCADE,
    )
    entitlement = models.OneToOneField(
        "PaymentEntitlement",
        on_delete=models.SET_NULL,
        related_name="payment_record",
        null=True,
    )


class PaymentEntitlement(TimeStampedUUIDModel):
    DELIVERY_TYPE_CHOICE = (
        ("CASH", _("Cash")),
        ("DEPOSIT_TO_CARD", _("Deposit to Card")),
        ("TRANSFER", _("Transfer")),
    )
    delivery_type = models.CharField(
        max_length=255, choices=DELIVERY_TYPE_CHOICE,
    )
    entitlement_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    delivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    entitlement_card_issue_date = models.DateTimeField(blank=True, null=True)
    entitlement_card_number = models.CharField(
        max_length=255, choices=DELIVERY_TYPE_CHOICE,
    )
    currency = models.CharField(max_length=255)
    delivery_date = models.DateTimeField(blank=True, null=True)
    transaction_reference_id = models.CharField(max_length=255)
    fsp = models.CharField(max_length=255)


class EntitlementCard(TimeStampedUUIDModel):
    STATUS_CHOICE = Choices(
        ("ACTIVE", _("Active")),
        ("ERRONEOUS", _("Erroneous")),
        ("CLOSED", _("Closed")),
    )
    card_number = models.CharField(max_length=255)
    status = models.CharField(
        choices=STATUS_CHOICE, default=STATUS_CHOICE.ACTIVE, max_length=10,
    )
    card_type = models.CharField(max_length=255)
    current_card_size = models.CharField(max_length=255)
    card_custodian = models.CharField(max_length=255)
    service_provider = models.CharField(max_length=255)
    household = models.ForeignKey(
        "Household",
        related_name="entitlement_cards",
        on_delete=models.SET_NULL,
        null=True,
    )
