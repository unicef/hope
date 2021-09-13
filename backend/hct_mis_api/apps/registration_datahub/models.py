import logging
import re
from datetime import date

from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import JSONField
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    validate_image_file_extension,
)
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_countries.fields import CountryField
from multiselectfield import MultiSelectField
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField

from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES
from hct_mis_api.apps.household.models import (
    BLANK,
    DATA_SHARING_CHOICES,
    DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
    DISABILITY_CHOICES,
    IDENTIFICATION_TYPE_CHOICE,
    MARITAL_STATUS_CHOICE,
    NOT_DISABLED,
    NOT_PROVIDED,
    OBSERVED_DISABILITY_CHOICE,
    ORG_ENUMERATOR_CHOICES,
    REGISTRATION_METHOD_CHOICES,
    RELATIONSHIP_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    ROLE_CHOICE,
    SEVERITY_OF_DISABILITY_CHOICES,
    SEX_CHOICE,
    UNIQUE,
    WORK_STATUS_CHOICE,
    YES_NO_CHOICE,
)
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel

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

logger = logging.getLogger(__name__)


class ImportedHousehold(TimeStampedUUIDModel):
    consent_sign = ImageField(validators=[validate_image_file_extension], blank=True)
    consent = models.NullBooleanField()
    consent_sharing = MultiSelectField(choices=DATA_SHARING_CHOICES, default=BLANK)
    residence_status = models.CharField(max_length=255, choices=RESIDENCE_STATUS_CHOICE)
    country_origin = CountryField()
    size = models.PositiveIntegerField()
    address = models.CharField(max_length=255, blank=True, default=BLANK)
    country = CountryField()
    admin1 = models.CharField(max_length=255, blank=True, default=BLANK)
    admin1_title = models.CharField(max_length=255, blank=True, default=BLANK)
    admin2 = models.CharField(max_length=255, blank=True, default=BLANK)
    admin2_title = models.CharField(max_length=255, blank=True, default=BLANK)
    geopoint = PointField(null=True, default=None)
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
    head_of_household = models.OneToOneField("ImportedIndividual", on_delete=models.CASCADE, null=True)
    fchild_hoh = models.NullBooleanField()
    child_hoh = models.NullBooleanField()
    registration_data_import = models.ForeignKey(
        "RegistrationDataImportDatahub",
        related_name="households",
        on_delete=models.CASCADE,
    )
    first_registration_date = models.DateTimeField()
    last_registration_date = models.DateTimeField()
    returnee = models.NullBooleanField()
    flex_fields = JSONField(default=dict)
    start = models.DateTimeField(blank=True, null=True)
    deviceid = models.CharField(max_length=250, blank=True)
    name_enumerator = models.CharField(max_length=250, blank=True, default=BLANK)
    org_enumerator = models.CharField(max_length=250, choices=ORG_ENUMERATOR_CHOICES, blank=True, default=BLANK)
    org_name_enumerator = models.CharField(max_length=250, blank=True, default=BLANK)
    village = models.CharField(max_length=250, blank=True, default=BLANK)
    registration_method = models.CharField(max_length=250, choices=REGISTRATION_METHOD_CHOICES, default=BLANK)
    collect_individual_data = models.CharField(max_length=250, choices=YES_NO_CHOICE, default=BLANK)
    currency = models.CharField(max_length=250, choices=CURRENCY_CHOICES, default=BLANK)
    unhcr_id = models.CharField(max_length=250, blank=True, default=BLANK)
    kobo_submission_uuid = models.UUIDField(null=True, default=None)
    kobo_asset_id = models.CharField(max_length=150, blank=True, default=BLANK)
    kobo_submission_time = models.DateTimeField(max_length=150, blank=True, null=True)

    @property
    def business_area(self):
        return self.registration_data_import.business_area

    def __str__(self):
        return f"Household ID: {self.id}"


