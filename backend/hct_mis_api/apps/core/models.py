from typing import Any, Dict, List, Optional, Tuple

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models import JSONField, Q, UniqueConstraint
from django.utils.translation import gettext_lazy as _

from django_celery_beat.models import PeriodicTask
from django_celery_beat.schedulers import DatabaseScheduler, ModelEntry
from model_utils import Choices
from model_utils.models import SoftDeletableModel, TimeStampedModel
from natural_keys import NaturalKeyModel

import mptt
from hct_mis_api.apps.core.utils import unique_slugify
from hct_mis_api.apps.utils.models import (
    SoftDeletionTreeManager,
    SoftDeletionTreeModel,
    TimeStampedUUIDModel,
)
from mptt.fields import TreeForeignKey


class BusinessAreaPartnerThrough(TimeStampedUUIDModel):
    business_area = models.ForeignKey(
        "BusinessArea",
        on_delete=models.CASCADE,
        related_name="business_area_partner_through",
    )
    partner = models.ForeignKey(
        "account.Partner",
        on_delete=models.CASCADE,
        related_name="business_area_partner_through",
    )
    roles = models.ManyToManyField(
        "account.Role",
        related_name="business_area_partner_through",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["business_area", "partner"],
                name="unique_business_area_partner",
            )
        ]


class BusinessArea(NaturalKeyModel, TimeStampedUUIDModel):
    """
    BusinessArea (EPRP called Workspace, also synonym was
    country/region) model.
    It's used for drop down menu in top bar in the UI. Many times
    BusinessArea means country.
    region_name is a short code for distinct business arease
    <BusinessArea>
        <BUSINESS_AREA_CODE>0120</BUSINESS_AREA_CODE>
        <BUSINESS_AREA_NAME>Algeria</BUSINESS_AREA_NAME>
        <BUSINESS_AREA_LONG_NAME>THE PEOPLE'S DEMOCRATIC REPUBLIC OF ALGERIA</BUSINESS_AREA_LONG_NAME>
        <REGION_CODE>59</REGION_CODE>
        <REGION_NAME>MENAR</REGION_NAME>
    </BusinessArea>
    """

    code_to_cash_assist_mapping = {"575RE00000": "SLVK"}
    cash_assist_to_code_mapping = {v: k for k, v in code_to_cash_assist_mapping.items()}
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    long_name = models.CharField(max_length=255)
    region_code = models.CharField(max_length=8)
    region_name = models.CharField(max_length=8)
    kobo_username = models.CharField(max_length=255, null=True, blank=True)
    kobo_token = models.CharField(max_length=255, null=True, blank=True)
    kobo_url = models.URLField(max_length=255, null=True, blank=True)
    rapid_pro_host = models.URLField(null=True, blank=True)
    rapid_pro_payment_verification_token = models.CharField(max_length=40, null=True, blank=True)
    rapid_pro_messages_token = models.CharField(max_length=40, null=True, blank=True)
    rapid_pro_survey_token = models.CharField(max_length=40, null=True, blank=True)
    slug = models.CharField(
        max_length=250,
        unique=True,
        db_index=True,
    )
    custom_fields = JSONField(default=dict, blank=True)

    has_data_sharing_agreement = models.BooleanField(default=False)
    parent = models.ForeignKey(
        "self",
        related_name="children",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_split = models.BooleanField(default=False)

    postpone_deduplication = models.BooleanField(default=False)
    countries = models.ManyToManyField("geo.Country", related_name="business_areas")
    deduplication_duplicate_score = models.FloatField(
        default=6.0,
        validators=[MinValueValidator(0.0)],
        help_text="Results equal or above this score are considered duplicates",
    )
    deduplication_possible_duplicate_score = models.FloatField(
        default=6.0,
        validators=[MinValueValidator(0.0)],
        help_text="Results equal or above this score are considered possible duplicates (needs adjudication) must be lower than deduplication_duplicate_score",
    )

    deduplication_batch_duplicates_percentage = models.IntegerField(
        default=50,
        help_text="If percentage of duplicates is higher or equal to this setting, deduplication is aborted",
    )
    deduplication_batch_duplicates_allowed = models.IntegerField(
        default=5,
        help_text="If amount of duplicates for single individual exceeds this limit deduplication is aborted",
    )
    deduplication_golden_record_duplicates_percentage = models.IntegerField(
        default=50,
        help_text="If percentage of duplicates is higher or equal to this setting, deduplication is aborted",
    )
    deduplication_golden_record_duplicates_allowed = models.IntegerField(
        default=5,
        help_text="If amount of duplicates for single individual exceeds this limit deduplication is aborted",
    )
    screen_beneficiary = models.BooleanField(default=False, help_text="Enable screen beneficiary against sanction list")
    deduplication_ignore_withdraw = models.BooleanField(default=False)

    is_payment_plan_applicable = models.BooleanField(default=False)
    is_accountability_applicable = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    enable_email_notification = models.BooleanField(default=True, verbose_name="Automatic Email notifications enabled")

    partners = models.ManyToManyField(
        to="account.Partner", through=BusinessAreaPartnerThrough, related_name="business_areas"
    )

    def save(self, *args: Any, **kwargs: Any) -> None:
        unique_slugify(self, self.name, slug_field_name="slug")
        if self.parent:
            self.parent.is_split = True
            self.parent.save()
        if self.children.count():
            self.is_split = True
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]
        permissions = (
            ("can_split", "Can split BusinessArea"),
            ("can_send_doap", "Can send DOAP matrix"),
            ("can_reset_doap", "Can force sync DOAP matrix"),
            ("can_export_doap", "Can export DOAP matrix"),
        )

    def __str__(self) -> str:
        return self.name

    def natural_key(self) -> Tuple[str]:
        return (self.code,)

    @property
    def cash_assist_code(self) -> str:
        return self.code_to_cash_assist_mapping.get(self.code, self.code)

    @property
    def can_import_ocha_response_plans(self) -> bool:
        return any([c.details for c in self.countries.all()])

    @classmethod
    def get_business_areas_as_choices(cls) -> List[Dict[str, Any]]:
        return [
            {"label": {"English(EN)": business_area.name}, "value": business_area.slug}
            for business_area in cls.objects.all()
        ]

    def should_check_against_sanction_list(self) -> bool:
        return self.screen_beneficiary

    def get_sys_option(self, key: str, default: None = None) -> Any:
        if "hope" in self.custom_fields:
            return self.custom_fields["hope"].get(key, default)
        return default


