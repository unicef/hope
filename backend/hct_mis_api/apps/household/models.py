import re
from datetime import date

from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import JSONField
from django.core.validators import MaxLengthValidator, MinLengthValidator, validate_image_file_extension
from django.db import models
from django.utils.translation import ugettext_lazy as _

from dateutil.relativedelta import relativedelta
from django_countries.fields import CountryField
from model_utils import Choices
from multiselectfield import MultiSelectField
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField

from utils.models import AbstractSyncable, TimeStampedUUIDModel

RESIDENCE_STATUS_CHOICE = (
    ("IDP", _("Displaced  |  Internally Displaced People")),
    ("REFUGEE", _("Displaced  |  Refugee / Asylum Seeker")),
    ("OTHERS_OF_CONCERN", _("Displaced  |  Others of Concern")),
    ("HOST", _("Non-displaced  |   Host")),
    ("NON_HOST", _("Non-displaced  |   Non-host")),
)
# INDIVIDUALS
MALE = "MALE"
FEMALE = "FEMALE"
SEX_CHOICE = (
    (MALE, _("Male")),
    (FEMALE, _("Female")),
)
SINGLE = "SINGLE"
MARRIED = "MARRIED"
WIDOWED = "WIDOWED"
DIVORCED = "DIVORCED"
SEPARATED = "SEPARATED"
MARITAL_STATUS_CHOICE = (
    (SINGLE, _("Single")),
    (MARRIED, _("Married")),
    (WIDOWED, _("Widowed")),
    (DIVORCED, _("Divorced")),
    (SEPARATED, _("Separated")),
)

