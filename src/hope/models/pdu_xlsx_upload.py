import json

from django.conf import settings
from django.db import models

from hope.models.pdu_xlsx_template import PDUXlsxTemplate
from hope.models.utils import CeleryEnabledModel, TimeStampedModel


class PDUXlsxUpload(TimeStampedModel, CeleryEnabledModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        NOT_SCHEDULED = "NOT_SCHEDULED", "Not scheduled"
        PROCESSING = "PROCESSING", "Processing"
        SUCCESSFUL = "SUCCESSFUL", "Successful"
        FAILED = "FAILED", "Failed"
        CANCELED = "CANCELED", "Canceled"

    template = models.ForeignKey(
        PDUXlsxTemplate,
        on_delete=models.CASCADE,
        related_name="uploads",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="pdu_uploads",
        null=True,
        blank=True,
    )
    file = models.FileField()
    error_message = models.TextField(null=True, blank=True)

    ordering = ["-created_at"]

    celery_task_names = {"import": "hope.apps.periodic_data_update.celery_tasks.import_periodic_data_update"}

    class Meta:
        app_label = "periodic_data_update"

    @property
    def errors(self) -> dict | None:
        if not self.error_message:
            return None
        return json.loads(self.error_message)

    @property
    def combined_status(self) -> str:  # pragma: no cover
        celery_status = self.get_celery_status()

        status_map = {
            self.Status.SUCCESSFUL: self.Status.SUCCESSFUL,
            self.Status.FAILED: self.Status.FAILED,
            self.CELERY_STATUS_SUCCESS: self.Status.SUCCESSFUL,
            self.CELERY_STATUS_STARTED: self.Status.PROCESSING,
            self.CELERY_STATUS_FAILURE: self.Status.FAILED,
            self.CELERY_STATUS_NOT_SCHEDULED: self.Status.NOT_SCHEDULED,
            self.CELERY_STATUS_RECEIVED: self.Status.PENDING,
            self.CELERY_STATUS_RETRY: self.Status.PENDING,
            self.CELERY_STATUS_REVOKED: self.Status.CANCELED,
            self.CELERY_STATUS_CANCELED: self.Status.CANCELED,
        }

        if self.status in status_map:
            return status_map[self.status]
        if celery_status in status_map:
            return status_map[celery_status]

        return self.status

    @property
    def combined_status_display(self) -> str:
        status_dict = {status.value: status.label for status in self.Status}
        return status_dict[self.combined_status]