class FlexibleAttribute(SoftDeletableModel, NaturalKeyModel, TimeStampedUUIDModel):
    STRING = "STRING"
    IMAGE = "IMAGE"
    INTEGER = "INTEGER"
    DECIMAL = "DECIMAL"
    SELECT_ONE = "SELECT_ONE"
    SELECT_MANY = "SELECT_MANY"
    DATE = "DATE"
    GEOPOINT = "GEOPOINT"
    PDU = "PDU"
    TYPE_CHOICE = Choices(
        (DATE, _("Date")),
        (DECIMAL, _("Decimal")),
        (IMAGE, _("Image")),
        (INTEGER, _("Integer")),
        (GEOPOINT, _("Geopoint")),
        (SELECT_ONE, _("Select One")),
        (SELECT_MANY, _("Select Many")),
        (STRING, _("String")),
        (PDU, _("PDU")),
    )

    ASSOCIATED_WITH_HOUSEHOLD = 0
    ASSOCIATED_WITH_INDIVIDUAL = 1
    ASSOCIATED_WITH_CHOICES: Any = (
        (0, _("Household")),
        (1, _("Individual")),
    )

    type = models.CharField(max_length=16, choices=TYPE_CHOICE)
    name = models.CharField(max_length=255)
    required = models.BooleanField(default=False)
    program = models.ForeignKey(
        "program.Program",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="pdu_fields",
    )
    pdu_data = models.OneToOneField(
        "core.PeriodicFieldData",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="flex_field",
    )
    label = JSONField(default=dict)
    hint = JSONField(default=dict)
    group = models.ForeignKey(
        "core.FlexibleAttributeGroup",
        on_delete=models.CASCADE,
        related_name="flex_attributes",
        null=True,
        blank=True,
    )
    associated_with = models.SmallIntegerField(choices=ASSOCIATED_WITH_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("name", "program"), name="unique_name_program"),
            models.UniqueConstraint(
                fields=("name",), condition=Q(program__isnull=True), name="unique_name_without_program"
            ),
        ]

    @property
    def is_flex_field(self) -> bool:
        return True

    def __str__(self) -> str:
        return f"type: {self.type}, name: {self.name}"


