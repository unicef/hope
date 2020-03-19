import operator
from datetime import date
from typing import List

from core import models as core_models
from django.core.validators import (
    validate_image_file_extension,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from household.const import NATIONALITIES
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField
from utils.models import TimeStampedUUIDModel

_INTEGER = "INTEGER"
_SELECT_ONE = "SELECT_ONE"


class Household(TimeStampedUUIDModel):
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
    address = models.CharField(max_length=255, blank=True, null=True)
    location = models.ForeignKey(
        "core.Location", related_name="households", on_delete=models.CASCADE,
    )
    representative = models.ForeignKey(
        "Individual",
        on_delete=models.SET_NULL,
        related_name="represented_households",
        null=True,
    )
    registration_data_import_id = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="households",
        on_delete=models.CASCADE,
    )
    head_of_household = models.OneToOneField(
        "Individual",
        on_delete=models.CASCADE,
        related_name="heading_household",
        null=True,
    )
    programs = models.ManyToManyField(
        "program.Program", related_name="households", blank=True,
    )
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
    dob = models.DateField(blank=True, null=True)
    estimated_dob = models.DateField(blank=True, null=True)
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
        "Household", related_name="individuals", on_delete=models.CASCADE,
    )
    registration_data_import_id = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="individuals",
        on_delete=models.CASCADE,
    )
    work_status = models.CharField(
        max_length=3, default="NO", choices=YES_NO_CHOICE,
    )
    disability = models.CharField(
        max_length=30, default="NO", choices=DISABILITY_CHOICE,
    )
    serious_illness = models.CharField(
        max_length=3, default="NO", choices=YES_NO_CHOICE,
    )
    age_first_married = models.PositiveIntegerField(null=True, default=None)
    enrolled_in_school = models.CharField(
        max_length=3, default="NO", choices=YES_NO_CHOICE,
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


# TODO(codecakes): make it dynamic when possible.
def get_core_fields() -> List:
    """Gets list of flex metadatatype objects. """

    get_item_fn = operator.itemgetter(1)
    associated_with = core_models.FlexibleAttribute.ASSOCIATED_WITH_CHOICES

    return [
        {
            "id": "05c6be72-22ac-401b-9d3f-0a7e7352aa87",
            "type": _INTEGER,
            "name": "years_in_school",
            "label": {"English(EN)": "years in school"},
            "hint": "number of years spent in school",
            "required": True,
            "choices": [],
            "associated_with": get_item_fn(associated_with[1]),
        },
        {
            "id": "a1741e3c-0e24-4a60-8d2f-463943abaebb",
            "type": _INTEGER,
            "name": "age",
            "label": {"English(EN)": "age"},
            "hint": "age in years",
            "required": True,
            "choices": [],
            "associated_with": get_item_fn(associated_with[1]),
        },
        {
            "id": "d6aa9669-ae82-4e3c-adfe-79b5d95d0754",
            "type": _INTEGER,
            "name": "family_size",
            "label": {"English(EN)": "Family Size"},
            "hint": "how many persons in the household",
            "required": True,
            "choices": [],
            "associated_with": get_item_fn(associated_with[0]),
        },
        {
            "id": "3c2473d6-1e81-4025-86c7-e8036dd92f4b",
            "type": _SELECT_ONE,
            "name": "residence_status",
            "required": True,
            "label": {"English(EN)": "Residence Status"},
            "hint": "residential status of household",
            "choices": [
                {"name": name, "value": str(value)}
                for name, value in Household.RESIDENCE_STATUS_CHOICE
            ],
            "associated_with": get_item_fn(associated_with[0]),
        },
    ]
