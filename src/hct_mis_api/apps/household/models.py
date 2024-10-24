import logging
import re
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from django.conf import settings
from django.contrib.gis.db.models import PointField, Q, UniqueConstraint
from django.contrib.postgres.fields import ArrayField, CICharField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.cache import cache
from django.core.validators import MinLengthValidator, validate_image_file_extension
from django.db import models
from django.db.models import BooleanField, F, Func, JSONField, QuerySet, Value
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from dateutil.relativedelta import relativedelta
from model_utils import Choices
from model_utils.models import TimeStampedModel
from multiselectfield import MultiSelectField
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES
from hct_mis_api.apps.core.languages import Languages
from hct_mis_api.apps.core.models import BusinessArea, StorageFile
from hct_mis_api.apps.core.utils import FlexFieldsEncoder
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.signals import (
    household_deleted,
    household_withdrawn,
    individual_deleted,
    individual_withdrawn,
)
from hct_mis_api.apps.utils.models import (
    AbstractSyncable,
    AdminUrlMixin,
    ConcurrencyModel,
    MergeStatusModel,
    RepresentationManager,
    SoftDeletableRepresentationMergeStatusModel,
    SoftDeletableRepresentationMergeStatusModelWithDate,
    SoftDeletableRepresentationPendingManager,
    TimeStampedUUIDModel,
    UnicefIdentifiedModel,
)
from hct_mis_api.apps.utils.phone import (
    calculate_phone_numbers_validity,
    recalculate_phone_numbers_validity,
)

if TYPE_CHECKING:
    from hct_mis_api.contrib.aurora.models import Record

BLANK = ""
IDP = "IDP"
REFUGEE = "REFUGEE"
OTHERS_OF_CONCERN = "OTHERS_OF_CONCERN"
HOST = "HOST"
NON_HOST = "NON_HOST"
RETURNEE = "RETURNEE"
RESIDENCE_STATUS_CHOICE = (
    (BLANK, _("None")),
    (IDP, _("Displaced  |  Internally Displaced People")),
    (REFUGEE, _("Displaced  |  Refugee / Asylum Seeker")),
    (OTHERS_OF_CONCERN, _("Displaced  |  Others of Concern")),
    (HOST, _("Non-displaced  |   Host")),
    (NON_HOST, _("Non-displaced  |   Non-host")),
    (RETURNEE, _("Displaced  |   Returnee")),
)
# INDIVIDUALS
MALE = "MALE"
FEMALE = "FEMALE"
UNKNOWN = "UNKNOWN"

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
GRANDDAUGHTER_GRANDSON = "GRANDDAUGHER_GRANDSON"  # key is wrong, but it is used in kobo and aurora
NEPHEW_NIECE = "NEPHEW_NIECE"
COUSIN = "COUSIN"
FOSTER_CHILD = "FOSTER_CHILD"
RELATIONSHIP_UNKNOWN = "UNKNOWN"
RELATIONSHIP_OTHER = "OTHER"
FREE_UNION = "FREE_UNION"

RELATIONSHIP_CHOICE = (
    (RELATIONSHIP_UNKNOWN, "Unknown"),
    (AUNT_UNCLE, "Aunt / Uncle"),
    (BROTHER_SISTER, "Brother / Sister"),
    (COUSIN, "Cousin"),
    (DAUGHTERINLAW_SONINLAW, "Daughter-in-law / Son-in-law"),
    (GRANDDAUGHTER_GRANDSON, "Granddaughter / Grandson"),
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
    (FOSTER_CHILD, "Foster child"),
    (FREE_UNION, "Free union"),
)
YES = "1"
NO = "0"
YES_NO_CHOICE = (
    (BLANK, _("None")),
    (YES, _("Yes")),
    (NO, _("No")),
)

COLLECT_TYPE_UNKNOWN = ""
COLLECT_TYPE_NONE = "0"
COLLECT_TYPE_FULL = "1"
COLLECT_TYPE_PARTIAL = "2"
COLLECT_TYPE_SIZE_ONLY = "3"

