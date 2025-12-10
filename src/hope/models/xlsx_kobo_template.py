from typing import Optional

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import SoftDeletableModel

from hope.models.utils import TimeStampedUUIDModel


class XLSXKoboTemplateManager(models.Manager):
    def latest_valid(self) -> Optional["XLSXKoboTemplate"]:
        return (
            self.get_queryset()
            .filter(status=self.model.SUCCESSFUL)
            .exclude(template_id__exact="")
            .order_by("-created_at")
            .first()
        )


class XLSXKoboTemplate(SoftDeletableModel, TimeStampedUUIDModel):
    SUCCESSFUL = "SUCCESSFUL"
    UPLOADED = "UPLOADED"
    UNSUCCESSFUL = "UNSUCCESSFUL"
    PROCESSING = "PROCESSING"
    CONNECTION_FAILED = "CONNECTION_FAILED"
    KOBO_FORM_UPLOAD_STATUS_CHOICES = (
        (CONNECTION_FAILED, _("Connection failed")),
        (PROCESSING, _("Processing")),
        (SUCCESSFUL, _("Successful")),
        (UNSUCCESSFUL, _("Unsuccessful")),
        (UPLOADED, _("Uploaded")),
    )

    file_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    file = models.FileField()
    error_description = models.TextField(blank=True)
    status = models.CharField(max_length=200, choices=KOBO_FORM_UPLOAD_STATUS_CHOICES)
    template_id = models.CharField(max_length=200, blank=True)
    first_connection_failed_time = models.DateTimeField(null=True, blank=True)

    objects = XLSXKoboTemplateManager()

    class Meta:
        app_label = "core"
        ordering = ("-created_at",)
        permissions = (
            ("download_last_valid_file", "Can download the last valid KOBO template"),
            ("rerun_kobo_import", "Can rerun a KOBO import"),
        )

    def __str__(self) -> str:
        return f"{self.file_name} - {self.created_at}"
