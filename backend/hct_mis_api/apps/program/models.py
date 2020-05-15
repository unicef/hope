from decimal import Decimal

from auditlog.models import AuditlogHistoryField
from django.conf import settings
from django.core.validators import (
    MinValueValidator,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.db import models
from django.db.models import Sum, UUIDField
from django.db.models.functions import Coalesce
from django.utils.translation import ugettext_lazy as _

from utils.models import TimeStampedUUIDModel
from auditlog.registry import auditlog


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

    CHILD_PROTECTION = "CHILD_PROTECTION"
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

    name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICE,)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    program_ca_id = models.CharField(max_length=255)
    admin_areas = models.ManyToManyField(
        "core.AdminArea", related_name="programs", blank=True,
    )
    business_area = models.ForeignKey(
        "core.BusinessArea", on_delete=models.CASCADE
    )
    budget = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    frequency_of_payments = models.CharField(
        max_length=50, choices=FREQUENCY_OF_PAYMENTS_CHOICE,
    )
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICE,)
    scope = models.CharField(max_length=50, choices=SCOPE_CHOICE,)
    cash_plus = models.BooleanField()
    population_goal = models.PositiveIntegerField()
    administrative_areas_of_implementation = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    history = AuditlogHistoryField(pk_indexable=False)

    @property
    def total_number_of_households(self):
        return self.cash_plans.aggregate(
            households=Coalesce(Sum("number_of_households"), 0),
        )["households"]

    class Meta:
        unique_together = ("name", "business_area")


class CashPlan(TimeStampedUUIDModel):
    business_area = models.ForeignKey(
        "core.BusinessArea", on_delete=models.CASCADE
    )
    ca_id = models.CharField(max_length=255)
    ca_hash_id = UUIDField(primary_key=True, version=4,)
    status = models.CharField(
        max_length=255,
        choices=(
            ("Distribution Completed", "Distribution Completed"),
            (
                "Distribution Completed with Errors",
                "Distribution Completed with Errors",
            ),
            ("Transaction Completed", "Transaction Completed"),
            (
                "Transaction Completed with Errors",
                "Transaction Completed with Errors",
            ),
        ),
    )
    status_date = models.DateTimeField()
    name = models.CharField(max_length=255)
    distribution_level = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    dispersion_date = models.DateTimeField()
    coverage_duration = models.PositiveIntegerField()
    coverage_unit = models.CharField(max_length=255)
    comments = models.CharField(max_length=255)
    program = models.ForeignKey(
        "program.Program", on_delete=models.CASCADE, related_name="cash_plans"
    )
    delivery_type = models.CharField(max_length=255)
    assistance_measurement = models.CharField(max_length=255)
    assistance_through = models.CharField(max_length=255)
    vision_id = models.CharField(max_length=255)
    funds_commitment = models.CharField(max_length=255)
    down_payment = models.CharField(max_length=255)
    validation_alerts_count = models.IntegerField()
    total_persons_covered = models.IntegerField()
    total_persons_covered_revised = models.IntegerField()
    payment_records_count = models.IntegerField()
    total_entitled_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    total_entitled_quantity_revised = models.DecimalField(
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


auditlog.register(Program)
