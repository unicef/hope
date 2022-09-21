import binascii
import os

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..apps.account.models import User
from ..apps.core.models import BusinessArea


class APIToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    allowed_ips = models.CharField(_("IPs"), max_length=200)
    valid_from = models.DateField(default=timezone.now)
    valid_to = models.DateField(blank=True, null=True)
    valid_for = models.ManyToManyField(BusinessArea)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
