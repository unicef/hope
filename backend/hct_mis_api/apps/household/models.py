import logging
import re
from datetime import date

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.gis.db.models import PointField, Q, UniqueConstraint
from django.contrib.postgres.fields import ArrayField, CICharField
from django.core.cache import cache
from django.core.validators import MinLengthValidator, validate_image_file_extension
from django.db import models
from django.db.models import DecimalField, JSONField
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from model_utils import Choices
from model_utils.models import SoftDeletableModel
from multiselectfield import MultiSelectField
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField
from django.contrib.postgres.search import SearchVectorField

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES
from hct_mis_api.apps.utils.models import (
    AbstractSyncable,
    ConcurrencyModel,
    SoftDeletableModelWithDate,
    TimeStampedUUIDModel,
)
from hct_mis_api.apps.payment.utils import is_right_phone_number_format

BLANK = ""
IDP = "IDP"
REFUGEE = "REFUGEE"
OTHERS_OF_CONCERN = "OTHERS_OF_CONCERN"
HOST = "HOST"
NON_HOST = "NON_HOST"
RESIDENCE_STATUS_CHOICE = (
    (BLANK, _("None")),
    (IDP, _("Displaced  |  Internally Displaced People")),
    (REFUGEE, _("Displaced  |  Refugee / Asylum Seeker")),
    (OTHERS_OF_CONCERN, _("Displaced  |  Others of Concern")),
    (HOST, _("Non-displaced  |   Host")),
    (NON_HOST, _("Non-displaced  |   Non-host")),
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
    (BLANK, _("None")),
    (DIVORCED, _("Divorced")),
    (MARRIED, _("Married")),
    (SEPARATED, _("Separated")),
    (SINGLE, _("Single")),
    (WIDOWED, _("Widowed")),
)

