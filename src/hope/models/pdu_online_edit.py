from celery import states
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxLengthValidator, MinLengthValidator, ProhibitNullCharactersValidator
from django.db import models
from django.db.models import UniqueConstraint
from django_celery_boost.models import AsyncJobModel

from hope.apps.utils.validators import DoubleSpaceValidator, StartEndSpaceValidator
from hope.models.async_job import AsyncJob
from hope.models.utils import AdminUrlMixin, TimeStampedModel


class PDUOnlineEdit(AdminUrlMixin, TimeStampedModel):
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
        PENDING_CREATE = "PENDING_CREATE", "Pending create"
        NEW = "NEW", "New"
        READY = "READY", "Ready"  # sent for approval
        APPROVED = "APPROVED", "Approved"
        PENDING_MERGE = "PENDING_MERGE", "Pending merge"
        MERGED = "MERGED", "Merged"

        # tasks statuses
        NOT_SCHEDULED_CREATE = "NOT_SCHEDULED_CREATE", "Not scheduled create"
        CREATING = "CREATING", "Creating"
        FAILED_CREATE = "FAILED_CREATE", "Failed create"
        CANCELED_CREATE = "CANCELED_CREATE", "Canceled create"
        NOT_SCHEDULED_MERGE = "NOT_SCHEDULED_MERGE", "Not scheduled merge"
        MERGING = "MERGING", "Processing"
        FAILED_MERGE = "FAILED_MERGE", "Failed merge"
        CANCELED_MERGE = "CANCELED_MERGE", "Canceled merge"

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
        related_name="pdu_online_edits",
    )
    program = models.ForeignKey(
        "program.Program",
        on_delete=models.CASCADE,
        related_name="pdu_online_edits",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_CREATE,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="pdu_online_edits_created",
        null=True,
        blank=True,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="pdu_online_edits_approved",
        null=True,
        blank=True,
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    edit_data = models.JSONField(default=dict, blank=True)
    number_of_records = models.PositiveIntegerField(null=True, blank=True)
    authorized_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="authorized_pdu_online_edits",
        blank=True,
        help_text="Users who are authorized to perform actions on this periodic data update",
    )
    ordering = ["-created_at"]
    GENERATE_EDIT_DATA_JOB_NAME = "generate_edit_data"
    GENERATE_EDIT_DATA_ACTION = "hope.apps.periodic_data_update.celery_tasks.generate_pdu_online_edit_data_task_action"
    MERGE_JOB_NAME = "merge"
    MERGE_ACTION = "hope.apps.periodic_data_update.celery_tasks.merge_pdu_online_edit_task_action"

    class Meta:
        app_label = "periodic_data_update"
        constraints = [
            UniqueConstraint(
                fields=["name", "program"],
                name="pdu_online_name_unique_per_program",
            ),
        ]
        ordering = ("-created_at",)

    def _get_async_job(self, job_name: str, action: str) -> AsyncJob | None:
        return self.async_jobs.filter(job_name=job_name, action=action).order_by("-datetime_created", "-pk").first()

    @property
    def async_jobs(self):
        if self.pk is None:
            return AsyncJob.objects.none()

        content_type = ContentType.objects.get_for_model(self, for_concrete_model=False)
        return AsyncJob.objects.filter(
            content_type=content_type,
            object_id=str(self.pk),
        )

    def _get_async_job_status(self, job_name: str, action: str) -> str:
        job = self._get_async_job(job_name, action)
        if not job:
            return self.CELERY_STATUS_NOT_SCHEDULED

        if job.local_status in {job.CANCELED, job.REVOKED}:
            return job.local_status

        status = job.task_status
        if status in {job.NOT_SCHEDULED, job.MISSING}:
            return self.CELERY_STATUS_NOT_SCHEDULED
        return status

    @property
    def combined_status(self) -> str:  # pragma: no cover
        status_create = self._get_async_job_status(self.GENERATE_EDIT_DATA_JOB_NAME, self.GENERATE_EDIT_DATA_ACTION)
        status_merge = self._get_async_job_status(self.MERGE_JOB_NAME, self.MERGE_ACTION)

        terminal_statuses = {
            self.Status.NEW,
            self.Status.READY,
            self.Status.APPROVED,
            self.Status.MERGED,
            self.Status.FAILED_CREATE,
            self.Status.FAILED_MERGE,
        }

        if self.status in terminal_statuses or self.CELERY_STATUS_SUCCESS in [status_create, status_merge]:
            return self.status

        create_map = {
            self.CELERY_STATUS_RECEIVED: self.Status.PENDING_CREATE,
            self.CELERY_STATUS_RETRY: self.Status.PENDING_CREATE,
            self.CELERY_STATUS_STARTED: self.Status.CREATING,
            self.CELERY_STATUS_FAILURE: self.Status.FAILED_CREATE,
            self.CELERY_STATUS_NOT_SCHEDULED: self.Status.NOT_SCHEDULED_CREATE,
            self.CELERY_STATUS_REVOKED: self.Status.CANCELED_CREATE,
            self.CELERY_STATUS_CANCELED: self.Status.CANCELED_CREATE,
        }

        merge_map = {
            self.CELERY_STATUS_RECEIVED: self.Status.PENDING_MERGE,
            self.CELERY_STATUS_RETRY: self.Status.PENDING_MERGE,
            self.CELERY_STATUS_STARTED: self.Status.MERGING,
            self.CELERY_STATUS_FAILURE: self.Status.FAILED_MERGE,
            self.CELERY_STATUS_NOT_SCHEDULED: self.Status.NOT_SCHEDULED_MERGE,
            self.CELERY_STATUS_REVOKED: self.Status.CANCELED_MERGE,
            self.CELERY_STATUS_CANCELED: self.Status.CANCELED_MERGE,
        }

        if status_create in create_map:
            return create_map[status_create]
        if status_merge in merge_map:
            return merge_map[status_merge]

        return self.status

    @property
    def combined_status_display(self) -> str:
        status_dict = {status.value: status.label for status in self.Status}
        return status_dict[self.combined_status]
