from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import Choices


class StorageFile(models.Model):
    STATUS_NOT_PROCESSED = "Not processed"
    STATUS_PROCESSING = "Processing"
    STATUS_FINISHED = "Finished"
    STATUS_FAILED = "Failed"

    STATUS_CHOICE = Choices(
        (STATUS_NOT_PROCESSED, _("Not processed")),
        (STATUS_PROCESSING, _("Processing")),
        (STATUS_FINISHED, _("Finished")),
        (STATUS_FAILED, _("Failed")),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to="files")

    status = models.CharField(
        choices=STATUS_CHOICE,
        default=STATUS_NOT_PROCESSED,
        max_length=25,
    )

    class Meta:
        app_label = "core"

    def __str__(self) -> str:
        return self.file.name

    @property
    def file_name(self) -> str:
        return self.file.name

    @property
    def file_url(self) -> str:
        return self.file.url

    @property
    def file_size(self) -> int:
        return self.file.size
