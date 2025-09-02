import json

from django.conf import settings
from django.db import models

from hope.models.periodic_data_update_template import PeriodicDataUpdateTemplate
from hope.models.utils import CeleryEnabledModel, TimeStampedModel


class PeriodicDataUpdateUpload(TimeStampedModel, CeleryEnabledModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        NOT_SCHEDULED = "NOT_SCHEDULED", "Not scheduled"
        PROCESSING = "PROCESSING", "Processing"
        SUCCESSFUL = "SUCCESSFUL", "Successful"
        FAILED = "FAILED", "Failed"
        CANCELED = "CANCELED", "Canceled"

    template = models.ForeignKey(
        PeriodicDataUpdateTemplate,
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
        related_name="periodic_data_update_uploads",
        null=True,
        blank=True,
    )
    file = models.FileField()
    error_message = models.TextField(null=True, blank=True)
    celery_task_name = "hope.apps.periodic_data_update.celery_tasks.import_periodic_data_update"

    class Meta:
        app_label = "periodic_data_update"

    @property
    def errors(self) -> dict | None:
        if not self.error_message:
            return None
        return json.loads(self.error_message)

    @property
    def combined_status(self) -> str:  # pragma: no cover
        if self.status == self.Status.SUCCESSFUL or self.celery_status == self.CELERY_STATUS_SUCCESS:
            return self.status
        if self.status == self.Status.FAILED:
            return self.status
        if self.celery_status == self.CELERY_STATUS_STARTED:
            return self.Status.PROCESSING
        if self.celery_status == self.CELERY_STATUS_FAILURE:
            return self.Status.FAILED
        if self.celery_status == self.CELERY_STATUS_NOT_SCHEDULED:
            return self.Status.NOT_SCHEDULED
        if self.celery_status == self.CELERY_STATUS_RECEIVED:
            return self.Status.PENDING
        if self.celery_status == self.CELERY_STATUS_RETRY:
            return self.Status.PENDING
        if self.celery_status in [
            self.CELERY_STATUS_REVOKED,
            self.CELERY_STATUS_CANCELED,
        ]:
            return self.Status.CANCELED

        return self.status

    @property
    def combined_status_display(self) -> str:
        status_dict = {status.value: status.label for status in self.Status}
        return status_dict[self.combined_status]
