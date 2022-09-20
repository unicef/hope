from django.conf import settings
from django.contrib.postgres.fields import CICharField
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    ProhibitNullCharactersValidator,
)
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_datahub.models import ImportedIndividual
from hct_mis_api.apps.utils.models import ConcurrencyModel, TimeStampedUUIDModel
from hct_mis_api.apps.utils.validators import (
    DoubleSpaceValidator,
    StartEndSpaceValidator,
)


class RegistrationDataImport(TimeStampedUUIDModel, ConcurrencyModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "name",
            "status",
            "import_date",
            "imported_by",
            "data_source",
            "number_of_individuals",
            "number_of_households",
            "datahub_id",
            "error_message",
        ]
    )
    IMPORTING = "IMPORTING"
    IN_REVIEW = "IN_REVIEW"
    MERGING = "MERGING"
    MERGED = "MERGED"
    DEDUPLICATION_FAILED = "DEDUPLICATION_FAILED"
    DEDUPLICATION = "DEDUPLICATION"
    REFUSED_IMPORT = "REFUSED"
    IMPORT_ERROR = "IMPORT_ERROR"
    MERGE_ERROR = "MERGE_ERROR"
    STATUS_CHOICE = (
        (DEDUPLICATION, _("Deduplication")),
        (DEDUPLICATION_FAILED, _("Deduplication Failed")),
        (IMPORTING, _("Importing")),
        (IMPORT_ERROR, _("Import Error")),
        (IN_REVIEW, _("In Review")),
        (MERGED, _("Merged")),
        (MERGING, _("Merging")),
        (MERGE_ERROR, _("Merge Error")),
        (REFUSED_IMPORT, _("Refused import")),
    )
    XLS = "XLS"
    KOBO = "KOBO"
    DIIA = "DIIA"
    API = "API"
    FLEX_REGISTRATION = "FLEX_REGISTRATION"
    DATA_SOURCE_CHOICE = (
        (XLS, "Excel"),
        (KOBO, "KoBo"),
        (DIIA, "DIIA"),
        (FLEX_REGISTRATION, "Flex Registration"),
        (API, "Flex API"),
    )
    name = CICharField(
        max_length=255,
        unique=True,
        db_index=True,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(255),
            DoubleSpaceValidator,
            StartEndSpaceValidator,
            ProhibitNullCharactersValidator(),
        ],
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICE, default=IN_REVIEW, db_index=True)
    import_date = models.DateTimeField(auto_now_add=True, db_index=True)
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="registration_data_imports",
        on_delete=models.CASCADE,
        null=True,
    )
    data_source = models.CharField(
        max_length=255,
        choices=DATA_SOURCE_CHOICE,
    )
    number_of_individuals = models.PositiveIntegerField(db_index=True)
    number_of_households = models.PositiveIntegerField(db_index=True)
    datahub_id = models.UUIDField(null=True, default=None, db_index=True, blank=True)
    error_message = models.TextField(blank=True)
    sentry_id = models.CharField(max_length=100, default="", blank=True, null=True)

    pull_pictures = models.BooleanField(default=True)
    business_area = models.ForeignKey(BusinessArea, null=True, on_delete=models.CASCADE)
    screen_beneficiary = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @cached_property
    def all_imported_individuals(self):
        return ImportedIndividual.objects.filter(registration_data_import=self.datahub_id)

    class Meta:
        unique_together = ("name", "business_area")
        verbose_name = "Registration data import"

    def should_check_against_sanction_list(self):
        return self.screen_beneficiary

    @classmethod
    def get_choices(cls, business_area_slug=None):
        filters = {}
        if business_area_slug:
            filters["business_area__slug"] = business_area_slug
        queryset = cls.objects.filter(**filters)
        return [
            {
                "label": {"English(EN)": f"{rdi.name}"},
                "value": rdi.id,
            }
            for rdi in queryset
        ]

    def can_be_merged(self):
        return self.status in [self.IN_REVIEW, self.MERGE_ERROR]