class FlexibleAttributeGroupManager(SoftDeletionTreeManager):
    def get_by_natural_key(self, name: str) -> "FlexibleAttributeGroup":
        return self.get(name=name)


class FlexibleAttributeGroup(SoftDeletionTreeModel):
    name = models.CharField(max_length=255, unique=True)
    label = JSONField(default=dict)
    required = models.BooleanField(default=False)
    repeatable = models.BooleanField(default=False)
    parent = TreeForeignKey(
        "self",
        verbose_name=_("Parent"),
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        on_delete=models.CASCADE,
    )
    objects = FlexibleAttributeGroupManager()

    def __str__(self) -> str:
        return f"name: {self.name}"

    def natural_key(self) -> Tuple[str]:
        return (self.name,)


class FlexibleAttributeChoice(SoftDeletableModel, NaturalKeyModel, TimeStampedUUIDModel):
    class Meta:
        unique_together = ["list_name", "name"]
        ordering = ("name",)

    list_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    label = JSONField(default=dict)
    flex_attributes = models.ManyToManyField("core.FlexibleAttribute", related_name="choices")

    def __str__(self) -> str:
        return f"list name: {self.list_name}, name: {self.name}"


mptt.register(FlexibleAttributeGroup, order_insertion_by=["name"])


class PeriodicFieldData(models.Model):
    """
    Additional data for PDU
    """

    STRING = "STRING"
    DECIMAL = "DECIMAL"
    DATE = "DATE"
    BOOLEAN = "BOOLEAN"

    TYPE_CHOICES = Choices(
        (DATE, _("Date")),
        (DECIMAL, _("Number")),
        (STRING, _("Text")),
        (BOOLEAN, _("Yes/No")),
    )

    subtype = models.CharField(max_length=16, choices=TYPE_CHOICES)
    number_of_rounds = models.IntegerField()
    rounds_names = ArrayField(models.CharField(max_length=255), default=list)

    class Meta:
        verbose_name = "Periodic Field Data"
        verbose_name_plural = "Periodic Fields Data"


class XLSXKoboTemplateManager(models.Manager):
    def latest_valid(self) -> Optional["XLSXKoboTemplate"]:
        return (
            self.get_queryset()
            .filter(status=self.model.SUCCESSFUL)
            .exclude(template_id__exact="")
            .order_by("-created_at")
            .first()
        )


class XLSXKoboTemplate(SoftDeletableModel, TimeStampedUUIDModel):
    SUCCESSFUL = "SUCCESSFUL"
    UPLOADED = "UPLOADED"
    UNSUCCESSFUL = "UNSUCCESSFUL"
    PROCESSING = "PROCESSING"
    CONNECTION_FAILED = "CONNECTION_FAILED"
    KOBO_FORM_UPLOAD_STATUS_CHOICES = (
        (CONNECTION_FAILED, _("Connection failed")),
        (PROCESSING, _("Processing")),
        (SUCCESSFUL, _("Successful")),
        (UNSUCCESSFUL, _("Unsuccessful")),
        (UPLOADED, _("Uploaded")),
    )

    class Meta:
        ordering = ("-created_at",)

    objects = XLSXKoboTemplateManager()

    file_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    file = models.FileField()
    error_description = models.TextField(blank=True)
    status = models.CharField(max_length=200, choices=KOBO_FORM_UPLOAD_STATUS_CHOICES)
    template_id = models.CharField(max_length=200, blank=True)
    first_connection_failed_time = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.file_name} - {self.created_at}"


