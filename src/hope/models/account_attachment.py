from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from hope.models.account import Account


class AccountAttachment(models.Model):
    FILE_LIMIT = 10  # max 10 files per Account
    FILE_SIZE_LIMIT = 10 * 1024 * 1024  # 10 MB

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="attachments")
    title = models.CharField(max_length=255, blank=True, default="")
    file = models.FileField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    class Meta:
        app_label = "payment"
        ordering = ["uploaded_at"]

    def __str__(self) -> str:
        return self.title or self.file.name or ""

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        super().clean()
        if not self._state.adding:
            return
        if self.file and self.file.size > self.FILE_SIZE_LIMIT:
            raise ValidationError(f"File size must be ≤ {self.FILE_SIZE_LIMIT // (1024 * 1024)}MB.")
        if self.account_id and AccountAttachment.objects.filter(account_id=self.account_id).count() >= self.FILE_LIMIT:
            raise ValidationError(f"Account already has the maximum of {self.FILE_LIMIT} attachments.")
