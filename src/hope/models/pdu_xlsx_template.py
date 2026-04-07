from celery import states
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxLengthValidator, MinLengthValidator, ProhibitNullCharactersValidator
from django.db import models
from django.db.models import UniqueConstraint
from django_celery_boost.models import AsyncJobModel

from hope.apps.utils.validators import DoubleSpaceValidator, StartEndSpaceValidator
from hope.models.async_job import AsyncJob
from hope.models.file_temp import FileTemp
from hope.models.utils import AdminUrlMixin, TimeStampedModel


class PDUXlsxTemplate(TimeStampedModel, AdminUrlMixin):
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
        TO_EXPORT = "TO_EXPORT", "To export"
        NOT_SCHEDULED = "NOT_SCHEDULED", "Not scheduled"
        EXPORTING = "EXPORTING", "Exporting"
        EXPORTED = "EXPORTED", "Exported"
        FAILED = "FAILED", "Failed"
        CANCELED = "CANCELED", "Canceled"

    name = models.CharField(
        max_length=255,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(255),
            DoubleSpaceValidator,
            StartEndSpaceValidator,
            ProhibitNullCharactersValidator(),
        ],
        null=True,
        blank=True,
    )
    business_area = models.ForeignKey(
        "core.BusinessArea",
        on_delete=models.CASCADE,
        related_name="pdu_xlsx_templates",
    )
    program = models.ForeignKey(
        "program.Program",
        on_delete=models.CASCADE,
        related_name="pdu_xlsx_templates",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TO_EXPORT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="pdu_xlsx_templates_created",
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

    ordering = ["-created_at"]

    EXPORT_JOB_NAME = "export_periodic_data_update_export_template_service_async_task"

    class Meta:
        app_label = "periodic_data_update"
        constraints = [
            UniqueConstraint(
                fields=["name", "program"],
                name="pdu_xlsx_template_name_unique_per_program",
            ),
        ]
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

    def _get_active_async_job_status(self, job_name: str) -> str:
        status = self._get_async_job_status(job_name)
        if status in self.CELERY_STATUS_SCHEDULED:
            return status
        return self.CELERY_STATUS_NOT_SCHEDULED

    @property
    def combined_status(self) -> str:  # pragma: no cover
        active_celery_status = self._get_active_async_job_status(self.EXPORT_JOB_NAME)
        if active_celery_status == self.CELERY_STATUS_STARTED:
            return self.Status.EXPORTING
        if active_celery_status in {
            states.PENDING,
            self.CELERY_STATUS_QUEUED,
            self.CELERY_STATUS_RECEIVED,
            self.CELERY_STATUS_RETRY,
        }:
            return self.Status.TO_EXPORT
        return self.status

    @property
    def can_export(self) -> bool:
        return (
            self.status == self.Status.TO_EXPORT
            and self._get_active_async_job_status(self.EXPORT_JOB_NAME) == self.CELERY_STATUS_NOT_SCHEDULED
        )

    @property
    def combined_status_display(self) -> str:
        status_dict = {status.value: status.label for status in self.Status}
        return status_dict[self.combined_status]

    def __str__(self) -> str:
        return f"{self.pk} - {self.status}"
