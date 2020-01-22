from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField

from hct_mis_api.apps.utils.models import TimeStampedUUIDModel


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
