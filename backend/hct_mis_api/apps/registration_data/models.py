from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from registration_datahub.models import ImportedIndividual
from utils.models import TimeStampedUUIDModel


class RegistrationDataImport(TimeStampedUUIDModel):
    IMPORTING = "IMPORTING"
    IN_REVIEW = "IN_REVIEW"
    MERGING = "MERGING"
    MERGED = "MERGED"
    DEDUPLICATION_FAILED = "DEDUPLICATION_FAILED"
    DEDUPLICATION = "DEDUPLICATION"
    STATUS_CHOICE = (
        (IN_REVIEW, _("In Review")),
        (MERGED, _("Merged")),
        (MERGING, _("Merging")),
        (IMPORTING, _("Importing")),
        (DEDUPLICATION_FAILED, _("Deduplication Failed")),
        (DEDUPLICATION, _("Deduplication")),
    )
    DATA_SOURCE_CHOICE = (
        ("XLS", "Excel"),
        ("KOBO", "KoBo"),
    )
    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICE, default=IN_REVIEW,)
    import_date = models.DateTimeField(auto_now_add=True)
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="registration_data_imports", on_delete=models.CASCADE,
    )
    data_source = models.CharField(max_length=255, choices=DATA_SOURCE_CHOICE,)
    number_of_individuals = models.PositiveIntegerField()
    number_of_households = models.PositiveIntegerField()
    datahub_id = models.UUIDField(null=True, default=None)
    error_message = models.TextField(blank=True)

    business_area = models.ForeignKey("core.BusinessArea", null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @cached_property
    def all_imported_individuals(self):
        return ImportedIndividual.objects.filter(registration_data_import=self.datahub_id)

    class Meta:
        unique_together = ("name", "business_area")
