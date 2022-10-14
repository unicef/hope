from functools import lru_cache

from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

from constance import config
from django_celery_beat.models import PeriodicTask
from django_celery_beat.schedulers import DatabaseScheduler, ModelEntry
from model_utils import Choices
from model_utils.models import SoftDeletableModel

import mptt
from hct_mis_api.apps.core.utils import unique_slugify
from hct_mis_api.apps.grievance.constants import PRIORITY_CHOICES, URGENCY_CHOICES
from hct_mis_api.apps.utils.models import SoftDeletionTreeModel, TimeStampedUUIDModel
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class BusinessArea(TimeStampedUUIDModel):
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
    rapid_pro_host = models.URLField(null=True, blank=True)
    rapid_pro_api_key = models.CharField(max_length=40, null=True, blank=True)
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
    screen_beneficiary = models.BooleanField(default=False)
    deduplication_ignore_withdraw = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
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

    def __str__(self):
        return self.name

    @property
    def cash_assist_code(self):
        return self.code_to_cash_assist_mapping.get(self.code, self.code)

    @cash_assist_code.setter
    def cash_assist_code(self, value):
        self.code = self.cash_assist_to_code_mapping.get(value, value)

    @property
    def can_import_ocha_response_plans(self):
        return any([c.details for c in self.countries.all()])

    @classmethod
    def get_business_areas_as_choices(cls):
        return [
            {"label": {"English(EN)": business_area.name}, "value": business_area.slug}
            for business_area in cls.objects.all()
        ]

    def should_check_against_sanction_list(self):
        return self.screen_beneficiary

    def get_sys_option(self, key, default=None):
        if "hope" in self.custom_fields:
            return self.custom_fields["hope"].get(key, default)
        return default


class FlexibleAttribute(SoftDeletableModel, TimeStampedUUIDModel):
    ASSOCIATED_WITH_HOUSEHOLD = 0
    ASSOCIATED_WITH_INDIVIDUAL = 1
    STRING = "STRING"
    IMAGE = "IMAGE"
    INTEGER = "INTEGER"
    DECIMAL = "DECIMAL"
    SELECT_ONE = "SELECT_ONE"
    SELECT_MANY = "SELECT_MANY"
    DATE = "DATE"
    GEOPOINT = "GEOPOINT"
    TYPE_CHOICE = Choices(
        (DATE, _("Date")),
        (DECIMAL, _("Decimal")),
        (IMAGE, _("Image")),
        (INTEGER, _("Integer")),
        (GEOPOINT, _("Geopoint")),
        (SELECT_ONE, _("Select One")),
        (SELECT_MANY, _("Select Many")),
        (STRING, _("String")),
    )
    ASSOCIATED_WITH_CHOICES = (
        (0, _("Household")),
        (1, _("Individual")),
    )

    type = models.CharField(max_length=16, choices=TYPE_CHOICE)
    name = models.CharField(max_length=255, unique=True)
    required = models.BooleanField(default=False)
    label = JSONField(default=dict)
    hint = JSONField(default=dict)
    group = models.ForeignKey(
        "core.FlexibleAttributeGroup",
        on_delete=models.CASCADE,
        related_name="flex_attributes",
        null=True,
    )
    associated_with = models.SmallIntegerField(choices=ASSOCIATED_WITH_CHOICES)

    @property
    def is_flex_field(self):
        return True

    def __str__(self):
        return f"type: {self.type}, name: {self.name}"


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

    def __str__(self):
        return f"name: {self.name}"


class FlexibleAttributeChoice(SoftDeletableModel, TimeStampedUUIDModel):
    class Meta:
        unique_together = ["list_name", "name"]
        ordering = ("name",)

    list_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    label = JSONField(default=dict)
    flex_attributes = models.ManyToManyField("core.FlexibleAttribute", related_name="choices")

    def __str__(self):
        return f"list name: {self.list_name}, name: {self.name}"


mptt.register(FlexibleAttributeGroup, order_insertion_by=["name"])


