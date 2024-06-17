from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel

from hct_mis_api.apps.core.models import FileTemp


class PeriodicDataUpdateTemplate(TimeStampedModel):
    class Status(models.TextChoices):
        TO_EXPORT = 'TO_EXPORT', 'To export'
        EXPORTING = 'EXPORTING', 'Exporting'
        EXPORTED = 'EXPORTED', 'Exported'

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TO_EXPORT,
    )
    rounds_data = models.JSONField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="periodic_data_updates_created",
        null=True,
        blank=True,
    )
    filters = models.JSONField()
    number_of_records = models.PositiveIntegerField()
    file = models.ForeignKey(
        FileTemp, null=True, blank=True, related_name="+", on_delete=models.SET_NULL
    )


    def __str__(self):
        return f"{self.pk} - {self.status}"