NONE = "NONE"
SEEING = "SEEING"
HEARING = "HEARING"
WALKING = "WALKING"
MEMORY = "MEMORY"
SELF_CARE = "SELF_CARE"
COMMUNICATING = "COMMUNICATING"
DISABILITY_CHOICE = (
    (NONE, _("None")),
    (SEEING, _("Difficulty seeing (even if wearing glasses)")),
    (HEARING, _("Difficulty hearing (even if using a hearing aid)")),
    (WALKING, _("Difficulty walking or climbing steps")),
    (MEMORY, _("Difficulty remembering or concentrating")),
    (SELF_CARE, _("Difficulty with self care (washing, dressing)")),
    (COMMUNICATING, _("Difficulty communicating " "(e.g understanding or being understood)"),),
)
NON_BENEFICIARY = "NON_BENEFICIARY"
HEAD = "HEAD"
SON_DAUGHTER = "SON_DAUGHTER"
WIFE_HUSBAND = "WIFE_HUSBAND"
BROTHER_SISTER = "BROTHER_SISTER"
MOTHER_FATHER = "MOTHER_FATHER"
AUNT_UNCLE = "AUNT_UNCLE"
GRANDMOTHER_GRANDFATHER = "GRANDMOTHER_GRANDFATHER"
MOTHERINLAW_FATHERINLAW = "MOTHERINLAW_FATHERINLAW"
DAUGHTERINLAW_SONINLAW = "DAUGHTERINLAW_SONINLAW"
SISTERINLAW_BROTHERINLAW = "SISTERINLAW_BROTHERINLAW"
GRANDDAUGHER_GRANDSON = "GRANDDAUGHER_GRANDSON"
NEPHEW_NIECE = "NEPHEW_NIECE"
COUSIN = "COUSIN"
RELATIONSHIP_CHOICE = (
    (NON_BENEFICIARY, "Not a Family Member. Can only act as a recipient.",),
    (HEAD, "Head of household (self)"),
    (SON_DAUGHTER, "Son / Daughter"),
    (WIFE_HUSBAND, "Wife / Husband"),
    (BROTHER_SISTER, "Brother / Sister"),
    (MOTHER_FATHER, "Mother / Father"),
    (AUNT_UNCLE, "Aunt / Uncle"),
    (GRANDMOTHER_GRANDFATHER, "Grandmother / Grandfather"),
    (MOTHERINLAW_FATHERINLAW, "Mother-in-law / Father-in-law"),
    (DAUGHTERINLAW_SONINLAW, "Daughter-in-law / Son-in-law"),
    (SISTERINLAW_BROTHERINLAW, "Sister-in-law / Brother-in-law"),
    (GRANDDAUGHER_GRANDSON, "Granddaughter / Grandson"),
    (NEPHEW_NIECE, "Nephew / Niece"),
    (COUSIN, "Cousin"),
)
YES = "YES"
NO = "NO"
YES_NO_CHOICE = (
    (YES, _("Yes")),
    (NO, _("No")),
)
NOT_PROVIDED = "NOT_PROVIDED"
WORK_STATUS_CHOICE = (
    (YES, _("Yes")),
    (NO, _("No")),
    (NOT_PROVIDED, _("Not provided")),
)
ROLE_PRIMARY = "PRIMARY"
ROLE_ALTERNATE = "ALTERNATE"
ROLE_NO_ROLE = "NO_ROLE"
ROLE_CHOICE = (
    (ROLE_PRIMARY, "Primary collector"),
    (ROLE_ALTERNATE, "Alternate collector"),
    (ROLE_NO_ROLE, "None"),
)
IDENTIFICATION_TYPE_BIRTH_CERTIFICATE = "BIRTH_CERTIFICATE"
IDENTIFICATION_TYPE_DRIVERS_LICENSE = "DRIVERS_LICENSE"
IDENTIFICATION_TYPE_NATIONAL_ID = "NATIONAL_ID"
IDENTIFICATION_TYPE_NATIONAL_PASSPORT = "NATIONAL_PASSPORT"
IDENTIFICATION_TYPE_ELECTORAL_CARD = "ELECTORAL_CARD"
IDENTIFICATION_TYPE_OTHER = "OTHER"
IDENTIFICATION_TYPE_CHOICE = (
    (IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, _("Birth Certificate")),
    (IDENTIFICATION_TYPE_DRIVERS_LICENSE, _("Driver's License")),
    (IDENTIFICATION_TYPE_NATIONAL_ID, _("National ID")),
    (IDENTIFICATION_TYPE_NATIONAL_PASSPORT, _("National Passport")),
    (IDENTIFICATION_TYPE_ELECTORAL_CARD, _("Electoral Card")),
    (IDENTIFICATION_TYPE_OTHER, _("Other")),
)
IDENTIFICATION_TYPE_DICT = {
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE: "Birth Certificate",
    IDENTIFICATION_TYPE_DRIVERS_LICENSE: "Driver's License",
    IDENTIFICATION_TYPE_NATIONAL_ID: "National ID",
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT: "National Passport",
    IDENTIFICATION_TYPE_ELECTORAL_CARD: "Electoral Card",
    IDENTIFICATION_TYPE_OTHER: "Other",
}
ACTIVE = "ACTIVE"
INACTIVE = "INACTIVE"
INDIVIDUAL_HOUSEHOLD_STATUS = ((ACTIVE, "Active"), (INACTIVE, "Inactive"))
UNIQUE = "UNIQUE"
DUPLICATE = "DUPLICATE"
NEEDS_ADJUDICATION = "NEEDS_ADJUDICATION"
NOT_PROCESSED = "NOT_PROCESSED"
DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE = (
    (UNIQUE, "Unique"),
    (DUPLICATE, "Duplicate"),
    (NEEDS_ADJUDICATION, "Needs Adjudication"),
    (NOT_PROCESSED, "Not Processed"),
)
SIMILAR_IN_BATCH = "SIMILAR_IN_BATCH"
DUPLICATE_IN_BATCH = "DUPLICATE_IN_BATCH"
UNIQUE_IN_BATCH = "UNIQUE_IN_BATCH"
NOT_PROCESSED = "NOT_PROCESSED"
DEDUPLICATION_BATCH_STATUS_CHOICE = (
    (SIMILAR_IN_BATCH, "Similar in batch"),
    (DUPLICATE_IN_BATCH, "Duplicate in batch"),
    (UNIQUE_IN_BATCH, "Unique in batch"),
    (NOT_PROCESSED, "Not Processed"),
)
SOME_DIFFICULTY = "SOME_DIFFICULTY"
LOT_DIFFICULTY = "LOT_DIFFICULTY"
CANNOT_DO = "CANNOT_DO"
SEVERITY_OF_DISABILITY_CHOICES = (
    (SOME_DIFFICULTY, "Some difficulty"),
    (LOT_DIFFICULTY, "A lot of difficulty"),
    (CANNOT_DO, "Cannot do at all"),
)
UNICEF = "UNICEF"
PARTNER = "PARTNER"
ORG_ENUMERATOR_CHOICES = (
    (UNICEF, "UNICEF"),
    (PARTNER, "Partner"),
)
HUMANITARIAN_PARTNER = "HUMANITARIAN_PARTNER"
PRIVATE_PARTNER = "PRIVATE_PARTNER"
GOVERNMENT_PARTNER = "GOVERNMENT_PARTNER"
DATA_SHARING_CHOICES = (
    (UNICEF, "UNICEF"),
    (HUMANITARIAN_PARTNER, "Humanitarian partners"),
    (PRIVATE_PARTNER, "Private partners"),
    (GOVERNMENT_PARTNER, "Government partners"),
)


