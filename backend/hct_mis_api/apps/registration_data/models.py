from django.conf import settings
from django.contrib.postgres.fields import CICharField
from django.core.validators import MinLengthValidator, MaxLengthValidator, ProhibitNullCharactersValidator
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.registration_datahub.models import ImportedIndividual
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel, ConcurrencyModel
from hct_mis_api.apps.utils.validators import DoubleSpaceValidator, StartEndSpaceValidator


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
    IMPORT_ERROR = "IMPORT_ERROR"
    MERGE_ERROR = "MERGE_ERROR"
    STATUS_CHOICE = (
        (IN_REVIEW, _("In Review")),
        (MERGED, _("Merged")),
        (MERGING, _("Merging")),
        (IMPORTING, _("Importing")),
        (DEDUPLICATION_FAILED, _("Deduplication Failed")),
        (DEDUPLICATION, _("Deduplication")),
        (IMPORT_ERROR, _("Import Error")),
        (MERGE_ERROR, _("Merge Error")),
    )
    DATA_SOURCE_CHOICE = (
        ("XLS", "Excel"),
        ("KOBO", "KoBo"),
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
    )
    data_source = models.CharField(
        max_length=255,
        choices=DATA_SOURCE_CHOICE,
    )
    number_of_individuals = models.PositiveIntegerField(db_index=True)
    number_of_households = models.PositiveIntegerField(db_index=True)
    datahub_id = models.UUIDField(null=True, default=None, db_index=True, blank=True)
    error_message = models.TextField(blank=True)

    business_area = models.ForeignKey("core.BusinessArea", null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @cached_property
    def all_imported_individuals(self):
        return ImportedIndividual.objects.filter(registration_data_import=self.datahub_id)

    class Meta:
        unique_together = ("name", "business_area")
        verbose_name = "Registration data import"
