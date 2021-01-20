from django.db import models


# Create your models here.
from hct_mis_api.apps.steficon.interpreters import interpreters
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel


class Rule(TimeStampedUUIDModel):
    LANGUAGES = ([a.label.lower(), a.label] for a in interpreters)
    name = models.CharField(max_length=100, unique=True)
    definition = models.TextField(blank=True)
    enabled = models.BooleanField(default=False)
    deprecated = models.BooleanField(default=False)
    language = models.CharField(max_length=10, choices=LANGUAGES)

    def __str__(self):
        return self.name
