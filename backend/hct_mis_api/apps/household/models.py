import re
from datetime import date

from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import JSONField
from django.core.validators import (
    validate_image_file_extension,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField

from household.const import NATIONALITIES
from utils.models import TimeStampedUUIDModel


RESIDENCE_STATUS_CHOICE = (
    ("REFUGEE", _("Refugee")),
    ("MIGRANT", _("Migrant")),
    ("CITIZEN", _("Citizen")),
    ("IDP", _("IDP")),
    ("OTHER", _("Other")),
)
# INDIVIDUALS
SEX_CHOICE = (
    ("MALE", _("Male")),
    ("FEMALE", _("Female")),
)
MARITAL_STATUS_CHOICE = (
    ("SINGLE", _("SINGLE")),
    ("MARRIED", _("Married")),
    ("WIDOW", _("Widow")),
    ("DIVORCED", _("Divorced")),
    ("SEPARATED", _("Separated")),
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
RELATIONSHIP_CHOICE = (
    ("NON_BENEFICIARY", "Not a Family Member. Can only act as a recipient.",),
    ("HEAD", "Head of household (self)"),
    ("SON_DAUGHTER", "Son / Daughter"),
    ("WIFE_HUSBAND", "Wife / Husband"),
    ("BROTHER_SISTER", "Brother / Sister"),
    ("MOTHER_FATHER", "Mother / Father"),
    ("AUNT_UNCLE", "Aunt / Uncle"),
    ("GRANDMOTHER_GRANDFATHER", "Grandmother / Grandfather"),
    ("MOTHERINLAW_FATHERINLAW", "Mother-in-law / Father-in-law"),
    ("DAUGHTERINLAW_SONINLAW", "Daughter-in-law / Son-in-law"),
    ("SISTERINLAW_BROTHERINLAW", "Sister-in-law / Brother-in-law"),
    ("GRANDDAUGHER_GRANDSON", "Granddaughter / Grandson"),
    ("NEPHEW_NIECE", "Nephew / Niece"),
    ("COUSIN", "Cousin"),
)
ROLE_CHOICE = (
    ("PRIMARY", "Primary collector"),
    ("ALTERNATE", "Alternate collector"),
    ("NO_ROLE", "None"),
)


class Household(TimeStampedUUIDModel):
    consent = ImageField(validators=[validate_image_file_extension])
    residence_status = models.CharField(
        max_length=255, choices=RESIDENCE_STATUS_CHOICE,
    )
    country_origin = CountryField(blank=True)
    country = CountryField(blank=True)

    size = models.PositiveIntegerField()
    address = models.CharField(max_length=255, blank=True)
    """location contains lowest administrative area info"""
    admin_area = models.ForeignKey(
        "core.AdminArea", null=True, on_delete=models.SET_NULL
    )
    geopoint = PointField(blank=True, null=True)
    unhcr_case_id = models.CharField(max_length=255, blank=True)
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
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="households",
        on_delete=models.CASCADE,
    )
    programs = models.ManyToManyField(
        "program.Program", related_name="households", blank=True,
    )
    returnee = models.BooleanField(default=False, null=True)
    flex_fields = JSONField(default=dict)
    registration_date = models.DateField(null=True)
    head_of_household = models.OneToOneField(
        "Individual",
        related_name="heading_household",
        on_delete=models.CASCADE,
    )

    @property
    def total_cash_received(self):
        return (
            self.payment_records.filter()
            .aggregate(Sum("entitlement__delivered_quantity"))
            .get("entitlement__delivered_quantity__sum")
        )

    def __str__(self):
        return f"Household ID: {self.id}"


class DocumentValidator(TimeStampedUUIDModel):
    type = models.ForeignKey(
        "DocumentType", related_name="validators", on_delete=models.CASCADE
    )
    regex = models.CharField(max_length=100, default=".*")


class DocumentType(TimeStampedUUIDModel):
    country = CountryField(blank=True)
    label = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.label} in {self.country}"


class Document(TimeStampedUUIDModel):
    document_number = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    individual = models.ForeignKey(
        "Individual", related_name="documents", on_delete=models.CASCADE
    )
    type = models.ForeignKey(
        "DocumentType", related_name="documents", on_delete=models.CASCADE
    )

    def clean(self):
        from django.core.exceptions import ValidationError
        for validator in self.type.validators:
            if not re.match(validator.regex, self.document_number):
                raise ValidationError("Document number is not validating")

    class Meta:
        unique_together = ("type", "document_number")


class Agency(models.Model):
    type = models.CharField(max_length=100,)
    label = models.CharField(max_length=100,)

    def __str__(self):
        return self.label


class Identity(models.Model):
    agency = models.ForeignKey(
        "Agency", related_name="identities", on_delete=models.CASCADE
    )
    individual = models.ForeignKey(
        "Individual", related_name="identities", on_delete=models.CASCADE
    )
    number = models.CharField(max_length=255,)

    class Meta:
        unique_together = ("agency", "number")

    def __str__(self):
        return f"{self.agency} {self.individual} {self.document_number}"


class Individual(TimeStampedUUIDModel):
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
    estimated_birth_date = models.BooleanField(default=False)
    marital_status = models.CharField(
        max_length=255, choices=MARITAL_STATUS_CHOICE,
    )
    phone_no = PhoneNumberField(blank=True)
    phone_no_alternative = PhoneNumberField(blank=True)
    household = models.ForeignKey(
        "Household", related_name="individuals", on_delete=models.CASCADE,
    )
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="individuals",
        on_delete=models.CASCADE,
    )
    disability = models.BooleanField(default=False,)
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
