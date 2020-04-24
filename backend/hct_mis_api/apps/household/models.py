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
    ("OTHER", _("Other")),
)
MARITAL_STATUS_CHOICE = (
    ("SINGLE", _("SINGLE")),
    ("MARRIED", _("Married")),
    ("WIDOW", _("Widow")),
    ("DIVORCED", _("Divorced")),
    ("SEPARATED", _("Separated")),
)
DOCUMENT_TYPE_CHOICE = (
    ("BIRTH_CERTIFICATE", _("Birth Certificate")),
    ("DRIVING_LICENSE", _("Driving License")),
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
    unhcr_id = models.CharField(max_length=255, blank=True)
    f_0_5_age_group = models.PositiveIntegerField(default=0)
    f_6_11_age_group = models.PositiveIntegerField(default=0)
    f_12_17_age_group = models.PositiveIntegerField(default=0)
    m_0_5_age_group = models.PositiveIntegerField(default=0)
    m_6_11_age_group = models.PositiveIntegerField(default=0)
    m_12_17_age_group = models.PositiveIntegerField(default=0)
    f_adults = models.PositiveIntegerField(default=0)
    m_adults = models.PositiveIntegerField(default=0)
    f_pregnant = models.PositiveIntegerField(default=0)
    f_0_5_disability = models.PositiveIntegerField(default=0)
    f_6_11_disability = models.PositiveIntegerField(default=0)
    f_12_17_disability = models.PositiveIntegerField(default=0)
    f_adults_disability = models.PositiveIntegerField(default=0)
    m_0_5_disability = models.PositiveIntegerField(default=0)
    m_6_11_disability = models.PositiveIntegerField(default=0)
    m_12_17_disability = models.PositiveIntegerField(default=0)
    m_adults_disability = models.PositiveIntegerField(default=0)
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="households",
        on_delete=models.CASCADE,
    )
    programs = models.ManyToManyField(
        "program.Program", related_name="households", blank=True,
    )
    flex_fields = JSONField(default=dict)
    registration_date = models.DateField(null=True)
    head_of_household = models.OneToOneField(
        "Individual",
        related_name="heading_household",
        null=True,
        on_delete=models.SET_NULL,
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


class DocumentType(TimeStampedUUIDModel):
    country = CountryField(blank=True)
    type = models.CharField(max_length=100)
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


class Agency(models.Model):
    type = models.CharField(max_length=100,)
    label = models.CharField(max_length=100,)

    def __str__(self):
        return f"{self.label}"


class Identity(models.Model):
    agency = models.ForeignKey(
        "Agency", related_name="identities", on_delete=models.CASCADE
    )
    individual = models.ForeignKey(
        "Individual", related_name="identities", on_delete=models.CASCADE
    )
    document_number = models.CharField(max_length=255,)

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
    estimated_birth_date = models.BooleanField(null=True)
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