class ImportedIndividual(TimeStampedUUIDModel):
    individual_id = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    full_name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    given_name = models.CharField(max_length=85, blank=True, default=BLANK)
    middle_name = models.CharField(max_length=85, blank=True, default=BLANK)
    family_name = models.CharField(max_length=85, blank=True, default=BLANK)
    relationship = models.CharField(
        max_length=255,
        blank=True,
        choices=RELATIONSHIP_CHOICE,
        default=BLANK,
    )
    sex = models.CharField(
        max_length=255,
        choices=SEX_CHOICE,
    )
    birth_date = models.DateField()
    estimated_birth_date = models.BooleanField(default=False)
    marital_status = models.CharField(
        max_length=255,
        choices=MARITAL_STATUS_CHOICE,
    )
    phone_no = PhoneNumberField(blank=True, default=BLANK)
    phone_no_alternative = PhoneNumberField(blank=True, default=BLANK)
    household = models.ForeignKey(
        "ImportedHousehold",
        null=True,
        related_name="individuals",
        on_delete=models.CASCADE,
    )
    registration_data_import = models.ForeignKey(
        "RegistrationDataImportDatahub",
        related_name="individuals",
        on_delete=models.CASCADE,
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
    deduplication_batch_status = models.CharField(
        max_length=50,
        default=UNIQUE_IN_BATCH,
        choices=DEDUPLICATION_BATCH_STATUS_CHOICE,
        blank=True,
    )
    deduplication_golden_record_status = models.CharField(
        max_length=50,
        default=UNIQUE,
        choices=DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
        blank=True,
    )
    deduplication_batch_results = JSONField(default=dict)
    deduplication_golden_record_results = JSONField(default=dict)
    flex_fields = JSONField(default=dict)
    pregnant = models.NullBooleanField()
    observed_disability = MultiSelectField(choices=OBSERVED_DISABILITY_CHOICE)
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
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    @property
    def get_hash_key(self):
        from hashlib import sha256

        fields = (
            "given_name",
            "middle_name",
            "family_name",
            "full_name",
            "sex",
            "birth_date",
            "estimated_birth_date",
            "phone_no",
            "phone_no_alternative",
        )
        values = [str(getattr(self, field)).lower() for field in fields]

        return sha256(";".join(values).encode()).hexdigest()

    def __str__(self):
        return self.full_name

    @property
    def business_area(self):
        return self.registration_data_import.business_area


class ImportedIndividualRoleInHousehold(TimeStampedUUIDModel):
    individual = models.ForeignKey(
        "ImportedIndividual",
        on_delete=models.CASCADE,
        related_name="households_and_roles",
    )
    household = models.ForeignKey(
        "ImportedHousehold",
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


class RegistrationDataImportDatahub(TimeStampedUUIDModel):
    NOT_STARTED = "NOT_STARTED"
    STARTED = "STARTED"
    DONE = "DONE"
    IMPORT_DONE_CHOICES = (
        (NOT_STARTED, _("Not Started")),
        (STARTED, _("Started")),
        (DONE, _("Done")),
    )

    name = models.CharField(max_length=255, blank=True)
    import_date = models.DateTimeField(auto_now_add=True)
    hct_id = models.UUIDField(null=True, db_index=True)
    import_data = models.OneToOneField(
        "ImportData",
        related_name="registration_data_import",
        on_delete=models.CASCADE,
        null=True,
    )
    import_done = models.CharField(max_length=15, choices=IMPORT_DONE_CHOICES, default=NOT_STARTED)
    business_area_slug = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    @property
    def business_area(self):
        return self.business_area_slug


class ImportData(TimeStampedUUIDModel):
    XLSX = "XLSX"
    JSON = "JSON"
    DATA_TYPE_CHOICES = (
        (XLSX, _("XLSX File")),
        (JSON, _("JSON File")),
    )

    file = models.FileField()
    data_type = models.CharField(max_length=4, choices=DATA_TYPE_CHOICES, default=XLSX)
    number_of_households = models.PositiveIntegerField()
    number_of_individuals = models.PositiveIntegerField()


class DocumentValidator(TimeStampedUUIDModel):
    type = models.ForeignKey(
        "ImportedDocumentType",
        related_name="validators",
        on_delete=models.CASCADE,
    )
    regex = models.CharField(max_length=100, default=".*")


class ImportedDocumentType(TimeStampedUUIDModel):
    country = CountryField(default="U")
    label = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=IDENTIFICATION_TYPE_CHOICE)

    class Meta:
        unique_together = ("country", "type")

    def __str__(self):
        return f"{self.label} in {self.country}"


class ImportedDocument(TimeStampedUUIDModel):
    document_number = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    individual = models.ForeignKey("ImportedIndividual", related_name="documents", on_delete=models.CASCADE)
    type = models.ForeignKey(
        "ImportedDocumentType",
        related_name="documents",
        on_delete=models.CASCADE,
    )

    def clean(self):
        from django.core.exceptions import ValidationError

        for validator in self.type.validators.all():
            if not re.match(validator.regex, self.document_number):
                logger.error("Document number is not validating")
                raise ValidationError("Document number is not validating")


class ImportedAgency(models.Model):
    type = models.CharField(
        max_length=100,
    )
    label = models.CharField(
        max_length=100,
    )
    country = CountryField()

    class Meta:
        unique_together = ("country", "type")

    def __str__(self):
        return f"{self.label}"


class ImportedIndividualIdentity(models.Model):
    agency = models.ForeignKey("ImportedAgency", related_name="identities", on_delete=models.CASCADE)
    individual = models.ForeignKey(
        "ImportedIndividual",
        related_name="identities",
        on_delete=models.CASCADE,
    )
    document_number = models.CharField(
        max_length=255,
    )

    def __str__(self):
        return f"{self.agency} {self.individual} {self.document_number}"


class KoboImportedSubmission(models.Model):
    kobo_submission_uuid = models.UUIDField()
    kobo_asset_id = models.CharField(max_length=150)
    kobo_submission_time = models.DateTimeField()
    registration_data_import = models.ForeignKey(
        RegistrationDataImportDatahub,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
