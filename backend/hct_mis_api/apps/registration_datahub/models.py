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
    YES_NO_CHOICE,
    MARTIAL_STATUS_CHOICE,
    IDENTIFICATION_TYPE_CHOICE,
    RELATIONSHIP_CHOICE,
    ROLE_CHOICE,
)
from utils.models import TimeStampedUUIDModel


class ImportedHousehold(TimeStampedUUIDModel):
    household_ca_id = models.CharField(max_length=255, blank=True)
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
    f_0_5_age_group = models.PositiveIntegerField(default=0)
    f_6_11_age_group = models.PositiveIntegerField(default=0)
    f_12_17_age_group = models.PositiveIntegerField(default=0)
    f_adults = models.PositiveIntegerField(default=0)
    f_pregnant = models.PositiveIntegerField(default=0)
    m_0_5_age_group = models.PositiveIntegerField(default=0)
    m_6_11_age_group = models.PositiveIntegerField(default=0)
    m_12_17_age_group = models.PositiveIntegerField(default=0)
    m_adults = models.PositiveIntegerField(default=0)
    f_0_5_disability = models.PositiveIntegerField(default=0)
    f_6_11_disability = models.PositiveIntegerField(default=0)
    f_12_17_disability = models.PositiveIntegerField(default=0)
    f_adults_disability = models.PositiveIntegerField(default=0)
    m_0_5_disability = models.PositiveIntegerField(default=0)
    m_6_11_disability = models.PositiveIntegerField(default=0)
    m_12_17_disability = models.PositiveIntegerField(default=0)
    m_adults_disability = models.PositiveIntegerField(default=0)
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
    individual_ca_id = models.CharField(max_length=255, blank=True,)
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
    estimated_birth_date = models.CharField(
        max_length=3, default="NO", choices=YES_NO_CHOICE, blank=True,
    )
    martial_status = models.CharField(
        max_length=255, choices=MARTIAL_STATUS_CHOICE,
    )
    phone_no = PhoneNumberField(blank=True)
    phone_no_alternative = PhoneNumberField(blank=True)
    id_type = models.CharField(
        max_length=255, choices=IDENTIFICATION_TYPE_CHOICE,
    )
    head_of_household = models.OneToOneField(
        "ImportedIndividual", on_delete=models.CASCADE, null=True
    )
    birth_certificate_no = models.CharField(max_length=255, blank=True)
    birth_certificate_photo = models.ImageField(blank=True)
    drivers_license_no = models.CharField(max_length=255, blank=True)
    drivers_license_photo = models.ImageField(blank=True)
    electoral_card_no = models.CharField(max_length=255, blank=True)
    electoral_card_photo = models.ImageField(blank=True)
    unhcr_id_no = models.CharField(max_length=255, blank=True)
    unhcr_id_photo = models.ImageField(blank=True)
    national_passport = models.CharField(max_length=255, blank=True)
    national_passport_photo = models.ImageField(blank=True)
    scope_id_no = models.CharField(max_length=255, blank=True)
    scope_id_photo = models.ImageField(blank=True)
    other_id_type = models.CharField(max_length=255, blank=True)
    other_id_no = models.CharField(max_length=255, blank=True)
    other_id_photo = models.ImageField(blank=True)
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
    work_status = models.CharField(
        max_length=3, default="NO", choices=YES_NO_CHOICE,
    )
    disability = models.CharField(
        max_length=30, default="NO", choices=YES_NO_CHOICE,
    )
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