class CountryCodeMapManager(models.Manager):
    def __init__(self) -> None:
        self._cache = {2: {}, 3: {}, "ca2": {}, "ca3": {}}
        super().__init__()

    def get_code(self, iso_code: str) -> Optional[str]:
        iso_code = iso_code.upper()
        self.build_cache()
        return self._cache[len(iso_code)].get(iso_code, iso_code)

    def get_iso3_code(self, ca_code: str) -> str:
        ca_code = ca_code.upper()
        self.build_cache()

        return self._cache["ca3"].get(ca_code, ca_code)

    def get_iso2_code(self, ca_code: str) -> str:
        ca_code = ca_code.upper()
        self.build_cache()

        return self._cache["ca2"].get(ca_code, ca_code)

    def build_cache(self) -> None:
        if not self._cache[2] or not self._cache[3] or not self._cache["ca2"] or not self._cache["ca3"]:
            for entry in self.all().select_related("country"):
                self._cache[2][entry.country.iso_code2] = entry.ca_code
                self._cache[3][entry.country.iso_code3] = entry.ca_code
                self._cache["ca2"][entry.ca_code] = entry.country.iso_code2
                self._cache["ca3"][entry.ca_code] = entry.country.iso_code3


class CountryCodeMap(models.Model):
    country = models.OneToOneField("geo.Country", blank=True, null=True, on_delete=models.PROTECT)
    ca_code = models.CharField(max_length=5, unique=True)

    objects = CountryCodeMapManager()

    class Meta:
        ordering = ("country",)


class CustomModelEntry(ModelEntry):
    """
    don't update existing tasks
    """

    @classmethod
    def from_entry(cls, name: str, app: Optional[str] = None, **entry: Any) -> "CustomModelEntry":
        obj, _ = PeriodicTask._default_manager.get_or_create(
            name=name,
            defaults=cls._unpack_fields(**entry),
        )
        return cls(obj, app=app)


class CustomDatabaseScheduler(DatabaseScheduler):
    Entry = CustomModelEntry


class StorageFile(models.Model):
    STATUS_NOT_PROCESSED = "Not processed"
    STATUS_PROCESSING = "Processing"
    STATUS_FINISHED = "Finished"
    STATUS_FAILED = "Failed"

    STATUS_CHOICE = Choices(
        (STATUS_NOT_PROCESSED, _("Not processed")),
        (STATUS_PROCESSING, _("Processing")),
        (STATUS_FINISHED, _("Finished")),
        (STATUS_FAILED, _("Failed")),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to="files")

    status = models.CharField(
        choices=STATUS_CHOICE,
        default=STATUS_NOT_PROCESSED,
        max_length=25,
    )

    @property
    def file_name(self) -> str:
        return self.file.name

    @property
    def file_url(self) -> str:
        return self.file.url

    @property
    def file_size(self) -> int:
        return self.file.size

    def __str__(self) -> str:
        return self.file.name


class FileTemp(TimeStampedModel):
    """Use this model for temporary store files"""

    object_id = models.CharField(max_length=120, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    file = models.FileField()
    was_downloaded = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.file.name} - {self.created}"


class MigrationStatus(TimeStampedModel):
    is_running = models.BooleanField()

    class Meta:
        verbose_name_plural = "Migration Status"


class DataCollectingType(TimeStampedModel):
    class Type(models.TextChoices):
        STANDARD = "STANDARD", "Standard"
        SOCIAL = "SOCIAL", "Social Workers"

    label = models.CharField(max_length=32, blank=True)
    code = models.CharField(max_length=32)
    type = models.CharField(choices=Type.choices, null=True, blank=True, max_length=32)
    description = models.TextField(blank=True)
    compatible_types = models.ManyToManyField("self", blank=True, symmetrical=False)
    limit_to = models.ManyToManyField(to="BusinessArea", related_name="data_collecting_types", blank=True)
    active = models.BooleanField(default=True)
    deprecated = models.BooleanField(
        default=False, help_text="Cannot be used in new programs, totally hidden in UI, only admin have access"
    )
    individual_filters_available = models.BooleanField(default=False)
    household_filters_available = models.BooleanField(default=True)
    recalculate_composition = models.BooleanField(default=False)
    weight = models.PositiveSmallIntegerField(default=0)

    def __str__(self) -> str:
        return self.label

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["label", "code"],
                name="unique_label_code_data_collecting_type",
            )
        ]
        ordering = ("-weight",)

    def clean(self) -> None:
        super().clean()
        if (
            self.pk
            and self.type
            and self.compatible_types.exists()
            and not getattr(self, "skip_type_validation", False)
        ):
            incompatible_dcts = self.compatible_types.exclude(Q(type=self.type) | Q(pk=self.pk))
            if incompatible_dcts.exists():
                raise ValidationError("Type of DCT cannot be changed if it has compatible DCTs of different type.")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