NONE = "NONE"
SEEING = "SEEING"
HEARING = "HEARING"
WALKING = "WALKING"
MEMORY = "MEMORY"
SELF_CARE = "SELF_CARE"
COMMUNICATING = "COMMUNICATING"
OBSERVED_DISABILITY_CHOICE = (
    (NONE, _("None")),
    (SEEING, _("Difficulty seeing (even if wearing glasses)")),
    (HEARING, _("Difficulty hearing (even if using a hearing aid)")),
    (WALKING, _("Difficulty walking or climbing steps")),
    (MEMORY, _("Difficulty remembering or concentrating")),
    (SELF_CARE, _("Difficulty with self care (washing, dressing)")),
    (
        COMMUNICATING,
        _("Difficulty communicating " "(e.g understanding or being understood)"),
    ),
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
RELATIONSHIP_UNKNOWN = "UNKNOWN"
RELATIONSHIP_OTHER = "OTHER"

RELATIONSHIP_CHOICE = (
    (RELATIONSHIP_UNKNOWN, "Unknown"),
    (AUNT_UNCLE, "Aunt / Uncle"),
    (BROTHER_SISTER, "Brother / Sister"),
    (COUSIN, "Cousin"),
    (DAUGHTERINLAW_SONINLAW, "Daughter-in-law / Son-in-law"),
    (GRANDDAUGHER_GRANDSON, "Granddaughter / Grandson"),
    (GRANDMOTHER_GRANDFATHER, "Grandmother / Grandfather"),
    (HEAD, "Head of household (self)"),
    (MOTHER_FATHER, "Mother / Father"),
    (MOTHERINLAW_FATHERINLAW, "Mother-in-law / Father-in-law"),
    (NEPHEW_NIECE, "Nephew / Niece"),
    (
        NON_BENEFICIARY,
        "Not a Family Member. Can only act as a recipient.",
    ),
    (RELATIONSHIP_OTHER, "Other"),
    (SISTERINLAW_BROTHERINLAW, "Sister-in-law / Brother-in-law"),
    (SON_DAUGHTER, "Son / Daughter"),
    (WIFE_HUSBAND, "Wife / Husband"),
)
YES = "1"
NO = "0"
YES_NO_CHOICE = (
    (BLANK, _("None")),
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
    (ROLE_NO_ROLE, "None"),
    (ROLE_ALTERNATE, "Alternate collector"),
    (ROLE_PRIMARY, "Primary collector"),
)
IDENTIFICATION_TYPE_BIRTH_CERTIFICATE = "BIRTH_CERTIFICATE"
IDENTIFICATION_TYPE_DRIVERS_LICENSE = "DRIVERS_LICENSE"
IDENTIFICATION_TYPE_NATIONAL_ID = "NATIONAL_ID"
IDENTIFICATION_TYPE_NATIONAL_PASSPORT = "NATIONAL_PASSPORT"
IDENTIFICATION_TYPE_ELECTORAL_CARD = "ELECTORAL_CARD"
IDENTIFICATION_TYPE_TAX_ID = "TAX_ID"
IDENTIFICATION_TYPE_RESIDENCE_PERMIT_NO = "RESIDENCE_PERMIT_NO"
IDENTIFICATION_TYPE_OTHER = "OTHER"
IDENTIFICATION_TYPE_CHOICE = (
    (IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, _("Birth Certificate")),
    (IDENTIFICATION_TYPE_DRIVERS_LICENSE, _("Driver's License")),
    (IDENTIFICATION_TYPE_ELECTORAL_CARD, _("Electoral Card")),
    (IDENTIFICATION_TYPE_NATIONAL_ID, _("National ID")),
    (IDENTIFICATION_TYPE_NATIONAL_PASSPORT, _("National Passport")),
    (IDENTIFICATION_TYPE_TAX_ID, _("Tax Number Identification")),
    (IDENTIFICATION_TYPE_RESIDENCE_PERMIT_NO, _("Foreigner's Residence Permit")),
    (IDENTIFICATION_TYPE_OTHER, _("Other")),
)
IDENTIFICATION_TYPE_DICT = {
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE: "Birth Certificate",
    IDENTIFICATION_TYPE_DRIVERS_LICENSE: "Driver's License",
    IDENTIFICATION_TYPE_ELECTORAL_CARD: "Electoral Card",
    IDENTIFICATION_TYPE_NATIONAL_ID: "National ID",
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT: "National Passport",
    IDENTIFICATION_TYPE_TAX_ID: "Tax Number Identification",
    IDENTIFICATION_TYPE_RESIDENCE_PERMIT_NO: "Foreigner's Residence Permit",
    IDENTIFICATION_TYPE_OTHER: "Other",
}
UNHCR = "UNHCR"
WFP = "WFP"
AGENCY_TYPE_CHOICES = (
    (UNHCR, _("UNHCR")),
    (WFP, _("WFP")),
)
STATUS_ACTIVE = "ACTIVE"
STATUS_INACTIVE = "INACTIVE"
STATUS_WITHDRAWN = "WITHDRAWN"
STATUS_DUPLICATE = "DUPLICATE"
INDIVIDUAL_STATUS_CHOICES = (
    (STATUS_ACTIVE, "Active"),
    (STATUS_DUPLICATE, "Duplicate"),
    (STATUS_WITHDRAWN, "Withdrawn"),
)
INDIVIDUAL_HOUSEHOLD_STATUS = ((STATUS_ACTIVE, "Active"), (STATUS_INACTIVE, "Inactive"))
UNIQUE = "UNIQUE"
DUPLICATE = "DUPLICATE"
NEEDS_ADJUDICATION = "NEEDS_ADJUDICATION"
NOT_PROCESSED = "NOT_PROCESSED"
DEDUPLICATION_POSTPONE = "POSTPONE"
DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE = (
    (DUPLICATE, "Duplicate"),
    (NEEDS_ADJUDICATION, "Needs Adjudication"),
    (NOT_PROCESSED, "Not Processed"),
    (DEDUPLICATION_POSTPONE, "Postpone"),
    (UNIQUE, "Unique"),
)
SIMILAR_IN_BATCH = "SIMILAR_IN_BATCH"
DUPLICATE_IN_BATCH = "DUPLICATE_IN_BATCH"
UNIQUE_IN_BATCH = "UNIQUE_IN_BATCH"
NOT_PROCESSED = "NOT_PROCESSED"
DEDUPLICATION_BATCH_STATUS_CHOICE = (
    (DUPLICATE_IN_BATCH, "Duplicate in batch"),
    (NOT_PROCESSED, "Not Processed"),
    (SIMILAR_IN_BATCH, "Similar in batch"),
    (UNIQUE_IN_BATCH, "Unique in batch"),
)
SOME_DIFFICULTY = "SOME_DIFFICULTY"
LOT_DIFFICULTY = "LOT_DIFFICULTY"
CANNOT_DO = "CANNOT_DO"
SEVERITY_OF_DISABILITY_CHOICES = (
    (BLANK, _("None")),
    (LOT_DIFFICULTY, "A lot of difficulty"),
    (CANNOT_DO, "Cannot do at all"),
    (SOME_DIFFICULTY, "Some difficulty"),
)
UNICEF = "UNICEF"
PARTNER = "PARTNER"
ORG_ENUMERATOR_CHOICES = (
    (BLANK, _("None")),
    (PARTNER, "Partner"),
    (UNICEF, "UNICEF"),
)
HUMANITARIAN_PARTNER = "HUMANITARIAN_PARTNER"
PRIVATE_PARTNER = "PRIVATE_PARTNER"
GOVERNMENT_PARTNER = "GOVERNMENT_PARTNER"
DATA_SHARING_CHOICES = (
    (BLANK, _("None")),
    (GOVERNMENT_PARTNER, "Government partners"),
    (HUMANITARIAN_PARTNER, "Humanitarian partners"),
    (PRIVATE_PARTNER, "Private partners"),
    (UNICEF, "UNICEF"),
)
HH_REGISTRATION = "HH_REGISTRATION"
COMMUNITY = "COMMUNITY"
REGISTRATION_METHOD_CHOICES = (
    (BLANK, _("None")),
    (COMMUNITY, "Community-level Registration"),
    (HH_REGISTRATION, "Household Registration"),
)

DISABLED = "disabled"
NOT_DISABLED = "not disabled"
DISABILITY_CHOICES = (
    (
        DISABLED,
        "disabled",
    ),
    (
        NOT_DISABLED,
        "not disabled",
    ),
)
SANCTION_LIST_POSSIBLE_MATCH = "SANCTION_LIST_POSSIBLE_MATCH"
SANCTION_LIST_CONFIRMED_MATCH = "SANCTION_LIST_CONFIRMED_MATCH"
INDIVIDUAL_FLAGS_CHOICES = (
    (DUPLICATE, "Duplicate"),
    (NEEDS_ADJUDICATION, "Needs adjudication"),
    (SANCTION_LIST_CONFIRMED_MATCH, "Sanction list match"),
    (SANCTION_LIST_POSSIBLE_MATCH, "Sanction list possible match"),
)

logger = logging.getLogger(__name__)


class Household(SoftDeletableModelWithDate, TimeStampedUUIDModel, AbstractSyncable, ConcurrencyModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "withdrawn",
            "status",
            "consent_sign",
            "consent",
            "consent_sharing",
            "residence_status",
            "country_origin",
            "country",
            "size",
            "address",
            "admin_area",
            "representatives",
            "geopoint",
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_age_group_18_59_count",
            "female_age_group_60_count",
            "pregnant_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_age_group_18_59_count",
            "male_age_group_60_count",
            "female_age_group_0_5_disabled_count",
            "female_age_group_6_11_disabled_count",
            "female_age_group_12_17_disabled_count",
            "female_age_group_18_59_disabled_count",
            "female_age_group_60_disabled_count",
            "male_age_group_0_5_disabled_count",
            "male_age_group_6_11_disabled_count",
            "male_age_group_12_17_disabled_count",
            "male_age_group_18_59_disabled_count",
            "male_age_group_60_disabled_count",
            "registration_data_import",
            "programs",
            "returnee",
            "flex_fields",
            "first_registration_date",
            "last_registration_date",
            "head_of_household",
            "fchild_hoh",
            "child_hoh",
            "unicef_id",
            "start",
            "deviceid",
            "name_enumerator",
            "org_enumerator",
            "org_name_enumerator",
            "village",
            "registration_method",
            "collect_individual_data",
            "currency",
            "unhcr_id",
            "kobo_asset_id",
            "row_id",
        ]
    )
    withdrawn = models.BooleanField(default=False, db_index=True)
    withdrawn_date = models.DateTimeField(null=True, blank=True, db_index=True)
    consent_sign = ImageField(validators=[validate_image_file_extension], blank=True)
    consent = models.BooleanField(null=True)
    consent_sharing = MultiSelectField(choices=DATA_SHARING_CHOICES, default=BLANK)
    residence_status = models.CharField(max_length=254, choices=RESIDENCE_STATUS_CHOICE)
    country_origin = CountryField(blank=True, db_index=True)
    country_origin_new = models.ForeignKey(
        "geo.Country", related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )
    country = CountryField(db_index=True)
    country_new = models.ForeignKey("geo.Country", related_name="+", blank=True, null=True, on_delete=models.PROTECT)
    size = models.PositiveIntegerField(db_index=True)
    address = CICharField(max_length=1024, blank=True)
    """location contains lowest administrative area info"""
    admin_area = models.ForeignKey("core.AdminArea", null=True, on_delete=models.SET_NULL, blank=True)
    admin_area_new = models.ForeignKey("geo.Area", null=True, on_delete=models.SET_NULL, blank=True)
    representatives = models.ManyToManyField(
        to="household.Individual",
        through="household.IndividualRoleInHousehold",
        help_text="""This is only used to track collector (primary or secondary) of a household.
            They may still be a HOH of this household or any other household.
            Through model will contain the role (ROLE_CHOICE) they are connected with on.""",
        related_name="represented_households",
    )
    geopoint = PointField(blank=True, null=True)
    female_age_group_0_5_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_6_11_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_12_17_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_18_59_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_60_count = models.PositiveIntegerField(default=None, null=True)
    pregnant_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_0_5_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_6_11_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_12_17_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_18_59_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_60_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_0_5_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_6_11_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_12_17_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_18_59_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_60_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_0_5_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_6_11_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_12_17_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_18_59_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_60_disabled_count = models.PositiveIntegerField(default=None, null=True)
    children_count = models.PositiveIntegerField(default=None, null=True)
    male_children_count = models.PositiveIntegerField(default=None, null=True)
    female_children_count = models.PositiveIntegerField(default=None, null=True)
    children_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_children_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_children_disabled_count = models.PositiveIntegerField(default=None, null=True)

    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="households",
        on_delete=models.CASCADE,
    )
    programs = models.ManyToManyField(
        "program.Program",
        related_name="households",
        blank=True,
    )
    returnee = models.BooleanField(null=True)
    flex_fields = JSONField(default=dict, blank=True)
    first_registration_date = models.DateTimeField()
    last_registration_date = models.DateTimeField()
    head_of_household = models.OneToOneField("Individual", related_name="heading_household", on_delete=models.CASCADE)
    fchild_hoh = models.BooleanField(null=True)
    child_hoh = models.BooleanField(null=True)
    unicef_id = CICharField(max_length=250, blank=True, default=BLANK, db_index=True)
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    start = models.DateTimeField(blank=True, null=True)
    deviceid = models.CharField(max_length=250, blank=True, default=BLANK)
    name_enumerator = models.CharField(max_length=250, blank=True, default=BLANK)
    org_enumerator = models.CharField(max_length=250, choices=ORG_ENUMERATOR_CHOICES, default=BLANK)
    org_name_enumerator = models.CharField(max_length=250, blank=True, default=BLANK)
    village = models.CharField(max_length=250, blank=True, default=BLANK)
    registration_method = models.CharField(max_length=250, choices=REGISTRATION_METHOD_CHOICES, default=BLANK)
    collect_individual_data = models.CharField(max_length=250, choices=YES_NO_CHOICE, default=BLANK)
    currency = models.CharField(max_length=250, choices=CURRENCY_CHOICES, default=BLANK)
    unhcr_id = models.CharField(max_length=250, blank=True, default=BLANK, db_index=True)
    user_fields = JSONField(default=dict, blank=True)
    kobo_asset_id = models.CharField(max_length=150, blank=True, default=BLANK, db_index=True)
    row_id = models.PositiveIntegerField(blank=True, null=True)
    total_cash_received_usd = models.DecimalField(
        null=True,
        decimal_places=2,
        max_digits=64,
        blank=True,
    )
    total_cash_received = models.DecimalField(
        null=True,
        decimal_places=2,
        max_digits=64,
        blank=True,
    )

    class Meta:
        verbose_name = "Household"
        permissions = (("can_withdrawn", "Can withdrawn Household"),)

    def save(self, *args, **kwargs):
        from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation

        if self.withdrawn:
            HouseholdSelection.objects.filter(
                household=self, target_population__status=TargetPopulation.STATUS_LOCKED
            ).delete()
        super().save(*args, **kwargs)

    @property
    def status(self):
        return STATUS_INACTIVE if self.withdrawn else STATUS_ACTIVE

    def withdraw(self):
        self.withdrawn = True
        self.withdrawn_date = timezone.now()
        self.save()

    def set_sys_field(self, key, value):
        if "sys" not in self.user_fields:
            self.user_fields["sys"] = {}
        self.user_fields["sys"][key] = value

    def get_sys_field(self, key):
        if "sys" in self.user_fields:
            return self.user_fields["sys"][key]
        return None

    @property
    def admin_area_title(self):
        return self.admin_area.title

    @property
    def admin1(self):
        if self.admin_area is None:
            return None
        if self.admin_area.level == 0:
            return None
        current_admin = self.admin_area
        while current_admin.level != 1:
            current_admin = current_admin.parent
        return current_admin

    @property
    def admin2(self):
        if not self.admin_area or self.admin_area.level in (0, 1):
            return None
        current_admin = self.admin_area
        while current_admin.level != 2:
            current_admin = current_admin.parent
        return current_admin

    @property
    def admin1_new(self):
        if self.admin_area_new is None:
            return None
        if self.admin_area_new.area_type.area_level == 0:
            return None
        current_admin = self.admin_area_new
        while current_admin.area_type.area_level != 1:
            current_admin = current_admin.parent
        return current_admin

    @property
    def admin2_new(self):
        if not self.admin_area_new or self.admin_area_new.area_type.area_level in (0, 1):
            return None
        current_admin = self.admin_area_new
        while current_admin.area_type.area_level != 2:
            current_admin = current_admin.parent
        return current_admin

    @property
    def sanction_list_possible_match(self):
        return self.individuals.filter(sanction_list_possible_match=True).count() > 0

    @property
    def sanction_list_confirmed_match(self):
        return self.individuals.filter(sanction_list_confirmed_match=True).count() > 0

    @property
    def total_cash_received_realtime(self):
        return (
            self.payment_records.filter()
            .aggregate(models.Sum("delivered_quantity", output_field=DecimalField()))
            .get("delivered_quantity__sum")
        )

    @property
    def total_cash_received_usd_realtime(self):
        return (
            self.payment_records.filter()
            .aggregate(models.Sum("delivered_quantity_usd", output_field=DecimalField()))
            .get("delivered_quantity_usd__sum")
        )

    @property
    def active_individuals(self):
        return self.individuals.filter(withdrawn=False, duplicate=False)

    def __str__(self):
        return f"{self.unicef_id}"