class Household(TimeStampedUUIDModel, AbstractSyncable):
    status = models.CharField(max_length=20, choices=INDIVIDUAL_HOUSEHOLD_STATUS, default=ACTIVE)
    consent_sign = ImageField(validators=[validate_image_file_extension], blank=True)
    consent = models.BooleanField(default=True)
    consent_sharing = MultiSelectField(choices=DATA_SHARING_CHOICES)
    residence_status = models.CharField(max_length=255, choices=RESIDENCE_STATUS_CHOICE)
    country_origin = CountryField(blank=True)
    country = CountryField(blank=True)
    size = models.PositiveIntegerField()
    address = models.CharField(max_length=255, blank=True)
    """location contains lowest administrative area info"""
    admin_area = models.ForeignKey("core.AdminArea", null=True, on_delete=models.SET_NULL)
    representatives = models.ManyToManyField(
        to="household.Individual",
        through="household.IndividualRoleInHousehold",
        help_text="""This is only used to track collector (primary or secondary) of a household.
            They may still be a HOH of this household or any other household.
            Through model will contain the role (ROLE_CHOICE) they are connected with on.""",
        related_name="represented_households",
    )
    geopoint = PointField(blank=True, null=True)
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
    female_age_group_6_11_disabled_count = models.PositiveIntegerField(default=0)
    female_age_group_12_17_disabled_count = models.PositiveIntegerField(default=0)
    female_adults_disabled_count = models.PositiveIntegerField(default=0)
    male_age_group_0_5_disabled_count = models.PositiveIntegerField(default=0)
    male_age_group_6_11_disabled_count = models.PositiveIntegerField(default=0)
    male_age_group_12_17_disabled_count = models.PositiveIntegerField(default=0)
    male_adults_disabled_count = models.PositiveIntegerField(default=0)
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport", related_name="households", on_delete=models.CASCADE,
    )
    programs = models.ManyToManyField("program.Program", related_name="households", blank=True,)
    returnee = models.BooleanField(default=False, null=True)
    flex_fields = JSONField(default=dict)
    first_registration_date = models.DateField()
    last_registration_date = models.DateField()
    head_of_household = models.OneToOneField("Individual", related_name="heading_household", on_delete=models.CASCADE)
    fchild_hoh = models.BooleanField(default=False)
    child_hoh = models.BooleanField(default=False)
    unicef_id = models.CharField(max_length=250, blank=True)
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    deviceid = models.CharField(max_length=250, blank=True)
    name_enumerator = models.CharField(max_length=250)
    org_enumerator = models.CharField(max_length=250, choices=ORG_ENUMERATOR_CHOICES)
    org_name_enumerator = models.CharField(max_length=250)
    village = models.CharField(max_length=250, blank=True)

    @property
    def sanction_list_possible_match(self):
        return self.individuals.filter(sanction_list_possible_match=True).count() > 0

    @property
    def total_cash_received(self):
        return self.payment_records.filter().aggregate(models.Sum("delivered_quantity")).get("delivered_quantity__sum")

    def __str__(self):
        return f"Household ID: {self.id}"


class DocumentValidator(TimeStampedUUIDModel):
    type = models.ForeignKey("DocumentType", related_name="validators", on_delete=models.CASCADE)
    regex = models.CharField(max_length=100, default=".*")


class DocumentType(TimeStampedUUIDModel):
    country = CountryField(blank=True)
    label = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=IDENTIFICATION_TYPE_CHOICE)

    class Meta:
        unique_together = ("country", "type")

    def __str__(self):
        return f"{self.label} in {self.country}"


class Document(TimeStampedUUIDModel):
    document_number = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    individual = models.ForeignKey("Individual", related_name="documents", on_delete=models.CASCADE)
    type = models.ForeignKey("DocumentType", related_name="documents", on_delete=models.CASCADE)

    def clean(self):
        from django.core.exceptions import ValidationError

        for validator in self.type.validators:
            if not re.match(validator.regex, self.document_number):
                raise ValidationError("Document number is not validating")


class Agency(models.Model):
    type = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=100,)

    def __str__(self):
        return self.label


class HouseholdIdentity(models.Model):
    agency = models.ForeignKey("Agency", related_name="households_identities", on_delete=models.CASCADE)
    household = models.ForeignKey("Household", related_name="identities", on_delete=models.CASCADE)
    document_number = models.CharField(max_length=255,)

    def __str__(self):
        return f"{self.agency} {self.household} {self.document_number}"


class IndividualIdentity(models.Model):
    agency = models.ForeignKey("Agency", related_name="individual_identities", on_delete=models.CASCADE)
    individual = models.ForeignKey("Individual", related_name="identities", on_delete=models.CASCADE)
    number = models.CharField(max_length=255,)

    def __str__(self):
        return f"{self.agency} {self.individual} {self.number}"


