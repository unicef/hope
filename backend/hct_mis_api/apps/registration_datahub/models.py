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
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField

from household.models import (
    RESIDENCE_STATUS_CHOICE,
    SEX_CHOICE,
    MARITAL_STATUS_CHOICE,
    RELATIONSHIP_CHOICE,
    ROLE_CHOICE,
    IDENTIFICATION_TYPE_CHOICE,
    WORK_STATUS_CHOICE,
    NOT_PROVIDED,
    UNIQUE,
    DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
)
from utils.models import TimeStampedUUIDModel

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


class ImportedHouseholdIdentity(models.Model):
    agency = models.ForeignKey("ImportedAgency", related_name="households_identities", on_delete=models.CASCADE,)
    household = models.ForeignKey("ImportedHousehold", related_name="identities", on_delete=models.CASCADE)
    document_number = models.CharField(max_length=255,)

    def __str__(self):
        return f"{self.agency} {self.individual} {self.document_number}"


class ImportedHousehold(TimeStampedUUIDModel):
    consent = ImageField(validators=[validate_image_file_extension])
    residence_status = models.CharField(max_length=255, choices=RESIDENCE_STATUS_CHOICE,)
    country_origin = CountryField()
    size = models.PositiveIntegerField()
    address = models.CharField(max_length=255, blank=True, default="")
    country = CountryField(blank=True, default="")
    admin1 = models.CharField(max_length=255, blank=True, default="")
    admin2 = models.CharField(max_length=255, blank=True, default="")
    geopoint = PointField(null=True, default=None)
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
    head_of_household = models.OneToOneField("ImportedIndividual", on_delete=models.CASCADE, null=True)
    registration_data_import = models.ForeignKey(
        "RegistrationDataImportDatahub", related_name="households", on_delete=models.CASCADE,
    )
    first_registration_date = models.DateField()
    last_registration_date = models.DateField()
    returnee = models.BooleanField(default=False)
    flex_fields = JSONField(default=dict)

    def __str__(self):
        return f"Household ID: {self.id}"


class ImportedIndividual(TimeStampedUUIDModel):
    individual_id = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    full_name = models.CharField(max_length=255, validators=[MinLengthValidator(3), MaxLengthValidator(255)],)
    given_name = models.CharField(max_length=85, blank=True, default="")
    middle_name = models.CharField(max_length=85, blank=True, default="")
    family_name = models.CharField(max_length=85, blank=True, default="")
    relationship = models.CharField(max_length=255, blank=True, choices=RELATIONSHIP_CHOICE, default="",)
    sex = models.CharField(max_length=255, choices=SEX_CHOICE,)
    birth_date = models.DateField()
    estimated_birth_date = models.BooleanField(default=False)
    marital_status = models.CharField(max_length=255, choices=MARITAL_STATUS_CHOICE,)
    phone_no = PhoneNumberField(blank=True, default="")
    phone_no_alternative = PhoneNumberField(blank=True, default="")
    household = models.ForeignKey("ImportedHousehold", null=True, related_name="individuals", on_delete=models.CASCADE,)
    registration_data_import = models.ForeignKey(
        "RegistrationDataImportDatahub", related_name="individuals", on_delete=models.CASCADE,
    )
    disability = models.BooleanField(default=False)
    work_status = models.CharField(max_length=20, choices=WORK_STATUS_CHOICE, blank=True, default=NOT_PROVIDED,)
    first_registration_date = models.DateField()
    last_registration_date = models.DateField()
    deduplication_batch_status = models.CharField(
        max_length=50, default=UNIQUE_IN_BATCH, choices=DEDUPLICATION_BATCH_STATUS_CHOICE, blank=True,
    )
    deduplication_golden_record_status = models.CharField(
        max_length=50, default=UNIQUE, choices=DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE, blank=True,
    )
    deduplication_batch_results = JSONField(default=dict)
    deduplication_golden_record_results = JSONField(default=dict)
    flex_fields = JSONField(default=dict)
    pregnant = models.BooleanField(default=False)

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
            "sex",
            "birth_date",
            "phone_no",
            "phone_no_alternative",
        )
        values = [str(getattr(self, field)) for field in fields]

        return sha256(";".join(values).encode()).hexdigest()

    def __str__(self):
        return self.full_name


class ImportedIndividualRoleInHousehold(TimeStampedUUIDModel):
    individual = models.ForeignKey("ImportedIndividual", on_delete=models.CASCADE, related_name="households_and_roles",)
    household = models.ForeignKey("ImportedHousehold", on_delete=models.CASCADE, related_name="individuals_and_roles",)
    role = models.CharField(max_length=255, blank=True, choices=ROLE_CHOICE,)

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
    hct_id = models.UUIDField(null=True)
    import_data = models.OneToOneField(
        "ImportData", related_name="registration_data_import", on_delete=models.CASCADE, null=True,
    )
    import_done = models.CharField(max_length=15, choices=IMPORT_DONE_CHOICES, default=NOT_STARTED)
    business_area_slug = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return self.name


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
    type = models.ForeignKey("ImportedDocumentType", related_name="validators", on_delete=models.CASCADE,)
    regex = models.CharField(max_length=100, default=".*")


class ImportedDocumentType(TimeStampedUUIDModel):
    country = CountryField(blank=True)
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
    type = models.ForeignKey("ImportedDocumentType", related_name="documents", on_delete=models.CASCADE,)

    def clean(self):
        from django.core.exceptions import ValidationError

        for validator in self.type.validators:
            if not re.match(validator.regex, self.document_number):
                raise ValidationError("Document number is not validating")


class ImportedAgency(models.Model):
    type = models.CharField(max_length=100,)
    label = models.CharField(max_length=100,)

    def __str__(self):
        return f"{self.label}"


class ImportedIndividualIdentity(models.Model):
    agency = models.ForeignKey("ImportedAgency", related_name="identities", on_delete=models.CASCADE)
    individual = models.ForeignKey("ImportedIndividual", related_name="identities", on_delete=models.CASCADE,)
    document_number = models.CharField(max_length=255,)

    def __str__(self):
        return f"{self.agency} {self.individual} {self.document_number}"
