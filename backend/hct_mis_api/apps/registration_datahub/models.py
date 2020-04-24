from datetime import date

from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import JSONField
from django.core.validators import (
    validate_image_file_extension,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.db import models
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField

from household.const import NATIONALITIES
from household.models import (
    RESIDENCE_STATUS_CHOICE,
    SEX_CHOICE,
    MARTIAL_STATUS_CHOICE,
    RELATIONSHIP_CHOICE,
    ROLE_CHOICE,
)
from utils.models import TimeStampedUUIDModel


class ImportedHousehold(TimeStampedUUIDModel):
    consent = ImageField(validators=[validate_image_file_extension])
    residence_status = models.CharField(
        max_length=255, choices=RESIDENCE_STATUS_CHOICE,
    )
    country_origin = models.CharField(max_length=255, choices=NATIONALITIES,)
    size = models.PositiveIntegerField()
    address = models.CharField(max_length=255, blank=True)
    country = CountryField(blank=True)
    admin1 = models.CharField(max_length=255, blank=True)
    admin2 = models.CharField(max_length=255, blank=True)
    geopoint = PointField(blank=True, null=True)
    unhcr_id = models.CharField(max_length=255, blank=True)
    female_age_group_0_5_count = models.PositiveIntegerField(default=0)
    female_age_group_6_11_count = models.PositiveIntegerField(default=0)
    female_age_group_12_17_count = models.PositiveIntegerField(default=0)
    female_adults_count = models.PositiveIntegerField(default=0)
    pregnant_count = models.PositiveIntegerField(default=0)
    male_age_group_0_5_count = models.PositiveIntegerField(default=0)
    male_age_group_6_11_count = models.PositiveIntegerField(default=0)
    male_age_group_12_17_count = models.PositiveIntegerField(default=0)
    male_adults_count = models.PositiveIntegerField(default=0)
    female_age_group_0_5_disabled_count = models.PositiveIntegerField(default=0)
    female_age_group_6_11_disabled_count = models.PositiveIntegerField(
        default=0
    )
    female_age_group_12_17_disabled_count = models.PositiveIntegerField(
        default=0
    )
    female_adults_disabled_count = models.PositiveIntegerField(default=0)
    male_age_group_0_5_disabled_count = models.PositiveIntegerField(default=0)
    male_age_group_6_11_disabled_count = models.PositiveIntegerField(default=0)
    male_age_group_12_17_disabled_count = models.PositiveIntegerField(default=0)
    male_adults_disabled_count = models.PositiveIntegerField(default=0)
    head_of_household = models.OneToOneField(
        "ImportedIndividual", on_delete=models.CASCADE, null=True
    )
    registration_data_import = models.ForeignKey(
        "RegistrationDataImportDatahub",
        related_name="households",
        on_delete=models.CASCADE,
    )
    registration_date = models.DateField(null=True)
    flex_fields = JSONField(default=dict)

    def __str__(self):
        return f"Household ID: {self.id}"


class ImportedIndividual(TimeStampedUUIDModel):
    individual_id = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    full_name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    given_name = models.CharField(max_length=85, blank=True,)
    middle_name = models.CharField(max_length=85, blank=True,)
    family_name = models.CharField(max_length=85, blank=True,)
    relationship = models.CharField(
        max_length=255, blank=True, choices=RELATIONSHIP_CHOICE,
    )
    role = models.CharField(max_length=255, blank=True, choices=ROLE_CHOICE,)
    sex = models.CharField(max_length=255, choices=SEX_CHOICE,)
    birth_date = models.DateField()
    estimated_birth_date = models.BooleanField(default=False, null=True)
    marital_status = models.CharField(
        max_length=255, choices=MARTIAL_STATUS_CHOICE,
    )
    phone_no = PhoneNumberField(blank=True)
    phone_no_alternative = PhoneNumberField(blank=True)
    household = models.ForeignKey(
        "ImportedHousehold",
        related_name="individuals",
        on_delete=models.CASCADE,
    )
    registration_data_import = models.ForeignKey(
        "RegistrationDataImportDatahub",
        related_name="individuals",
        on_delete=models.CASCADE,
    )
    disability = models.BooleanField(default=False)
    flex_fields = JSONField(default=dict)

    @property
    def age(self):
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - (
                (today.month, today.day)
                < (self.birth_date.month, self.birth_date.day)
            )
        )

    def __str__(self):
        return self.full_name


class RegistrationDataImportDatahub(TimeStampedUUIDModel):
    name = models.CharField(max_length=255, blank=True)
    import_date = models.DateTimeField(auto_now_add=True)
    hct_id = models.UUIDField(null=True)
    import_data = models.OneToOneField(
        "ImportData",
        related_name="registration_data_import",
        on_delete=models.CASCADE,
        null=True,
    )

    def __str__(self):
        return self.name


class ImportData(TimeStampedUUIDModel):
    xlsx_file = models.FileField()
    number_of_households = models.PositiveIntegerField()
    number_of_individuals = models.PositiveIntegerField()