class IndividualRoleInHousehold(TimeStampedUUIDModel, AbstractSyncable):
    individual = models.ForeignKey(
        "household.Individual", on_delete=models.CASCADE, related_name="households_and_roles",
    )
    household = models.ForeignKey(
        "household.Household", on_delete=models.CASCADE, related_name="individuals_and_roles",
    )
    role = models.CharField(max_length=255, blank=True, choices=ROLE_CHOICE,)

    class Meta:
        unique_together = ("role", "household")

    def __str__(self):
        return f"{self.individual.full_name} - {self.role}"


class Individual(TimeStampedUUIDModel, AbstractSyncable):
    status = models.CharField(max_length=20, choices=INDIVIDUAL_HOUSEHOLD_STATUS, default="ACTIVE")
    individual_id = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    full_name = models.CharField(max_length=255, validators=[MinLengthValidator(3), MaxLengthValidator(255)],)
    given_name = models.CharField(max_length=85, blank=True,)
    middle_name = models.CharField(max_length=85, blank=True,)
    family_name = models.CharField(max_length=85, blank=True,)
    sex = models.CharField(max_length=255, choices=SEX_CHOICE,)
    birth_date = models.DateField()
    estimated_birth_date = models.BooleanField(default=False)
    marital_status = models.CharField(max_length=255, choices=MARITAL_STATUS_CHOICE,)
    phone_no = PhoneNumberField(blank=True)
    phone_no_alternative = PhoneNumberField(blank=True)
    relationship = models.CharField(
        max_length=255,
        blank=True,
        choices=RELATIONSHIP_CHOICE,
        help_text="""This represents the MEMBER relationship. can be blank
            as well if household is null!""",
    )
    household = models.ForeignKey(
        "Household",
        related_name="individuals",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="""This represents the household this person is a MEMBER,
            and if null then relationship is NON_BENEFICIARY and that
            simply means they are a representative of one or more households
            and not a member of one.""",
    )
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport", related_name="individuals", on_delete=models.CASCADE, null=True,
    )
    disability = models.BooleanField(default=False)
    work_status = models.CharField(max_length=20, choices=WORK_STATUS_CHOICE, blank=True, default=NOT_PROVIDED,)
    first_registration_date = models.DateField()
    last_registration_date = models.DateField()
    flex_fields = JSONField(default=dict)
    enrolled_in_nutrition_programme = models.BooleanField(default=False)
    administration_of_rutf = models.BooleanField(default=False)
    unicef_id = models.CharField(max_length=250, blank=True)
    deduplication_golden_record_status = models.CharField(
        max_length=50, default=UNIQUE, choices=DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
    )
    deduplication_batch_status = models.CharField(
        max_length=50, default=UNIQUE_IN_BATCH, choices=DEDUPLICATION_BATCH_STATUS_CHOICE,
    )
    deduplication_golden_record_results = JSONField(default=dict)
    deduplication_batch_results = JSONField(default=dict)
    imported_individual_id = models.UUIDField(null=True)
    sanction_list_possible_match = models.BooleanField(default=False)
    sanction_list_last_check = models.DateTimeField(null=True, blank=True)
    pregnant = models.BooleanField(default=False)
    observed_disability = MultiSelectField(choices=DISABILITY_CHOICE, default=NONE)
    seeing_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    hearing_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    physical_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    memory_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    selfcare_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    comms_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    who_answers_phone = models.CharField(max_length=150, blank=True)
    who_answers_alt_phone = models.CharField(max_length=150, blank=True)

    @property
    def age(self):
        return relativedelta(date.today(), self.birth_date).years

    @property
    def get_hash_key(self):
        from hashlib import sha256

        fields = (
            "given_name",
            "middle_name",
            "family_name",
            "sex",
            "birth_date",
            "phone_no",
            "phone_no_alternative",
        )
        values = [str(getattr(self, field)) for field in fields]

        return sha256(";".join(values).encode()).hexdigest()

    def __str__(self):
        return self.full_name


class EntitlementCard(TimeStampedUUIDModel):
    ACTIVE = "ACTIVE"
    ERRONEOUS = "ERRONEOUS"
    CLOSED = "CLOSED"
    STATUS_CHOICE = Choices((ACTIVE, _("Active")), (ERRONEOUS, _("Erroneous")), (CLOSED, _("Closed")),)
    card_number = models.CharField(max_length=255)
    status = models.CharField(choices=STATUS_CHOICE, default=ACTIVE, max_length=10,)
    card_type = models.CharField(max_length=255)
    current_card_size = models.CharField(max_length=255)
    card_custodian = models.CharField(max_length=255)
    service_provider = models.CharField(max_length=255)
    household = models.ForeignKey("Household", related_name="entitlement_cards", on_delete=models.SET_NULL, null=True,)
