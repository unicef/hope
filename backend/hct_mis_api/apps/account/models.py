from django.contrib.auth.models import AbstractUser
from django.db import models

from model_utils.models import UUIDModel


class User(AbstractUser, UUIDModel):
    business_areas = models.ManyToManyField("core.BusinessArea", blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
