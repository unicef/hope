import binascii
import os
from typing import Any

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hope.apps.account.fields import ChoiceArrayField
from hope.models.business_area import BusinessArea
from hope.models.grant import Grant
from hope.models.user import User


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

    class Meta:
        app_label = "api"