COLLECT_TYPES = (
    (COLLECT_TYPE_UNKNOWN, _("Unknown")),
    (COLLECT_TYPE_PARTIAL, _("Partial individuals collected")),
    (COLLECT_TYPE_FULL, _("Full individual collected")),
    (COLLECT_TYPE_SIZE_ONLY, _("Size only collected")),
    (COLLECT_TYPE_NONE, _("No individual data")),
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
IDENTIFICATION_TYPE_BANK_STATEMENT = "BANK_STATEMENT"
IDENTIFICATION_TYPE_DISABILITY_CERTIFICATE = "DISABILITY_CERTIFICATE"
IDENTIFICATION_TYPE_FOSTER_CHILD = "FOSTER_CHILD"
IDENTIFICATION_TYPE_OTHER = "OTHER"
IDENTIFICATION_TYPE_CHOICE = (
    (IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, _("Birth Certificate")),
    (IDENTIFICATION_TYPE_DRIVERS_LICENSE, _("Driver's License")),
    (IDENTIFICATION_TYPE_ELECTORAL_CARD, _("Electoral Card")),
    (IDENTIFICATION_TYPE_NATIONAL_ID, _("National ID")),
    (IDENTIFICATION_TYPE_NATIONAL_PASSPORT, _("National Passport")),
    (IDENTIFICATION_TYPE_TAX_ID, _("Tax Number Identification")),
    (IDENTIFICATION_TYPE_RESIDENCE_PERMIT_NO, _("Foreigner's Residence Permit")),
    (IDENTIFICATION_TYPE_BANK_STATEMENT, _("Bank Statement")),
    (IDENTIFICATION_TYPE_DISABILITY_CERTIFICATE, _("Disability Certificate")),
    (IDENTIFICATION_TYPE_FOSTER_CHILD, _("Foster Child")),
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


class HouseholdCollection(UnicefIdentifiedModel):
    """
    Collection of household representations.
    """

    def __str__(self) -> str:
        return self.unicef_id or ""

    @property
    def business_area(self) -> Optional[BusinessArea]:
        return self.households.first().business_area if self.households.first() else None


class Household(
    SoftDeletableRepresentationMergeStatusModelWithDate,
    TimeStampedUUIDModel,
    AbstractSyncable,
    ConcurrencyModel,
    UnicefIdentifiedModel,
    AdminUrlMixin,
):
    class CollectType(models.TextChoices):
        STANDARD = "STANDARD", "Standard"
        SINGLE = "SINGLE", "Single"

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
            "zip_code",
            "size",
            "address",
            "admin_area",
            "admin1",
            "admin2",
            "admin3",
            "admin4",
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
            "detail_id",
            "registration_id",
            "program_registration_id",
        ]
    )
    household_collection = models.ForeignKey(
        HouseholdCollection,
        related_name="households",
        on_delete=models.CASCADE,
        null=True,
    )
    withdrawn = models.BooleanField(default=False, db_index=True)
    withdrawn_date = models.DateTimeField(null=True, blank=True, db_index=True)
    consent_sign = ImageField(validators=[validate_image_file_extension], blank=True)
    consent = models.BooleanField(null=True)
    consent_sharing = MultiSelectField(choices=DATA_SHARING_CHOICES, default=BLANK)
    residence_status = models.CharField(max_length=254, choices=RESIDENCE_STATUS_CHOICE, blank=True)

    country_origin = models.ForeignKey("geo.Country", related_name="+", blank=True, null=True, on_delete=models.PROTECT)
    country = models.ForeignKey("geo.Country", related_name="+", blank=True, null=True, on_delete=models.PROTECT)
    address = CICharField(max_length=1024, blank=True)
    zip_code = models.CharField(max_length=12, blank=True, null=True)
    """location contains lowest administrative area info"""
    admin_area = models.ForeignKey("geo.Area", null=True, on_delete=models.SET_NULL, blank=True)
    admin1 = models.ForeignKey("geo.Area", null=True, on_delete=models.SET_NULL, blank=True, related_name="+")
    admin2 = models.ForeignKey("geo.Area", null=True, on_delete=models.SET_NULL, blank=True, related_name="+")
    admin3 = models.ForeignKey("geo.Area", null=True, on_delete=models.SET_NULL, blank=True, related_name="+")
    admin4 = models.ForeignKey("geo.Area", null=True, on_delete=models.SET_NULL, blank=True, related_name="+")
    geopoint = PointField(blank=True, null=True)

    size = models.PositiveIntegerField(db_index=True, null=True, blank=True)
    representatives = models.ManyToManyField(
        to="household.Individual",
        through="household.IndividualRoleInHousehold",
        help_text="""This is only used to track collector (primary or secondary) of a household.
            They may still be a HOH of this household or any other household.
            Through model will contain the role (ROLE_CHOICE) they are connected with on.""",
        related_name="represented_households",
    )
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
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    programs = models.ManyToManyField(
        "program.Program",
        related_name="households",
        blank=True,
    )  # TODO: remove after migration
    returnee = models.BooleanField(null=True)
    flex_fields = JSONField(default=dict, blank=True)
    first_registration_date = models.DateTimeField()
    last_registration_date = models.DateTimeField()
    head_of_household = models.OneToOneField(
        "Individual", related_name="heading_household", on_delete=models.CASCADE, null=True
    )
    fchild_hoh = models.BooleanField(null=True)
    child_hoh = models.BooleanField(null=True)
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    start = models.DateTimeField(blank=True, null=True)
    deviceid = models.CharField(max_length=250, blank=True, default=BLANK)
    name_enumerator = models.CharField(max_length=250, blank=True, default=BLANK)
    org_enumerator = models.CharField(max_length=250, choices=ORG_ENUMERATOR_CHOICES, default=BLANK)
    org_name_enumerator = models.CharField(max_length=250, blank=True, default=BLANK)
    village = models.CharField(max_length=250, blank=True, default=BLANK)
    registration_method = models.CharField(max_length=250, choices=REGISTRATION_METHOD_CHOICES, default=BLANK)
    collect_individual_data = models.CharField(max_length=250, choices=COLLECT_TYPES, default=COLLECT_TYPE_UNKNOWN)
    currency = models.CharField(max_length=250, choices=CURRENCY_CHOICES, default=BLANK)
    unhcr_id = models.CharField(max_length=250, blank=True, default=BLANK, db_index=True)
    user_fields = JSONField(default=dict, blank=True)
    detail_id = models.CharField(
        max_length=150, blank=True, null=True, help_text="Kobo asset ID, Xlsx row ID, Aurora source ID"
    )
    registration_id = CICharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        verbose_name=_("Aurora Registration Id"),
    )
    program_registration_id = CICharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        unique=True,
        verbose_name=_("Beneficiary Program Registration Id"),
    )
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

    family_id = models.CharField(max_length=100, blank=True, null=True)  # eDopomoga household id
    storage_obj = models.ForeignKey(StorageFile, on_delete=models.SET_NULL, blank=True, null=True)
    program = models.ForeignKey(
        "program.Program", null=True, blank=True, db_index=True, on_delete=models.SET_NULL
    )  # TODO Add later related name, when no clash with programs, set null=False after migration
    copied_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="copied_to",
        help_text="If this household was copied from another household, "
        "this field will contain the household it was copied from.",
    )
    origin_unicef_id = models.CharField(max_length=100, blank=True, null=True)
    is_migration_handled = models.BooleanField(default=False)
    migrated_at = models.DateTimeField(null=True, blank=True)
    is_recalculated_group_ages = models.BooleanField(default=False)  # TODO remove after migration
    collect_type = models.CharField(choices=CollectType.choices, default=CollectType.STANDARD.value, max_length=8)

    kobo_submission_uuid = models.UUIDField(null=True, default=None)
    kobo_submission_time = models.DateTimeField(max_length=150, blank=True, null=True)
    enumerator_rec_id = models.PositiveIntegerField(blank=True, null=True)
    mis_unicef_id = models.CharField(max_length=255, null=True)
    flex_registrations_record_id = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "Household"
        permissions = (("can_withdrawn", "Can withdrawn Household"),)

    def save(self, *args: Any, **kwargs: Any) -> None:
        from hct_mis_api.apps.targeting.models import (
            HouseholdSelection,
            TargetPopulation,
        )

        if self.withdrawn:
            HouseholdSelection.objects.filter(
                household=self, target_population__status=TargetPopulation.STATUS_LOCKED
            ).delete()
        cache.delete_pattern(f"count_{self.business_area.slug}_HouseholdNodeConnection_*")
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> Tuple[int, Dict[str, int]]:
        household_deleted.send(self.__class__, instance=self)
        return super().delete(*args, **kwargs)

    @property
    def status(self) -> str:
        return STATUS_INACTIVE if self.withdrawn else STATUS_ACTIVE

    def withdraw(self, tag: Optional[Any] = None) -> None:
        self.withdrawn = True
        self.withdrawn_date = timezone.now()
        user_fields = self.user_fields or {}
        user_fields["withdrawn_tag"] = tag
        self.user_fields = user_fields
        self.save()
        household_withdrawn.send(sender=self.__class__, instance=self)

    def unwithdraw(self) -> None:
        self.withdrawn = False
        self.withdrawn_date = None
        self.save()

    def set_sys_field(self, key: str, value: Any) -> None:
        if "sys" not in self.user_fields:
            self.user_fields["sys"] = {}
        self.user_fields["sys"][key] = value

    def get_sys_field(self, key: str) -> Any:
        if "sys" in self.user_fields:
            return self.user_fields["sys"][key]
        return None

    def set_admin_areas(self, new_admin_area: Optional[Area] = None, save: bool = True) -> None:
        """Propagates admin1,2,3,4 based on admin_area parents"""
        admins = ["admin1", "admin2", "admin3", "admin4"]

        if not new_admin_area:
            new_admin_area = self.admin_area
        else:
            self.admin_area = new_admin_area
        if not new_admin_area:
            return
        for admin in admins:
            setattr(self, admin, None)

        new_admin_area_level = new_admin_area.area_type.area_level if new_admin_area else 4  # lowest possible level

        for admin_level in reversed(range(1, new_admin_area_level + 1)):
            setattr(self, f"admin{admin_level}", new_admin_area)
            new_admin_area = getattr(new_admin_area, "parent", None)

        if save:
            self.save(update_fields=["admin_area"] + admins)

    @property
    def sanction_list_possible_match(self) -> bool:
        return self.individuals.filter(sanction_list_possible_match=True).count() > 0

    @property
    def sanction_list_confirmed_match(self) -> bool:
        return self.individuals.filter(sanction_list_confirmed_match=True).count() > 0

    @property
    def active_individuals(self) -> QuerySet:
        return self.individuals.filter(withdrawn=False, duplicate=False)

    @cached_property
    def primary_collector(self) -> Optional["Individual"]:
        return self.representatives.get(households_and_roles__role=ROLE_PRIMARY)

    @cached_property
    def alternate_collector(self) -> Optional["Individual"]:
        return self.representatives.filter(households_and_roles__role=ROLE_ALTERNATE).first()

    @property
    def flex_registrations_record(self) -> Optional["Record"]:
        from hct_mis_api.contrib.aurora.models import Record

        return Record.objects.filter(id=self.flex_registrations_record_id).first()

    def __str__(self) -> str:
        return self.unicef_id or ""

    def can_be_erase(self) -> bool:
        yesterday = timezone.now() - timedelta(days=1)
        conditions = [
            self.is_removed,
            self.withdrawn,
            self.removed_date >= yesterday,
            self.withdrawn_date >= yesterday,
        ]
        return all(conditions)

    def erase(self) -> None:
        for individual in self.individuals.all():
            individual.erase()

        self.flex_fields = {}
        self.save()


