from django.db import models
from django.utils import timezone

from hope.models.api_token import APIToken


class APILogEntry(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    token = models.ForeignKey(APIToken, on_delete=models.PROTECT)
    url = models.URLField()
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()

    class Meta:
        app_label = "api"
        verbose_name_plural = "Api Log Entries"

    def __str__(self) -> str:
        return f"{self.url} {self.method} {self.status_code}"
