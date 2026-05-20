import logging
from typing import Any

from django_celery_beat.models import PeriodicTask
from django_celery_beat.schedulers import DatabaseScheduler, ModelEntry
from kombu.transport.redis import loads as redis_loads

from hope.apps.core.celery_queues import CELERY_QUEUE_PERIODIC

logger = logging.getLogger(__name__)


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
    queued_task_scan_limit = 1000

    def apply_async(
        self,
        entry: Any,
        producer: Any = None,
        advance: bool = True,
        **kwargs: Any,
    ) -> Any:
        if self._is_periodic_task_already_in_queue(entry):
            logger.info(
                "Scheduler: Skipping due task %s (%s) because it is already queued",
                entry.name,
                entry.task,
            )
            return None
        return super().apply_async(entry, producer=producer, advance=advance, **kwargs)

    def _is_periodic_task_already_in_queue(self, entry: Any) -> bool:
        periodic_task_name = getattr(entry, "name", None)
        if not periodic_task_name:
            return False

        if self._get_queue_name(entry) != CELERY_QUEUE_PERIODIC:
            return False

        with self.app.connection_for_write() as connection:
            if getattr(connection.transport, "driver_type", None) != "redis":
                return False

            channel = connection.channel()
            try:
                client = channel.client
                queue_names = self._get_queue_names_to_scan(channel, CELERY_QUEUE_PERIODIC)
                max_index = self.queued_task_scan_limit - 1

                for redis_queue_name in queue_names:
                    for raw_message in client.lrange(redis_queue_name, 0, max_index):
                        if self._get_periodic_task_name_from_message(raw_message) == periodic_task_name:
                            return True
            finally:
                close = getattr(channel, "close", None)
                if callable(close):
                    close()

        return False

    def _get_queue_name(self, entry: Any) -> str:
        entry_options = getattr(entry, "options", {}) or {}
        return entry_options.get("queue") or self.app.conf.task_default_queue

    def _get_queue_names_to_scan(self, channel: Any, queue_name: str) -> list[str]:
        priority_steps = getattr(channel, "priority_steps", (0,))
        return [channel._q_for_pri(queue_name, priority) for priority in priority_steps]

    @staticmethod
    def _get_periodic_task_name_from_message(raw_message: Any) -> str | None:
        try:
            message = redis_loads(raw_message)
        except (TypeError, ValueError):
            return None

        if isinstance(message, list) and message:
            headers = message[0]
            if isinstance(headers, dict):
                periodic_task_name = headers.get("periodic_task_name")
                if isinstance(periodic_task_name, str):
                    return periodic_task_name

        if isinstance(message, dict):
            headers = message.get("headers")
            if isinstance(headers, dict):
                periodic_task_name = headers.get("periodic_task_name")
                if isinstance(periodic_task_name, str):
                    return periodic_task_name

        return None
