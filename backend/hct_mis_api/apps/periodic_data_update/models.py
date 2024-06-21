from django.conf import settings
from django.db import models

from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.utils.models import TimeStampedModel


class PeriodicDataUpdateTemplate(TimeStampedModel):
    class Status(models.TextChoices):
        TO_EXPORT = "TO_EXPORT", "To export"
        EXPORTING = "EXPORTING", "Exporting"
        EXPORTED = "EXPORTED", "Exported"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TO_EXPORT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="periodic_data_updates_created",
        null=True,
        blank=True,
    )
    file = models.ForeignKey(FileTemp, null=True, blank=True, related_name="+", on_delete=models.SET_NULL)
    program = models.ForeignKey(
        "program.Program",
        on_delete=models.CASCADE,
        related_name="periodic_data_update_templates",
    )
    business_area = models.ForeignKey(
        "core.BusinessArea",
        on_delete=models.CASCADE,
        related_name="periodic_data_update_templates",
    )
    filters = models.JSONField()
    rounds_data = models.JSONField()
    """
    Example of rounds_data:
        {
            {
                "Vaccination Records Update": {
                "round": 2,
                "round_name": "February vaccination",
                "number_of_records": 100,
                }

            },
            {
                "Health Records Update": {
                "round": 4,
                "round_name": "April",
                "number_of_records": 58,
                }

            },
        }
    """
    number_of_records = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.pk} - {self.status}"


class PeriodicDataUpdateUpload(TimeStampedModel):
    class Status(models.TextChoices):
        PROCESSING = "PROCESSING", "Processing"
        SUCCESSFUL = "SUCCESSFUL", "Successful"
        FAILED = "FAILED", "Failed"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROCESSING,
    )
    template = models.ForeignKey(
        PeriodicDataUpdateTemplate,
        on_delete=models.CASCADE,
        related_name="uploads",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="periodic_data_update_uploads",
        null=True,
        blank=True,
    )
    file = models.FileField()