class DocumentValidator(TimeStampedUUIDModel):
    type = models.ForeignKey("DocumentType", related_name="validators", on_delete=models.CASCADE)
    regex = models.CharField(max_length=100, default=".*")


class DocumentType(TimeStampedUUIDModel):
    label = models.CharField(max_length=100)
    key = models.CharField(max_length=50, unique=True)
    is_identity_document = models.BooleanField(default=True)
    unique_for_individual = models.BooleanField(default=False)
    valid_for_deduplication = models.BooleanField(default=False)

    class Meta:
        ordering = [
            "label",
        ]

    def __str__(self) -> str:
        return f"{self.label}"


class Document(AbstractSyncable, SoftDeletableRepresentationMergeStatusModel, TimeStampedUUIDModel):
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

    document_number = models.CharField(max_length=255, blank=True, db_index=True)
    photo = models.ImageField(blank=True)
    individual = models.ForeignKey("Individual", related_name="documents", on_delete=models.CASCADE)
    type = models.ForeignKey("DocumentType", related_name="documents", on_delete=models.CASCADE)
    country = models.ForeignKey("geo.Country", blank=True, null=True, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    cleared = models.BooleanField(default=False)
    cleared_date = models.DateTimeField(default=timezone.now)
    cleared_by = models.ForeignKey("account.User", null=True, on_delete=models.SET_NULL)
    issuance_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True, db_index=True)
    program = models.ForeignKey("program.Program", null=True, related_name="+", on_delete=models.CASCADE)

    is_migration_handled = models.BooleanField(default=False)
    copied_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="copied_to",
        help_text="If this object was copied from another, this field will contain the object it was copied from.",
    )

    def clean(self) -> None:
        from django.core.exceptions import ValidationError

        for validator in self.type.validators.all():
            if not re.match(validator.regex, self.document_number):
                logger.error("Document number is not validating")
                raise ValidationError("Document number is not validating")

    class Meta:
        constraints = [
            # if document_type.unique_for_individual=True then document of this type must be unique for an individual
            # is_original = True -> 1 original instance of document
            # is_original = False -> 1 representation of document per program
            UniqueConstraint(
                fields=["individual", "type", "country", "program"],
                condition=Q(
                    Q(is_removed=False)
                    & Q(status="VALID")
                    & Func(
                        F("type_id"),
                        Value(True),
                        function="check_unique_document_for_individual",
                        output_field=BooleanField(),
                    )
                ),
                name="unique_for_individual_if_not_removed_and_valid",
            ),
            # document_number must be unique across all documents of the same type
            UniqueConstraint(
                fields=["document_number", "type", "country", "program", "is_original"],
                condition=Q(Q(is_removed=False) & Q(status="VALID") & Q(rdi_merge_status=MergeStatusModel.MERGED)),
                name="unique_if_not_removed_and_valid_for_representations",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.type} - {self.document_number}"

    def mark_as_need_investigation(self) -> None:
        self.status = self.STATUS_NEED_INVESTIGATION

    def mark_as_valid(self) -> None:
        self.status = self.STATUS_VALID

    def erase(self) -> None:
        self.is_removed = True
        self.photo = ""
        self.document_number = "GDPR REMOVED"
        self.save()


class IndividualIdentity(SoftDeletableRepresentationMergeStatusModel, TimeStampedModel):
    # notice that this model has `created` and `modified` fields
    individual = models.ForeignKey("Individual", related_name="identities", on_delete=models.CASCADE)
    number = models.CharField(
        max_length=255,
    )
    partner = models.ForeignKey(
        "account.Partner",
        related_name="individual_identities",
        null=True,
        on_delete=models.PROTECT,
    )
    country = models.ForeignKey("geo.Country", null=True, on_delete=models.PROTECT)
    is_migration_handled = models.BooleanField(default=False)
    copied_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="copied_to",
        help_text="If this object was copied from another, this field will contain the object it was copied from.",
    )

    class Meta:
        verbose_name_plural = "Individual Identities"

    def __str__(self) -> str:
        return f"{self.partner} {self.individual} {self.number}"


