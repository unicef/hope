from django.contrib.auth.models import AbstractUser

from model_utils.models import UUIDModel


class User(AbstractUser, UUIDModel):
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
