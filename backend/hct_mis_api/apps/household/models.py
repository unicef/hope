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

    @property
    def total_cash_received(self):
        return (
            self.payment_records.filter()
            .aggregate(Sum("entitlement__delivered_quantity"))
            .get("entitlement__delivered_quantity__sum")
        )

    def __str__(self):
        return f"Household CashAssist ID: {self.household_ca_id}"


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
    estimated_birth_date = models.DateField(blank=True, null=True)
    martial_status = models.CharField(
        max_length=255, choices=MARTIAL_STATUS_CHOICE,
    )
    phone_no = PhoneNumberField(blank=True)
    phone_no_alternative = PhoneNumberField(blank=True)
    id_type = models.CharField(
        max_length=255, choices=IDENTIFICATION_TYPE_CHOICE,
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
        "Household", related_name="individuals", on_delete=models.CASCADE,
    )
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="individuals",
        on_delete=models.CASCADE,
    )
    work_status = models.CharField(
        max_length=3, default="NO", choices=YES_NO_CHOICE,
    )
    disability = models.CharField(
        max_length=30, default="NO", choices=YES_NO_CHOICE,
    )
    serious_illness = models.CharField(
        max_length=3, choices=YES_NO_CHOICE, blank=True, default="",
    )
    age_first_married = models.PositiveIntegerField(null=True, default=None)
    enrolled_in_school = models.CharField(
        max_length=3, choices=YES_NO_CHOICE, blank=True, default="",
    )
    school_attendance = models.CharField(max_length=100, blank=True, default="")
    school_type = models.CharField(max_length=100, blank=True, default="")
    years_in_school = models.PositiveIntegerField(null=True, default=None)
    minutes_to_school = models.PositiveIntegerField(null=True, default=None)
    enrolled_in_nutrition_programme = models.CharField(
        max_length=3, default="", choices=YES_NO_CHOICE, blank=True,
    )
    administration_of_rutf = models.CharField(
        max_length=3, default="", choices=YES_NO_CHOICE, blank=True,
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
