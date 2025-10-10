from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import JSONField, UniqueConstraint
from natural_keys import NaturalKeyModel

from hope.apps.core.utils import unique_slugify
from hope.models.utils import (
    TimeStampedUUIDModel,
)


class BusinessAreaPartnerThrough(TimeStampedUUIDModel):  # TODO: remove after migration to RoleAssignment
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
        app_label = "core"
        constraints = [
            UniqueConstraint(
                fields=["business_area", "partner"],
                name="unique_business_area_partner",
            )
        ]


class BusinessArea(NaturalKeyModel, TimeStampedUUIDModel):
    """BusinessArea (EPRP called Workspace, also synonym was country/region) model.

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

    code = models.CharField(max_length=10, unique=True)
    slug = models.CharField(
        max_length=250,
        unique=True,
        db_index=True,
    )
    name = models.CharField(max_length=255)
    long_name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self",
        related_name="children",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    partners = models.ManyToManyField(
        to="account.Partner",
        through=BusinessAreaPartnerThrough,
        related_name="business_areas",
    )
    countries = models.ManyToManyField("geo.Country", related_name="business_areas")
    office_country = models.ForeignKey(
        "geo.Country",
        related_name="business_area",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    payment_countries = models.ManyToManyField("geo.Country", related_name="payment_business_areas")

    is_split = models.BooleanField(default=False)
    region_code = models.CharField(max_length=8)
    region_name = models.CharField(max_length=8)
    has_data_sharing_agreement = models.BooleanField(default=False)
    is_accountability_applicable = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    enable_email_notification = models.BooleanField(default=True, verbose_name="Automatic Email notifications enabled")
    # TODO: deprecated to remove in the next release
    kobo_username = models.CharField(max_length=255, null=True, blank=True)
    kobo_token = models.CharField(max_length=255, null=True, blank=True)
    kobo_url = models.URLField(max_length=255, null=True, blank=True)

    rapid_pro_host = models.URLField(null=True, blank=True)
    rapid_pro_payment_verification_token = models.CharField(max_length=40, null=True, blank=True)
    rapid_pro_messages_token = models.CharField(max_length=40, null=True, blank=True)
    rapid_pro_survey_token = models.CharField(max_length=40, null=True, blank=True)

    postpone_deduplication = models.BooleanField(default=False)
    deduplication_duplicate_score = models.FloatField(
        default=6.0,
        validators=[MinValueValidator(0.0)],
        help_text="Results equal or above this score are considered duplicates",
    )
    deduplication_possible_duplicate_score = models.FloatField(
        default=6.0,
        validators=[MinValueValidator(0.0)],
        help_text="Results equal or above this score are considered possible duplicates (needs adjudication) "
        "must be lower than deduplication_duplicate_score",
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
    deduplication_ignore_withdraw = models.BooleanField(default=False)
    biometric_deduplication_threshold = models.FloatField(
        default=0.0,
        help_text="Threshold for Face Image Deduplication",
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )

    custom_fields = JSONField(default=dict, blank=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        unique_slugify(self, self.name, slug_field_name="slug")
        if self.parent:
            self.parent.is_split = True
            self.parent.save()
        if self.children.count():
            self.is_split = True
        super().save(*args, **kwargs)

    class Meta:
        app_label = "core"
        ordering = ["name"]
        permissions = (
            ("can_split", "Can split BusinessArea"),
            ("ping_rapidpro", "Can test RapidPRO connection"),
            ("execute_sync_rapid_pro", "Can execute RapidPRO sync"),
        )

    def __str__(self) -> str:
        return self.name

    def natural_key(self) -> tuple[str]:
        return (self.code,)

    @property
    def can_import_ocha_response_plans(self) -> bool:
        return any(c.details for c in self.countries.all())

    @classmethod
    def get_business_areas_as_choices(cls) -> list[dict[str, Any]]:
        return [
            {"label": {"English(EN)": business_area.name}, "value": business_area.slug}
            for business_area in cls.objects.all()
        ]

    def get_sys_option(self, key: str, default: None = None) -> Any:
        if "hope" in self.custom_fields:
            return self.custom_fields["hope"].get(key, default)
        return default