class XLSXKoboTemplateManager(models.Manager):
    def latest_valid(self):
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

    def __str__(self):
        return f"{self.file_name} - {self.created_at}"


class CountryCodeMapManager(models.Manager):
    def __init__(self):
        self._cache = {2: {}, 3: {}, "ca2": {}, "ca3": {}}
        super().__init__()

    def get_code(self, iso_code):
        iso_code = iso_code.upper()
        self.build_cache()
        return self._cache[len(iso_code)].get(iso_code, iso_code)

    def get_iso3_code(self, ca_code):
        ca_code = ca_code.upper()
        self.build_cache()

        return self._cache["ca3"].get(ca_code, ca_code)

    def get_iso2_code(self, ca_code):
        ca_code = ca_code.upper()
        self.build_cache()

        return self._cache["ca2"].get(ca_code, ca_code)

    def build_cache(self):
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
    def from_entry(cls, name, app=None, **entry):
        obj, _ = PeriodicTask._default_manager.get_or_create(
            name=name,
            defaults=cls._unpack_fields(**entry),
        )
        return cls(obj, app=app)


class CustomDatabaseScheduler(DatabaseScheduler):
    Entry = CustomModelEntry


class StorageFile(models.Model):
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

    @property
    def file_name(self):
        return self.file.name

    @property
    def file_url(self):
        return self.file.url

    @property
    def file_size(self):
        return self.file.size

    def __str__(self):
        return self.file.name


class TicketPriority(models.Model):
    NEEDS_ADJUDICATION = 1
    PAYMENT_VERIFICATION = 2
    SYSTEM_FLAGGING = 3
    TICKET_TYPE_CHOICES = (
        (NEEDS_ADJUDICATION, _("Needs Adjudication")),
        (PAYMENT_VERIFICATION, _("Payment Verification")),
        (SYSTEM_FLAGGING, _("System Flagging")),
    )

    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE, related_name="tickets_priority")
    priority = models.IntegerField(verbose_name=_("Priority"), choices=PRIORITY_CHOICES, default="")
    urgency = models.IntegerField(verbose_name=_("Urgency"), choices=URGENCY_CHOICES, default="")
    ticket_type = models.IntegerField(verbose_name=_("Ticket type"), choices=TICKET_TYPE_CHOICES, default="")

    class Meta:
        unique_together = (
            "business_area",
            "ticket_type",
        )

    @classmethod
    @lru_cache()
    def priority_by_business_area_and_ticket_type(cls, business_area_id, ticket_type):
        try:
            return cls.objects.get(business_area__pk=business_area_id, ticket_type=ticket_type).priority
        except ObjectDoesNotExist:
            return cls._get_default_priority_by_ticket_type(ticket_type)

    @classmethod
    @lru_cache()
    def urgency_by_business_area_and_ticket_type(cls, business_area_id, ticket_type):
        try:
            return cls.objects.get(business_area__pk=business_area_id, ticket_type=ticket_type).urgency
        except ObjectDoesNotExist:
            return cls._get_default_urgency_by_ticket_type(ticket_type)

    @classmethod
    def _get_default_priority_by_ticket_type(cls, ticket_type):
        return {
            cls.NEEDS_ADJUDICATION: config.NEEDS_ADJUDICATION_PRIORITY,
            cls.PAYMENT_VERIFICATION: config.PAYMENT_VERIFICATION_PRIORITY,
            cls.SYSTEM_FLAGGING: config.SYSTEM_FLAGGING_PRIORITY,
        }[ticket_type]

    @classmethod
    def _get_default_urgency_by_ticket_type(cls, ticket_type):
        return {
            cls.NEEDS_ADJUDICATION: config.NEEDS_ADJUDICATION_URGENCY,
            cls.PAYMENT_VERIFICATION: config.PAYMENT_VERIFICATION_URGENCY,
            cls.SYSTEM_FLAGGING: config.SYSTEM_FLAGGING_URGENCY,
        }[ticket_type]
