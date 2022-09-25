import binascii
import os
from enum import Enum, auto, unique

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..apps.account.models import ChoiceArrayField, User
from ..apps.core.models import BusinessArea


@unique
class Grant(Enum):
    def _generate_next_value_(name, *args):
        return name

    API_READ_ONLY = auto()
    API_UPLOAD_RDI = auto()
    API_CREATE_RDI = auto()

    @classmethod
    def choices(cls):
        return tuple((i.value, i.value) for i in cls)


class APIToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(_("Key"), max_length=40, unique=True, blank=True)
    allowed_ips = models.CharField(_("IPs"), max_length=200, blank=True, null=True)
    valid_from = models.DateField(default=timezone.now)
    valid_to = models.DateField(blank=True, null=True)

    valid_for = models.ManyToManyField(BusinessArea)
    grants = ChoiceArrayField(
        models.CharField(choices=Grant.choices(), max_length=255),
    )

    def __str__(self):
        return f"Token #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()


class APILogEntry(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    token = models.ForeignKey(APIToken, on_delete=models.PROTECT)
    url = models.URLField()
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
