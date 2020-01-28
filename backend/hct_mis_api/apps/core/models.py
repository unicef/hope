from django.contrib.postgres.fields import JSONField
from django.db import models
from django_countries.fields import CountryField
from model_utils.models import UUIDModel


class Location(UUIDModel):
    name = models.CharField(max_length=255)
    country = CountryField()

    def __str__(self):
        return self.name


class FlexibleField(UUIDModel):
    type = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    required = models.BooleanField()
    relevant = models.TextField(blank=True)
    calculation = models.TextField(blank=True)
    constraint_message = models.TextField(blank=True)
    default = models.TextField(blank=True)
    label = JSONField()
    hint = JSONField()
    choice_filter = models.TextField(blank=True)
    repeat_count = models.CharField(max_length=255, blank=True)
    read_only = models.BooleanField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
