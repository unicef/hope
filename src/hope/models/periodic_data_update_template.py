from django.conf import settings
from django.db import models

from hope.models.file_temp import FileTemp
from hope.models.utils import CeleryEnabledModel, TimeStampedModel


class PeriodicDataUpdateTemplate(TimeStampedModel, CeleryEnabledModel):
    class Status(models.TextChoices):
        TO_EXPORT = "TO_EXPORT", "To export"
        NOT_SCHEDULED = "NOT_SCHEDULED", "Not scheduled"
        EXPORTING = "EXPORTING", "Exporting"
        EXPORTED = "EXPORTED", "Exported"
        FAILED = "FAILED", "Failed"
        CANCELED = "CANCELED", "Canceled"

    business_area = models.ForeignKey(
        "core.BusinessArea",
        on_delete=models.CASCADE,
        related_name="periodic_data_update_templates",
    )
    program = models.ForeignKey(
        "program.Program",
        on_delete=models.CASCADE,
        related_name="periodic_data_update_templates",
    )
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
    number_of_records = models.PositiveIntegerField(null=True, blank=True)
    file = models.ForeignKey(FileTemp, null=True, blank=True, related_name="+", on_delete=models.SET_NULL)
    """
    {
    "registration_data_import_id": id,
    "target_population_id": id,
    "gender": "MALE"/"FEMALE",
    "age": {
        "from": 0,
        "to": 100
    },
    "registration_date": {
        "from": "2021-01-01",
        "to": "2021-12-31"
    },
    "has_grievance_ticket: true/false,
    "admin1": [id],
    "admin2": [id],
    "received_assistance": true/false,
    }
    """
    filters = models.JSONField(default=dict, blank=True, null=True)
    """
    Example of rounds_data:
        [
            {
                "field": "Vaccination Records Update",
                "round": 2,
                "round_name": "February vaccination",
                "number_of_records": 100,
            },
            {
                "field": "Health Records Update",
                "round": 4,
                "round_name": "April",
                "number_of_records": 58,
            },
        ]
    """
    rounds_data = models.JSONField()

    celery_task_name = "hope.apps.periodic_data_update.celery_tasks.export_periodic_data_update_export_template_service"

    class Meta:
        app_label = "periodic_data_update"

    @property
    def combined_status(self) -> str:  # pragma: no cover
        if self.status == self.Status.EXPORTED or self.celery_status == self.CELERY_STATUS_SUCCESS:
            return self.status
        if self.status == self.Status.FAILED:
            return self.status
        if self.celery_status == self.CELERY_STATUS_STARTED:
            return self.Status.EXPORTING
        if self.celery_status == self.CELERY_STATUS_FAILURE:
            return self.Status.FAILED
        if self.celery_status == self.CELERY_STATUS_NOT_SCHEDULED:
            return self.Status.NOT_SCHEDULED
        if self.celery_status == self.CELERY_STATUS_RECEIVED:
            return self.Status.TO_EXPORT
        if self.celery_status == self.CELERY_STATUS_RETRY:
            return self.Status.TO_EXPORT
        if self.celery_status in [
            self.CELERY_STATUS_REVOKED,
            self.CELERY_STATUS_CANCELED,
        ]:
            return self.Status.CANCELED
        return self.status

    @property
    def can_export(self) -> bool:
        return self.status == self.Status.TO_EXPORT and self.celery_status == self.CELERY_STATUS_NOT_SCHEDULED

    @property
    def combined_status_display(self) -> str:
        status_dict = {status.value: status.label for status in self.Status}
        return status_dict[self.combined_status]

    def __str__(self) -> str:
        return f"{self.pk} - {self.status}"