class IndividualRoleInHousehold(SoftDeletableRepresentationMergeStatusModel, TimeStampedUUIDModel, AbstractSyncable):
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
    is_migration_handled = models.BooleanField(default=False)
    migrated_at = models.DateTimeField(null=True, blank=True)
    copied_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="copied_to",
        help_text="If this object was copied from another, this field will contain the object it was copied from.",
    )

    class Meta:
        unique_together = [("role", "household"), ("household", "individual")]

    def __str__(self) -> str:
        return f"{self.individual.full_name} - {self.role}"


class IndividualCollection(UnicefIdentifiedModel):
    """
    Collection of individual representations.
    """

    def __str__(self) -> str:
        return self.unicef_id or ""

    @property
    def business_area(self) -> Optional[BusinessArea]:
        return self.individuals.first().business_area if self.individuals.first() else None


class Individual(
    SoftDeletableRepresentationMergeStatusModelWithDate,
    TimeStampedUUIDModel,
    AbstractSyncable,
    ConcurrencyModel,
    UnicefIdentifiedModel,
    AdminUrlMixin,
):
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
            "detail_id",
            "registration_id",
            "program_registration_id",
            "payment_delivery_phone_no",
        ]
    )
    individual_collection = models.ForeignKey(
        IndividualCollection,
        related_name="individuals",
        on_delete=models.CASCADE,
        null=True,
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
    phone_no_valid = models.BooleanField(null=True, db_index=True)
    phone_no_alternative = PhoneNumberField(blank=True, db_index=True)
    phone_no_alternative_valid = models.BooleanField(null=True, db_index=True)
    email = models.CharField(max_length=255, blank=True)
    payment_delivery_phone_no = PhoneNumberField(blank=True, null=True)

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
    )
    work_status = models.CharField(
        max_length=20,
        choices=WORK_STATUS_CHOICE,
        blank=True,
        default=NOT_PROVIDED,
    )
    first_registration_date = models.DateField()
    last_registration_date = models.DateField()
    flex_fields = JSONField(default=dict, blank=True, encoder=FlexFieldsEncoder)
    user_fields = JSONField(default=dict, blank=True)
    enrolled_in_nutrition_programme = models.BooleanField(null=True)
    administration_of_rutf = models.BooleanField(null=True)
    deduplication_golden_record_status = models.CharField(
        max_length=50,
        default=UNIQUE,
        choices=DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
        db_index=True,
    )
    deduplication_batch_status = models.CharField(
        max_length=50,
        default=UNIQUE_IN_BATCH,
        choices=DEDUPLICATION_BATCH_STATUS_CHOICE,
        db_index=True,
    )
    deduplication_golden_record_results = JSONField(default=dict, blank=True)
    deduplication_batch_results = JSONField(default=dict, blank=True)
    imported_individual_id = models.UUIDField(null=True, blank=True)
    sanction_list_possible_match = models.BooleanField(default=False, db_index=True)
    sanction_list_confirmed_match = models.BooleanField(default=False, db_index=True)
    pregnant = models.BooleanField(null=True)

    disability = models.CharField(max_length=20, choices=DISABILITY_CHOICES, default=NOT_DISABLED)
    observed_disability = MultiSelectField(choices=OBSERVED_DISABILITY_CHOICE, default=NONE)
    disability_certificate_picture = models.ImageField(blank=True, null=True)

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
    detail_id = models.CharField(
        max_length=150, blank=True, null=True, help_text="Kobo asset ID, Xlsx row ID, Aurora source ID"
    )
    registration_id = CICharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Aurora Registration Id"),
    )
    program_registration_id = CICharField(
        max_length=100, blank=True, null=True, verbose_name=_("Beneficiary Program Registration Id")
    )
    preferred_language = models.CharField(max_length=6, choices=Languages.get_tuple(), null=True, blank=True)
    relationship_confirmed = models.BooleanField(default=False)
    age_at_registration = models.PositiveSmallIntegerField(null=True, blank=True)
    wallet_name = models.CharField(max_length=64, blank=True, default="")
    blockchain_name = models.CharField(max_length=64, blank=True, default="")
    wallet_address = models.CharField(max_length=128, blank=True, default="")

    program = models.ForeignKey(
        "program.Program", null=True, blank=True, db_index=True, related_name="individuals", on_delete=models.SET_NULL
    )  # TODO set null=False after migration
    copied_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        db_index=True,
        related_name="copied_to",
        on_delete=models.SET_NULL,
        help_text="If this individual was copied from another individual, "
        "this field will contain the individual it was copied from.",
    )
    origin_unicef_id = models.CharField(max_length=100, blank=True, null=True)
    is_migration_handled = models.BooleanField(default=False)
    migrated_at = models.DateTimeField(null=True, blank=True)
    mis_unicef_id = models.CharField(max_length=255, null=True)

    vector_column = SearchVectorField(null=True)

    def delete(self, *args: Any, **kwargs: Any) -> Tuple[int, Dict[str, int]]:
        individual_deleted.send(self.__class__, instance=self)
        return super().delete(*args, **kwargs)

    @property
    def phone_no_text(self) -> str:
        return str(self.phone_no).replace(" ", "")

    @property
    def phone_no_alternative_text(self) -> str:
        return str(self.phone_no_alternative).replace(" ", "")

    @property
    def age(self) -> int:
        return relativedelta(date.today(), self.birth_date).years

    @property
    def role(self) -> str:
        role = self.households_and_roles.first()
        return role.role if role is not None else ROLE_NO_ROLE

    @property
    def get_hash_key(self) -> str:
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
    def status(self) -> str:
        statuses = []
        if self.duplicate:
            statuses.append(STATUS_DUPLICATE)
        if self.withdrawn:
            statuses.append(STATUS_WITHDRAWN)
        if len(statuses) > 0:
            return ", ".join(statuses)
        return STATUS_ACTIVE

    @property
    def cash_assist_status(self) -> str:
        return STATUS_INACTIVE if self.withdrawn or self.duplicate else STATUS_ACTIVE

    @property
    def sanction_list_last_check(self) -> Optional[datetime]:
        if self.business_area.should_check_against_sanction_list():
            return cache.get("sanction_list_last_check")
        return None

    @property
    def bank_name(self) -> str:
        bank_account_info = self.bank_account_info.first()
        return bank_account_info.bank_name if bank_account_info else None

    @property
    def bank_account_number(self) -> str:
        bank_account_info = self.bank_account_info.first()
        return bank_account_info.bank_account_number if bank_account_info else None

    @property
    def account_holder_name(self) -> str:
        bank_account_info = self.bank_account_info.first()
        return bank_account_info.account_holder_name if bank_account_info else None

    @property
    def bank_branch_name(self) -> str:
        bank_account_info = self.bank_account_info.first()
        return bank_account_info.bank_branch_name if bank_account_info else None

    def withdraw(self) -> None:
        self.documents.update(status=Document.STATUS_INVALID)
        self.withdrawn = True
        self.withdrawn_date = timezone.now()
        self.save()
        individual_withdrawn.send(sender=self.__class__, instance=self)

    def unwithdraw(self) -> None:
        self.documents.update(status=Document.STATUS_NEED_INVESTIGATION)
        self.withdrawn = False
        self.withdrawn_date = None
        self.save()

    def mark_as_duplicate(self, original_individual: Optional["Individual"] = None) -> None:
        if original_individual is not None:
            self.unicef_id = str(original_individual.unicef_id)
        self.documents.update(status=Document.STATUS_INVALID)
        self.duplicate = True
        self.duplicate_date = timezone.now()
        self.save()

    def mark_as_distinct(self) -> None:
        self.documents.update(status=Document.STATUS_VALID)
        self.duplicate = False
        self.duplicate_date = timezone.now()
        self.save()

    def set_relationship_confirmed_flag(self, confirmed: bool) -> None:
        self.relationship_confirmed = confirmed
        self.save(update_fields=["relationship_confirmed"])

    def __str__(self) -> str:
        return self.unicef_id or ""

    class Meta:
        verbose_name = "Individual"
        indexes = (GinIndex(fields=["vector_column"]),)

    def set_sys_field(self, key: str, value: Any) -> None:
        if "sys" not in self.user_fields:
            self.user_fields["sys"] = {}
        self.user_fields["sys"][key] = value

    def get_sys_field(self, key: str) -> Any:
        if "sys" in self.user_fields:
            return self.user_fields["sys"][key]
        return None

    def recalculate_data(self, save: bool = True) -> Tuple[Any, List[str]]:
        update_fields = ["disability"]

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

        if save:
            self.save(update_fields=update_fields)

        return self, update_fields

    def count_all_roles(self) -> int:
        return self.households_and_roles.exclude(role=ROLE_NO_ROLE).count()

    def count_primary_roles(self) -> int:
        return self.households_and_roles.filter(role=ROLE_PRIMARY).count()

    @cached_property
    def parents(self) -> List["Individual"]:
        return self.household.individuals.exclude(Q(duplicate=True) | Q(withdrawn=True)) if self.household else []

    def is_golden_record_duplicated(self) -> bool:
        return self.deduplication_golden_record_status == DUPLICATE

    def get_deduplication_golden_record(self) -> List:
        status_key = "duplicates" if self.is_golden_record_duplicated() else "possible_duplicates"
        return self.deduplication_golden_record_results.get(status_key, [])

    @cached_property
    def active_record(self) -> Optional["Individual"]:
        if self.duplicate:
            return Individual.objects.filter(unicef_id=self.unicef_id, duplicate=False, is_removed=False).first()
        return None

    def is_head(self) -> bool:
        if not self.household:
            return False
        return self.household.head_of_household.id == self.id

    def erase(self) -> None:
        for document in self.documents.all():
            document.erase()

        self.is_removed = True
        self.removed_date = timezone.now()
        self.full_name = "GDPR REMOVED"
        self.given_name = "GDPR REMOVED"
        self.middle_name = "GDPR REMOVED"
        self.family_name = "GDPR REMOVED"
        self.photo = ""
        self.disability_certificate_picture = ""
        self.phone_no = ""
        self.phone_no_valid = False
        self.phone_no_alternative = ""
        self.phone_no_alternative_valid = False
        self.flex_fields = {}
        self.save()

    def validate_phone_numbers(self) -> None:
        calculate_phone_numbers_validity(self)

    def save(self, *args: Any, **kwargs: Any) -> None:
        recalculate_phone_numbers_validity(self, Individual)
        super().save(*args, **kwargs)


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
    is_original = models.BooleanField(db_index=True, default=False)

    objects = RepresentationManager()
    original_and_repr_objects = models.Manager()


