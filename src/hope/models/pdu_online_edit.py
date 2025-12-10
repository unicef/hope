from django.conf import settings
from django.core.validators import MaxLengthValidator, MinLengthValidator, ProhibitNullCharactersValidator
from django.db import models
from django.db.models import UniqueConstraint

from hope.apps.utils.validators import DoubleSpaceValidator, StartEndSpaceValidator
from hope.models.utils import AdminUrlMixin, CeleryEnabledModel, TimeStampedModel


class PDUOnlineEdit(AdminUrlMixin, TimeStampedModel, CeleryEnabledModel):
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

    celery_task_names = {
        "generate_edit_data": "hope.apps.periodic_data_update.celery_tasks.generate_pdu_online_edit_data_task",
        "merge": "hope.apps.periodic_data_update.celery_tasks.merge_pdu_online_edit_task",
    }

    class Meta:
        app_label = "periodic_data_update"
        constraints = [
            UniqueConstraint(
                fields=["name", "program"],
                name="pdu_online_name_unique_per_program",
            ),
        ]

    @property
    def combined_status(self) -> str:  # pragma: no cover
        status_create = self.get_celery_status(task_name="generate_edit_data")
        status_merge = self.get_celery_status(task_name="merge")

        if self.status in [
            self.Status.NEW,
            self.Status.READY,
            self.Status.APPROVED,
            self.Status.MERGED,
            self.Status.FAILED_CREATE,
            self.Status.FAILED_MERGE,
        ] or self.CELERY_STATUS_SUCCESS in [status_create, status_merge]:
            return self.status

        if status_create in [self.CELERY_STATUS_RECEIVED, self.CELERY_STATUS_RETRY]:
            return self.Status.PENDING_CREATE
        if status_create == self.CELERY_STATUS_STARTED:
            return self.Status.CREATING
        if status_create == self.CELERY_STATUS_FAILURE:
            return self.Status.FAILED_CREATE
        if status_create == self.CELERY_STATUS_NOT_SCHEDULED:
            return self.Status.NOT_SCHEDULED_CREATE
        if status_create in [self.CELERY_STATUS_REVOKED, self.CELERY_STATUS_CANCELED]:
            return self.Status.CANCELED_CREATE

        if status_merge in [self.CELERY_STATUS_RECEIVED, self.CELERY_STATUS_RECEIVED]:
            return self.Status.PENDING_MERGE
        if status_merge == self.CELERY_STATUS_STARTED:
            return self.Status.MERGING
        if status_merge == self.CELERY_STATUS_FAILURE:
            return self.Status.FAILED_MERGE
        if status_merge == self.CELERY_STATUS_NOT_SCHEDULED:
            return self.Status.NOT_SCHEDULED_MERGE
        if status_merge in [self.CELERY_STATUS_REVOKED, self.CELERY_STATUS_CANCELED]:
            return self.Status.CANCELED_MERGE

        return self.status

    @property
    def combined_status_display(self) -> str:
        status_dict = {status.value: status.label for status in self.Status}
        return status_dict[self.combined_status]
