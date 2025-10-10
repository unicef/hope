from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from fernet_fields import EncryptedCharField
from model_utils.models import TimeStampedModel


class FileTemp(TimeStampedModel):
    """Use this model for temporary store files."""

    object_id = models.CharField(max_length=120, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    file = models.FileField()
    was_downloaded = models.BooleanField(default=False)
    password = EncryptedCharField(max_length=255, null=True, blank=True)
    xlsx_password = EncryptedCharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.file.name} - {self.created}"

    class Meta:
        app_label = "core"