class XlsxUpdateFile(TimeStampedUUIDModel):
    file = models.FileField()
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    rdi = models.ForeignKey("registration_data.RegistrationDataImport", on_delete=models.CASCADE, null=True)
    xlsx_match_columns = ArrayField(models.CharField(max_length=32), null=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.PROTECT)
    program = models.ForeignKey("program.Program", null=True, on_delete=models.CASCADE)


class BankAccountInfo(SoftDeletableRepresentationMergeStatusModelWithDate, TimeStampedUUIDModel, AbstractSyncable):
    individual = models.ForeignKey(
        "household.Individual",
        related_name="bank_account_info",
        on_delete=models.CASCADE,
    )
    bank_name = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=64)
    debit_card_number = models.CharField(max_length=255, blank=True, default="")
    bank_branch_name = models.CharField(max_length=255, blank=True, default="")
    account_holder_name = models.CharField(max_length=255, blank=True, default="")
    is_migration_handled = models.BooleanField(default=False)
    copied_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="copied_to",
        help_text="If this object was copied from another, this field will contain the object it was copied from.",
    )

    def __str__(self) -> str:
        return f"{self.bank_account_number} ({self.bank_name})"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.bank_account_number:
            self.bank_account_number = str(self.bank_account_number).replace(" ", "")
        if self.debit_card_number:
            self.debit_card_number = str(self.debit_card_number).replace(" ", "")
        super().save(*args, **kwargs)


