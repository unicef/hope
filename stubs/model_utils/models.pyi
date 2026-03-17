from typing import Any, Self

from django.db import models

from model_utils.managers import SoftDeletableManager

class TimeStampedModel(models.Model):
    created: models.DateTimeField
    modified: models.DateTimeField
    class Meta:
        abstract: bool

class UUIDModel(models.Model):
    class Meta:
        abstract: bool

class SoftDeletableModel(models.Model):
    is_removed: models.BooleanField
    objects: SoftDeletableManager[Self]  # type: ignore[assignment]
    available_objects: SoftDeletableManager[Self]  # type: ignore[assignment]
    all_objects: models.Manager[Self]  # type: ignore[assignment]
    class Meta:
        abstract: bool
