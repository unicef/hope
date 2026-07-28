from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from encrypted_fields.fields import EncryptedTextField
from model_utils.models import TimeStampedModel

from hope.models.utils import UniqueUploadPath, upload_basename


class FileTemp(TimeStampedModel):
    """Use this model for temporary store files."""

    object_id = models.CharField(max_length=120, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    file = models.FileField(upload_to=UniqueUploadPath("file_temp"), max_length=255)
    was_downloaded = models.BooleanField(default=False)
    password = EncryptedTextField(max_length=255, null=True, blank=True)
    xlsx_password = EncryptedTextField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return f"{upload_basename(self.file.name)} - {self.created}"

    class Meta:
        app_label = "core"
        ordering = ("id",)
