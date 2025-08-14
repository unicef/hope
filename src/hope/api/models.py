import binascii
import os
from enum import Enum, auto, unique
from typing import Any

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hope.apps.account.models import ChoiceArrayField, User
from hope.apps.core.models import BusinessArea


@unique
class Grant(Enum):
    def _generate_next_value_(self: str, start: int, count: int, last_values: list[Any]) -> Any:  # type: ignore # FIXME: signature differs from superclass
        return self

    API_READ_ONLY = auto()
    API_RDI_UPLOAD = auto()
    API_RDI_CREATE = auto()

    API_PROGRAM_CREATE = auto()

    @classmethod
    def choices(cls) -> tuple[tuple[Any, Any], ...]:
        return tuple((i.value, i.value) for i in cls)


class APIToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(_("Key"), max_length=40, unique=True, blank=True)
    grants = ChoiceArrayField(
        models.CharField(choices=Grant.choices(), max_length=255),
    )
    valid_from = models.DateField(default=timezone.now)
    valid_to = models.DateField(blank=True, null=True)
    valid_for = models.ManyToManyField(BusinessArea)
    allowed_ips = models.CharField(_("IPs"), max_length=200, blank=True, null=True)

    def __str__(self) -> str:
        return f"Token #{self.pk}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls) -> str:
        return binascii.hexlify(os.urandom(20)).decode()


class APILogEntry(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    token = models.ForeignKey(APIToken, on_delete=models.PROTECT)
    url = models.URLField()
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()

    class Meta:
        verbose_name_plural = "Api Log Entries"

    def __str__(self) -> str:
        return f"{self.url} {self.method} {self.status_code}"
