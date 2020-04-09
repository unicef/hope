from datetime import date

from django.core.validators import (
    validate_image_file_extension,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.db import models
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField

from hct_mis_api.apps.household.const import NATIONALITIES
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel


class ImportedHousehold(TimeStampedUUIDModel):
    RESIDENCE_STATUS_CHOICE = (
        ("REFUGEE", _("Refugee")),
        ("MIGRANT", _("Migrant")),
        ("CITIZEN", _("Citizen")),
        ("IDP", _("IDP")),
        ("OTHER", _("Other")),
    )

    household_ca_id = models.CharField(max_length=255)
    consent = ImageField(validators=[validate_image_file_extension])
    residence_status = models.CharField(
        max_length=255, choices=RESIDENCE_STATUS_CHOICE,
    )
    nationality = models.CharField(max_length=255, choices=NATIONALITIES,)
    family_size = models.PositiveIntegerField()
    address = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255)
    representative = models.ForeignKey(
        "ImportedIndividual",
        on_delete=models.SET_NULL,
        related_name="represented_households",
        null=True,
    )
    registration_data_import_id = models.ForeignKey(
        "RegistrationDataImportDatahub",
        related_name="households",
        on_delete=models.CASCADE,
    )
    head_of_household = models.OneToOneField(
        "ImportedIndividual",
        on_delete=models.CASCADE,
        related_name="heading_household",
        null=True,
    )
    registration_date = models.DateField(null=True)

    def __str__(self):
        return f"Household CashAssist ID: {self.household_ca_id}"


class ImportedIndividual(TimeStampedUUIDModel):
    SEX_CHOICE = (
        ("MALE", _("Male")),
        ("FEMALE", _("Female")),
        ("OTHER", _("Other")),
    )
    MARTIAL_STATUS_CHOICE = (
        ("SINGLE", _("SINGLE")),
        ("MARRIED", _("Married")),
        ("WIDOW", _("Widow")),
        ("DIVORCED", _("Divorced")),
        ("SEPARATED", _("Separated")),
    )
    IDENTIFICATION_TYPE_CHOICE = (
        ("NA", _("N/A")),
        ("BIRTH_CERTIFICATE", _("Birth Certificate")),
        ("DRIVING_LICENSE", _("Driving License")),
        ("UNHCR_ID_CARD", _("UNHCR ID card")),
        ("NATIONAL_ID", _("National ID")),
        ("NATIONAL_PASSPORT", _("National Passport")),
    )
    YES_NO_CHOICE = (
        ("YES", _("Yes")),
        ("NO", _("No")),
    )
    DISABILITY_CHOICE = (
        ("NO", _("No")),
        ("SEEING", _("Difficulty seeing (even if wearing glasses)")),
        ("HEARING", _("Difficulty hearing (even if using a hearing aid)")),
        ("WALKING", _("Difficulty walking or climbing steps")),
        ("MEMORY", _("Difficulty remembering or concentrating")),
        ("SELF_CARE", _("Difficulty with self care (washing, dressing)")),
        (
            "COMMUNICATING",
            _(
                "Difficulty communicating "
                "(e.g understanding or being understood)"
            ),
        ),
    )

    individual_ca_id = models.CharField(max_length=255)
    full_name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    first_name = models.CharField(
        max_length=85,
        validators=[MinLengthValidator(3), MaxLengthValidator(85)],
    )
    middle_name = models.CharField(
        max_length=85,
        validators=[MinLengthValidator(3), MaxLengthValidator(85)],
        blank=True,
    )
    last_name = models.CharField(
        max_length=85,
        validators=[MinLengthValidator(3), MaxLengthValidator(85)],
    )
    sex = models.CharField(max_length=255, choices=SEX_CHOICE,)
    dob = models.DateField()
    estimated_dob = models.CharField(
        max_length=3, default="NO", choices=YES_NO_CHOICE,
    )
    nationality = models.CharField(max_length=255, choices=NATIONALITIES,)
    martial_status = models.CharField(
        max_length=255, choices=MARTIAL_STATUS_CHOICE,
    )
    phone_number = PhoneNumberField(blank=True)
    phone_number_alternative = PhoneNumberField(blank=True)
    identification_type = models.CharField(
        max_length=255, choices=IDENTIFICATION_TYPE_CHOICE,
    )
    identification_number = models.CharField(max_length=255)
    household = models.ForeignKey(
        "ImportedHousehold",
        related_name="individuals",
        on_delete=models.CASCADE,
    )
    registration_data_import_id = models.ForeignKey(
        "RegistrationDataImportDatahub",
        related_name="individuals",
        on_delete=models.CASCADE,
    )
    work_status = models.CharField(
        max_length=3, default="NO", choices=YES_NO_CHOICE,
    )
    disability = models.CharField(
        max_length=30, default="NO", choices=DISABILITY_CHOICE,
    )

    @property
    def age(self):
        today = date.today()
        return (
            today.year
            - self.dob.year
            - ((today.month, today.day) < (self.dob.month, self.dob.day))
        )

    def __str__(self):
        return self.full_name


class RegistrationDataImportDatahub(TimeStampedUUIDModel):
    STATUS_CHOICE = (
        ("IN_PROGRESS", _("In progress")),
        ("DONE", _("Done")),
    )
    name = models.CharField(max_length=255, blank=True)
    import_date = models.DateTimeField(auto_now_add=True)
    hct_id = models.UUIDField(null=True)
    import_data = models.OneToOneField(
        "ImportData",
        related_name="registration_data_import",
        on_delete=models.CASCADE,
        null=True,
    )
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICE, default="IN_PROGRESS"
    )

    def __str__(self):
        return self.name


class ImportData(TimeStampedUUIDModel):
    xlsx_file = models.FileField()
    number_of_households = models.PositiveIntegerField()
    number_of_individuals = models.PositiveIntegerField()