class DocumentValidator(TimeStampedUUIDModel):
    type = models.ForeignKey("DocumentType", related_name="validators", on_delete=models.CASCADE)
    regex = models.CharField(max_length=100, default=".*")


class DocumentType(TimeStampedUUIDModel):
    country = CountryField(default="U")
    country_new = models.ForeignKey("geo.Country", blank=True, null=True, on_delete=models.PROTECT)
    label = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=IDENTIFICATION_TYPE_CHOICE)

    class Meta:
        unique_together = ("country", "type")
        ordering = ["country", "label"]

    def __str__(self):
        return f"{self.label} in {self.country}"


class Document(SoftDeletableModel, TimeStampedUUIDModel):
    document_number = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    individual = models.ForeignKey("Individual", related_name="documents", on_delete=models.CASCADE)
    type = models.ForeignKey("DocumentType", related_name="documents", on_delete=models.CASCADE)
    STATUS_PENDING = "PENDING"
    STATUS_VALID = "VALID"
    STATUS_NEED_INVESTIGATION = "NEED_INVESTIGATION"
    STATUS_INVALID = "INVALID"
    STATUS_CHOICES = (
        (STATUS_PENDING, _("Pending")),
        (STATUS_VALID, _("Valid")),
        (STATUS_NEED_INVESTIGATION, _("Need Investigation")),
        (STATUS_INVALID, _("Invalid")),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    def clean(self):
        from django.core.exceptions import ValidationError

        for validator in self.type.validators.all():
            if not re.match(validator.regex, self.document_number):
                logger.error("Document number is not validating")
                raise ValidationError("Document number is not validating")

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["document_number", "type"],
                condition=Q(Q(is_removed=False) & Q(status="VALID")),
                name="unique_if_not_removed_and_valid",
            )
        ]

    def __str__(self):
        return f"{self.type} - {self.document_number}"


