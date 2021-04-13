import os

from celery import Celery
from django_celery_beat.models import PeriodicTask
from django_celery_beat.schedulers import ModelEntry, DatabaseScheduler


class CustomModelEntry(ModelEntry):
    """
    don't update existing tasks
    """
    @classmethod
    def from_entry(cls, name, app=None, **entry):
        obj, _ = PeriodicTask._default_manager.get_or_create(
            name=name, defaults=cls._unpack_fields(**entry),
        )
        return cls(obj, app=app)


class CustomDatabaseScheduler(DatabaseScheduler):
    Entry = CustomModelEntry