class PendingHousehold(Household):
    objects = SoftDeletableRepresentationPendingManager()

    @property
    def individuals(self) -> QuerySet:
        return super().individuals(manager="pending_objects")

    @property
    def individuals_and_roles(self) -> QuerySet:
        return super().individuals_and_roles(manager="pending_objects")

    @property
    def pending_representatives(self) -> QuerySet:
        return super().representatives(manager="pending_objects")

    @cached_property
    def primary_collector(self) -> Optional["Individual"]:
        return self.pending_representatives.get(households_and_roles__role=ROLE_PRIMARY)

    @cached_property
    def alternate_collector(self) -> Optional["Individual"]:
        return self.pending_representatives.filter(households_and_roles__role=ROLE_ALTERNATE).first()

    class Meta:
        proxy = True
        verbose_name = "Imported Household"
        verbose_name_plural = "Imported Households"


class PendingIndividual(Individual):
    objects = SoftDeletableRepresentationPendingManager()

    @property
    def households_and_roles(self) -> QuerySet:
        return super().households_and_roles(manager="pending_objects")

    @property
    def documents(self) -> QuerySet:
        return super().documents(manager="pending_objects")

    @property
    def identities(self) -> QuerySet:
        return super().identities(manager="pending_objects")

    @property
    def bank_account_info(self) -> QuerySet:
        return super().bank_account_info(manager="pending_objects")

    @property
    def pending_household(self) -> QuerySet:
        return PendingHousehold.objects.get(pk=self.household.pk)

    class Meta:
        proxy = True
        verbose_name = "Imported Individual"
        verbose_name_plural = "Imported Individuals"


class PendingIndividualIdentity(IndividualIdentity):
    objects = SoftDeletableRepresentationPendingManager()

    class Meta:
        proxy = True
        verbose_name = "Imported Individual Identity"
        verbose_name_plural = "Imported Individual Identities"


class PendingDocument(Document):
    objects = SoftDeletableRepresentationPendingManager()

    class Meta:
        proxy = True
        verbose_name = "Imported Document"
        verbose_name_plural = "Imported Documents"


class PendingBankAccountInfo(BankAccountInfo):
    objects = SoftDeletableRepresentationPendingManager()

    class Meta:
        proxy = True
        verbose_name = "Imported Bank Account Info"
        verbose_name_plural = "Imported Bank Account Infos"


class PendingIndividualRoleInHousehold(IndividualRoleInHousehold):
    objects = SoftDeletableRepresentationPendingManager()

    class Meta:
        proxy = True
        verbose_name = "Imported Individual Role In Household"
        verbose_name_plural = "Imported Individual Roles In Household"