class Agency(models.Model):
    type = models.CharField(max_length=100, choices=AGENCY_TYPE_CHOICES)
    label = models.CharField(
        max_length=100,
    )
    country = CountryField()
    country_new = models.ForeignKey("geo.Country", blank=True, null=True, on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "Agencies"
        constraints = [
            UniqueConstraint(
                fields=["type", "country"],
                name="unique_type_and_country",
            )
        ]

    def __str__(self):
        return f"{self.label} in {self.country}"


class IndividualIdentity(models.Model):
    agency = models.ForeignKey("Agency", related_name="individual_identities", on_delete=models.CASCADE)
    individual = models.ForeignKey("Individual", related_name="identities", on_delete=models.CASCADE)
    number = models.CharField(
        max_length=255,
    )

    class Meta:
        verbose_name_plural = "Individual Identities"

    def __str__(self):
        return f"{self.agency} {self.individual} {self.number}"


class IndividualRoleInHousehold(TimeStampedUUIDModel, AbstractSyncable):
    individual = models.ForeignKey(
        "household.Individual",
        on_delete=models.CASCADE,
        related_name="households_and_roles",
    )
    household = models.ForeignKey(
        "household.Household",
        on_delete=models.CASCADE,
        related_name="individuals_and_roles",
    )
    role = models.CharField(
        max_length=255,
        blank=True,
        choices=ROLE_CHOICE,
    )

    class Meta:
        unique_together = ("role", "household")

    def __str__(self):
        return f"{self.individual.full_name} - {self.role}"


class Individual(SoftDeletableModelWithDate, TimeStampedUUIDModel, AbstractSyncable, ConcurrencyModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "status",
            "duplicate",
            "withdrawn",
            "individual_id",
            "photo",
            "full_name",
            "given_name",
            "middle_name",
            "family_name",
            "sex",
            "birth_date",
            "estimated_birth_date",
            "marital_status",
            "phone_no",
            "phone_no_alternative",
            "relationship",
            "household",
            "registration_data_import",
            "disability",
            "work_status",
            "first_registration_date",
            "last_registration_date",
            "flex_fields",
            "enrolled_in_nutrition_programme",
            "administration_of_rutf",
            "unicef_id",
            "deduplication_golden_record_status",
            "deduplication_batch_status",
            "deduplication_golden_record_results",
            "deduplication_batch_results",
            "imported_individual_id",
            "sanction_list_possible_match",
            "sanction_list_confirmed_match",
            "sanction_list_last_check",
            "pregnant",
            "observed_disability",
            "seeing_disability",
            "hearing_disability",
            "physical_disability",
            "memory_disability",
            "selfcare_disability",
            "comms_disability",
            "who_answers_phone",
            "who_answers_alt_phone",
            "kobo_asset_id",
            "row_id",
        ]
    )
    duplicate = models.BooleanField(default=False, db_index=True)
    duplicate_date = models.DateTimeField(null=True, blank=True)
    withdrawn = models.BooleanField(default=False, db_index=True)
    withdrawn_date = models.DateTimeField(null=True, blank=True)
    individual_id = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    full_name = CICharField(max_length=255, validators=[MinLengthValidator(2)], db_index=True)
    given_name = CICharField(max_length=85, blank=True, db_index=True)
    middle_name = CICharField(max_length=85, blank=True, db_index=True)
    family_name = CICharField(max_length=85, blank=True, db_index=True)
    sex = models.CharField(max_length=255, choices=SEX_CHOICE, db_index=True)
    birth_date = models.DateField(db_index=True)
    estimated_birth_date = models.BooleanField(default=False)
    marital_status = models.CharField(max_length=255, choices=MARITAL_STATUS_CHOICE, default=BLANK, db_index=True)
    phone_no = PhoneNumberField(blank=True, db_index=True)
    phone_no_alternative = PhoneNumberField(blank=True, db_index=True)
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
        "registration_data.RegistrationDataImport",
        related_name="individuals",
        on_delete=models.CASCADE,
        null=True,
    )
    disability = models.CharField(max_length=20, choices=DISABILITY_CHOICES, default=NOT_DISABLED)
    work_status = models.CharField(
        max_length=20,
        choices=WORK_STATUS_CHOICE,
        blank=True,
        default=NOT_PROVIDED,
    )
    first_registration_date = models.DateField()
    last_registration_date = models.DateField()
    flex_fields = JSONField(default=dict, blank=True)
    user_fields = JSONField(default=dict, blank=True)
    enrolled_in_nutrition_programme = models.BooleanField(null=True)
    administration_of_rutf = models.BooleanField(null=True)
    unicef_id = CICharField(max_length=250, blank=True, db_index=True)
    deduplication_golden_record_status = models.CharField(
        max_length=50,
        default=UNIQUE,
        choices=DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
    )
    deduplication_batch_status = models.CharField(
        max_length=50,
        default=UNIQUE_IN_BATCH,
        choices=DEDUPLICATION_BATCH_STATUS_CHOICE,
    )
    deduplication_golden_record_results = JSONField(default=dict, blank=True)
    deduplication_batch_results = JSONField(default=dict, blank=True)
    imported_individual_id = models.UUIDField(null=True, blank=True)
    sanction_list_possible_match = models.BooleanField(default=False, db_index=True)
    sanction_list_confirmed_match = models.BooleanField(default=False, db_index=True)
    pregnant = models.BooleanField(null=True)
    observed_disability = MultiSelectField(choices=OBSERVED_DISABILITY_CHOICE, default=NONE)
    seeing_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    hearing_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    physical_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    memory_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    selfcare_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    comms_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    who_answers_phone = models.CharField(max_length=150, blank=True)
    who_answers_alt_phone = models.CharField(max_length=150, blank=True)
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    fchild_hoh = models.BooleanField(default=False)
    child_hoh = models.BooleanField(default=False)
    kobo_asset_id = models.CharField(max_length=150, blank=True, default=BLANK)
    row_id = models.PositiveIntegerField(blank=True, null=True)
    disability_certificate_picture = models.ImageField(blank=True, null=True)

    @property
    def phone_no_valid(self):
        return is_right_phone_number_format(self.phone_no)

    @property
    def phone_no_alternative_valid(self):
        return is_right_phone_number_format(self.phone_no_alternative)

    @property
    def age(self):
        return relativedelta(date.today(), self.birth_date).years

    @property
    def role(self):
        role = self.households_and_roles.first()
        return role.role if role is not None else ROLE_NO_ROLE

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

    @property
    def status(self):
        statuses = []
        if self.duplicate:
            statuses.append(STATUS_DUPLICATE)
        if self.withdrawn:
            statuses.append(STATUS_WITHDRAWN)
        if len(statuses) > 0:
            return ", ".join(statuses)
        return STATUS_ACTIVE

    @property
    def cash_assist_status(self):
        return STATUS_INACTIVE if self.withdrawn or self.duplicate else STATUS_ACTIVE

    @property
    def sanction_list_last_check(self):
        return cache.get("sanction_list_last_check")

    def withdraw(self):
        self.withdrawn = True
        self.withdrawn_date = timezone.now()
        self.save()

    def mark_as_duplicate(self, original_individual=None):
        if original_individual is not None:
            self.unicef_id = original_individual.unicef_id
        self.documents.update(status=Document.STATUS_INVALID)
        self.duplicate = True
        self.duplicate_date = timezone.now()
        self.save()

    def __str__(self):
        return self.unicef_id

    class Meta:
        verbose_name = "Individual"

    def set_sys_field(self, key, value):
        if "sys" not in self.user_fields:
            self.user_fields["sys"] = {}
        self.user_fields["sys"][key] = value

    def get_sys_field(self, key):
        if "sys" in self.user_fields:
            return self.user_fields["sys"][key]
        return None

    def recalculate_data(self):
        disability_fields = (
            "seeing_disability",
            "hearing_disability",
            "physical_disability",
            "memory_disability",
            "selfcare_disability",
            "comms_disability",
        )
        should_be_disabled = self.disability == DISABLED
        for field in disability_fields:
            value = getattr(self, field, None)
            should_be_disabled = should_be_disabled or value == CANNOT_DO or value == LOT_DIFFICULTY
        self.disability = DISABLED if should_be_disabled else NOT_DISABLED
        self.save(update_fields=["disability"])

    def count_all_roles(self):
        return self.households_and_roles.exclude(role=ROLE_NO_ROLE).count()

    def count_primary_roles(self):
        return self.households_and_roles.filter(role=ROLE_PRIMARY).count()

    @cached_property
    def parents(self):
        return self.household.individuals.exclude(Q(duplicate=True) | Q(withdrawn=True)) if self.household else []

    def is_golden_record_duplicated(self):
        return self.deduplication_golden_record_status == DUPLICATE

    def get_deduplication_golden_record(self):
        status_key = "duplicates" if self.is_golden_record_duplicated() else "possible_duplicates"
        return self.deduplication_golden_record_results.get(status_key, [])

    @cached_property
    def active_record(self):
        if self.duplicate:
            return Individual.objects.filter(unicef_id=self.unicef_id, duplicate=False, is_removed=False).first()

    def is_head(self):
        if not self.household:
            return False
        return self.household.head_of_household.id == self.id


