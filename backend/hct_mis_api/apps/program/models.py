from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from utils.models import TimeStampedUUIDModel


class Program(TimeStampedUUIDModel):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"
    STATUS_CHOICE = (
        (DRAFT, _("Draft")),
        (ACTIVE, _("Active")),
        (FINISHED, _("Finished")),
    )

    REGULAR = "REGULAR"
    ONE_OFF = "ONE_OFF"

    FREQUENCY_OF_PAYMENTS_CHOICE = (
        (REGULAR, _("Regular")),
        (ONE_OFF, _("One-off")),
    )

    CHILD_PROTECTION = "CHILD PROTECTION"
    EDUCATION = "EDUCATION"
    GENDER = "GENDER"
    HEALTH = "HEALTH"
    HIV_AIDS = "HIV_AIDS"
    MULTI_PURPOSE = "MULTI_PURPOSE"
    NUTRITION = "NUTRITION"
    SOCIAL_POLICY = "SOCIAL_POLICY"
    WASH = "WASH"

    SECTOR_CHOICE = (
        (CHILD_PROTECTION, _("Child Protection")),
        (EDUCATION, _("Education")),
        (GENDER, _("Gender")),
        (HEALTH, _("Health")),
        (HIV_AIDS, _("HIV / AIDS")),
        (MULTI_PURPOSE, _("Multi Purpose")),
        (NUTRITION, _("Nutrition")),
        (SOCIAL_POLICY, _("Social Policy")),
        (WASH, _("WASH")),
    )

    FULL = "FULL"
    PARTIAL = "PARTIAL"
    NO_INTEGRATION = "NO_INTEGRATION"
    SCOPE_CHOICE = (
        (FULL, _("Full")),
        (PARTIAL, _("Partial")),
        (NO_INTEGRATION, _("No Integration")),
    )

    name = models.CharField(max_length=255)
    status = models.CharField(max_length=255, choices=STATUS_CHOICE,)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.CharField(max_length=255)
    program_ca_id = models.CharField(max_length=255)
    locations = models.ManyToManyField(
        "core.Location", related_name="programs", blank=True
    )
    business_area = models.ForeignKey(
        "core.BusinessArea", on_delete=models.CASCADE
    )
    budget = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    frequency_of_payments = models.CharField(
        max_length=50, choices=FREQUENCY_OF_PAYMENTS_CHOICE,
    )
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICE,)
    scope = models.CharField(max_length=50, choices=SCOPE_CHOICE,)
    cash_plus = models.BooleanField()
    population_goal = models.PositiveIntegerField()
    administrative_areas_of_implementation = models.CharField(max_length=255)

    @property
    def total_number_of_households(self):
        return self.cash_plans.aggregate(
            households=Sum("number_of_households"),
        )["households"]


class CashPlan(TimeStampedUUIDModel):
    NOT_STARTED = "NOT_STARTED"
    STARTED = "STARTED"
    COMPLETE = "COMPLETE"

    STATUS_CHOICE = (
        (NOT_STARTED, _("NOT_STARTED")),
        (STARTED, _("STARTED")),
        ("COMPLETE", _("COMPLETE")),
    )

    program = models.ForeignKey(
        "Program", on_delete=models.CASCADE, related_name="cash_plans",
    )
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    disbursement_date = models.DateTimeField()
    number_of_households = models.PositiveIntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="cash_plans",
        null=True,
    )
    coverage_duration = models.PositiveIntegerField()
    coverage_units = models.CharField(max_length=255)
    target_population = models.ForeignKey(
        "targeting.TargetPopulation",
        on_delete=models.CASCADE,
        related_name="cash_plans",
    )
    cash_assist_id = models.CharField(max_length=255)
    distribution_modality = models.CharField(max_length=255)
    fsp = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICE)
    currency = models.CharField(max_length=255)
    total_entitled_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    total_delivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    total_undelivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    dispersion_date = models.DateField()
