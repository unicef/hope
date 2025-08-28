import json

from django.conf import settings
from django.core.validators import MaxLengthValidator, MinLengthValidator, ProhibitNullCharactersValidator
from django.db import models
from django.db.models import UniqueConstraint

from hope.apps.core.models import FileTemp
from hope.apps.utils.models import CeleryEnabledModel, TimeStampedModel
from hope.apps.utils.validators import DoubleSpaceValidator, StartEndSpaceValidator


class PDUXlsxTemplate(TimeStampedModel, CeleryEnabledModel):
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

    celery_task_names = {
        "export": "hope.apps.periodic_data_update.celery_tasks.export_periodic_data_update_export_template_service"
    }

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["name", "program"],
                name="pdu_xlsx_template_name_unique_per_program",
            ),
        ]

    @property
    def combined_status(self) -> str:  # pragma: no cover
        if self.status == self.Status.EXPORTED or self.get_celery_status() == self.CELERY_STATUS_SUCCESS:
            return self.status
        if self.status == self.Status.FAILED:
            return self.status
        if self.get_celery_status() == self.CELERY_STATUS_STARTED:
            return self.Status.EXPORTING
        if self.get_celery_status() == self.CELERY_STATUS_FAILURE:
            return self.Status.FAILED
        if self.get_celery_status() == self.CELERY_STATUS_NOT_SCHEDULED:
            return self.Status.NOT_SCHEDULED
        if self.get_celery_status() in [self.CELERY_STATUS_RECEIVED, self.CELERY_STATUS_RETRY]:
            return self.Status.TO_EXPORT
        if self.get_celery_status() in [self.CELERY_STATUS_REVOKED, self.CELERY_STATUS_CANCELED]:
            return self.Status.CANCELED
        return self.status

    @property
    def can_export(self) -> bool:
        return self.status == self.Status.TO_EXPORT and self.get_celery_status() == self.CELERY_STATUS_NOT_SCHEDULED

    @property
    def combined_status_display(self) -> str:
        status_dict = {status.value: status.label for status in self.Status}
        return status_dict[self.combined_status]

    def __str__(self) -> str:
        return f"{self.pk} - {self.status}"


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

    @property
    def errors(self) -> dict | None:
        if not self.error_message:
            return None
        return json.loads(self.error_message)

    @property
    def combined_status(self) -> str:  # pragma: no cover
        if self.status == self.Status.SUCCESSFUL or self.get_celery_status() == self.CELERY_STATUS_SUCCESS:
            return self.status
        if self.status == self.Status.FAILED:
            return self.status
        if self.get_celery_status() == self.CELERY_STATUS_STARTED:
            return self.Status.PROCESSING
        if self.get_celery_status() == self.CELERY_STATUS_FAILURE:
            return self.Status.FAILED
        if self.get_celery_status() == self.CELERY_STATUS_NOT_SCHEDULED:
            return self.Status.NOT_SCHEDULED
        if self.get_celery_status() in [self.CELERY_STATUS_RECEIVED, self.CELERY_STATUS_RETRY]:
            return self.Status.PENDING
        if self.get_celery_status() in [self.CELERY_STATUS_REVOKED, self.CELERY_STATUS_CANCELED]:
            return self.Status.CANCELED

        return self.status

    @property
    def combined_status_display(self) -> str:
        status_dict = {status.value: status.label for status in self.Status}
        return status_dict[self.combined_status]


class PDUOnlineEdit(TimeStampedModel, CeleryEnabledModel):
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


class PDUOnlineEditSentBackComment(TimeStampedModel):
    pdu_online_edit = models.OneToOneField(
        PDUOnlineEdit,
        on_delete=models.CASCADE,
        related_name="sent_back_comment",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="sent_back_comments",
        null=True,
    )
    comment = models.TextField()

    class Meta:
        ordering = ["-created_at"]