class EntitlementCard(TimeStampedUUIDModel):
    ACTIVE = "ACTIVE"
    ERRONEOUS = "ERRONEOUS"
    CLOSED = "CLOSED"
    STATUS_CHOICE = Choices(
        (ACTIVE, _("Active")),
        (ERRONEOUS, _("Erroneous")),
        (CLOSED, _("Closed")),
    )
    card_number = models.CharField(max_length=255)
    status = models.CharField(
        choices=STATUS_CHOICE,
        default=ACTIVE,
        max_length=10,
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


class XlsxUpdateFile(TimeStampedUUIDModel):
    file = models.FileField()
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    rdi = models.ForeignKey("registration_data.RegistrationDataImport", on_delete=models.CASCADE, null=True)
    xlsx_match_columns = ArrayField(models.CharField(max_length=32), null=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.PROTECT)


class BankAccountInfo(SoftDeletableModelWithDate, TimeStampedUUIDModel, AbstractSyncable):
    individual = models.ForeignKey("household.Individual", related_name="bank_account_info", on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=64)
    debit_card_number = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"{self.bank_account_number} ({self.bank_name})"

    def save(self, *args, **kwargs):
        if self.bank_account_number:
            self.bank_account_number = str(self.bank_account_number).replace(" ", "")
        if self.debit_card_number:
            self.debit_card_number = str(self.debit_card_number).replace(" ", "")
        super().save(*args, **kwargs)
