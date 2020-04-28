from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from model_utils import Choices

from hct_mis_api.apps.utils.models import TimeStampedUUIDModel


# TODO THIS MODELS MUST BE CHANGED

class Household(TimeStampedUUIDModel):
    # TODO Get correct RECEPTION_TYPE_CHOICE
    RECEPTION_TYPE_CHOICE = (
        ("REFUGEE", _("Refugee")),
        ("MIGRANT", _("Migrant")),
        ("CITIZEN", _("Citizen")),
        ("IDP", _("IDP")),
        ("OTHER", _("Other")),
    )

    household_ca_id = models.CharField(max_length=255)
    reception_type = models.CharField(
        max_length=255, choices=RECEPTION_TYPE_CHOICE,
    )
    family_name = models.CharField(max_length=255)
    household_size = models.PositiveIntegerField(blank=True, null=True)
    has_demographic_breakdown = models.BooleanField()

    def __str__(self):
        return self.family_name


class Individual(TimeStampedUUIDModel):
    SEX_CHOICE = (
        ("MALE", _("Male")),
        ("FEMALE", _("Female")),
        ("OTHER", _("Other")),
    )

    household = models.ForeignKey(
        "Household", related_name="individuals", on_delete=models.CASCADE
    )
    individual_ca_id = models.CharField(max_length=255)
    family_name = models.CharField(max_length=255)
    sex = models.CharField(max_length=255, choices=SEX_CHOICE,)
    date_of_birth = models.DateField(blank=True, null=True)
    estimated_date_of_birth = models.DateField(blank=True, null=True)
    country_of_origin = CountryField()

    def __str__(self):
        return self.family_name


class TargetPopulation(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    population_type = models.PositiveIntegerField()
    description = models.CharField(max_length=255, blank=True)
    target_type = models.CharField(max_length=255)
    households = models.ManyToManyField(
        "Household", related_name="target_populations"
    )

    def __str__(self):
        return self.name


class Program(TimeStampedUUIDModel):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    STATUS_CHOICE = (
        (ACTIVE, _("In progress")),
        (COMPLETED, _("Done")),
    )
    program_ca_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
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
