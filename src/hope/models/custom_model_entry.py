from typing import Any

from django_celery_beat.models import PeriodicTask
from django_celery_beat.schedulers import DatabaseScheduler, ModelEntry


class CustomModelEntry(ModelEntry):
    """Don't update existing tasks."""

    @classmethod
    def from_entry(cls, name: str, app: str | None = None, **entry: Any) -> "CustomModelEntry":
        obj, _ = PeriodicTask._default_manager.get_or_create(
            name=name,
            defaults=cls._unpack_fields(**entry),
        )
        return cls(obj, app=app)


class CustomDatabaseScheduler(DatabaseScheduler):
    Entry = CustomModelEntry
