import json

from celery import states
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_celery_boost.models import AsyncJobModel

from hope.models.async_job import AsyncJob
from hope.models.pdu_xlsx_template import PDUXlsxTemplate
from hope.models.utils import TimeStampedModel


class PDUXlsxUpload(TimeStampedModel):
    CELERY_STATUS_SCHEDULED = frozenset({states.PENDING, states.RECEIVED, states.STARTED, states.RETRY, "QUEUED"})
    CELERY_STATUS_QUEUED = AsyncJobModel.QUEUED
    CELERY_STATUS_CANCELED = AsyncJobModel.CANCELED
    CELERY_STATUS_RECEIVED = states.RECEIVED
    CELERY_STATUS_NOT_SCHEDULED = "NOT_SCHEDULED"
    CELERY_STATUS_STARTED = states.STARTED
    CELERY_STATUS_SUCCESS = states.SUCCESS
    CELERY_STATUS_FAILURE = states.FAILURE
    CELERY_STATUS_RETRY = states.RETRY
    CELERY_STATUS_REVOKED = states.REVOKED

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

    IMPORT_JOB_NAME = "import_periodic_data_update_async_task"

    class Meta:
        app_label = "periodic_data_update"
        ordering = ("-created_at",)

    def _get_async_job(self, job_name: str) -> AsyncJob | None:
        return self.async_jobs.filter(job_name=job_name).order_by("-datetime_created", "-pk").first()

    @property
    def async_jobs(self):
        if self.pk is None:
            return AsyncJob.objects.none()

        content_type = ContentType.objects.get_for_model(self, for_concrete_model=False)
        return AsyncJob.objects.filter(
            content_type=content_type,
            object_id=str(self.pk),
        )

    def _get_async_job_status(self, job_name: str) -> str:
        job = self._get_async_job(job_name)
        if not job:
            return self.CELERY_STATUS_NOT_SCHEDULED

        if job.local_status in {job.CANCELED, job.REVOKED}:
            return job.local_status

        status = job.task_status
        if status in {job.NOT_SCHEDULED, job.MISSING}:
            return self.CELERY_STATUS_NOT_SCHEDULED
        return status

    @property
    def errors(self) -> dict | None:
        if not self.error_message:
            return None
        return json.loads(self.error_message)

    @property
    def combined_status(self) -> str:
        celery_status = self._get_async_job_status(self.IMPORT_JOB_NAME)

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
