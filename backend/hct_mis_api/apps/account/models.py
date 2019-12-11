from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from model_utils.models import UUIDModel


class User(AbstractUser, UUIDModel):
    first_name = models.CharField(max_length=64, default="")
    last_name = models.CharField(max_length=64, default="")
    phone_number = models.CharField(max_length=16, default="")

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)
