from django.db import models
from django_countries.fields import CountryField
from model_utils.models import UUIDModel


class Location(UUIDModel):
    name = models.CharField(max_length=256)
    country = CountryField()

    def __str__(self):
        return self.name
