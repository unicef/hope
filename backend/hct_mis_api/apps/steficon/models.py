from django.db import models


# Create your models here.
from steficon.interpreters import interpreters


class Rule(models.Model):
    LANGUAGES = ([a.label.lower(), a.label] for a in interpreters)
    name = models.CharField(max_length=100, unique=True)
    definition = models.TextField(blank=True)
    enabled = models.BooleanField(default=False)
    deprecated = models.BooleanField(default=False)
    language = models.CharField(max_length=10, choices=LANGUAGES)
