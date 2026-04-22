from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from kombu.transport.redis import dumps as redis_dumps
import pytest

from hope.apps.core.celery_queues import CELERY_QUEUE_PERIODIC
from hope.models.custom_model_entry import CustomDatabaseScheduler


class FakeRedisChannel:
    def __init__(self, messages_by_queue, priority_steps=(0, 3, 6, 9)):
        self.client = MagicMock()
        self.client.lrange.side_effect = lambda queue_name, start, end: messages_by_queue.get(queue_name, [])
        self.priority_steps = priority_steps
        self.closed = False

    def _q_for_pri(self, queue_name, priority):
        return queue_name if priority == 0 else f"{queue_name}\x06\x16{priority}"

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, *, channel, driver_type="redis"):
        self._channel = channel
        self.transport = SimpleNamespace(driver_type=driver_type)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def channel(self):
        return self._channel


@pytest.fixture
def make_scheduler():
    def factory(*, channel, driver_type="redis", default_queue="celery"):
        scheduler = object.__new__(CustomDatabaseScheduler)
        scheduler.app = SimpleNamespace(
            conf=SimpleNamespace(task_default_queue=default_queue),
            connection_for_write=lambda: FakeConnection(channel=channel, driver_type=driver_type),
        )
        return scheduler

    return factory


def test_get_periodic_task_name_from_protocol_v2_message():
    periodic_task_name = "remove_old_cash_plan_payment_verification_xlsx_async_task"
    raw_message = redis_dumps(
        [
            {"periodic_task_name": periodic_task_name},
            {"correlation_id": "abc"},
            [[], {}, {}],
            None,
        ]
    )

    assert CustomDatabaseScheduler._get_periodic_task_name_from_message(raw_message) == periodic_task_name


def test_get_periodic_task_name_from_message_with_headers_dict():
    periodic_task_name = "periodic_grievances_notifications_async_task"
    raw_message = redis_dumps(
        {
            "headers": {
                "periodic_task_name": periodic_task_name,
            }
        }
    )

    assert CustomDatabaseScheduler._get_periodic_task_name_from_message(raw_message) == periodic_task_name


def test_get_periodic_task_name_from_list_message_without_dict_headers_returns_none():
    raw_message = redis_dumps(
        [
            "not-a-dict",
            {"correlation_id": "abc"},
            [[], {}, {}],
            None,
        ]
    )

    assert CustomDatabaseScheduler._get_periodic_task_name_from_message(raw_message) is None


def test_get_periodic_task_name_from_dict_message_without_periodic_task_name_returns_none():
    raw_message = redis_dumps(
        {
            "headers": {
                "task": "hope.apps.grievance.celery_tasks.periodic_grievances_notifications_async_task",
            }
        }
    )

    assert CustomDatabaseScheduler._get_periodic_task_name_from_message(raw_message) is None


def test_get_periodic_task_name_from_invalid_message_returns_none():
    assert CustomDatabaseScheduler._get_periodic_task_name_from_message(b"not-json") is None


def test_is_periodic_task_already_in_queue_returns_false_when_entry_name_is_missing(make_scheduler):
    channel = FakeRedisChannel(messages_by_queue={CELERY_QUEUE_PERIODIC: []})
    scheduler = make_scheduler(channel=channel)
    entry = SimpleNamespace(
        name="",
        task="hope.apps.grievance.celery_tasks.periodic_grievances_notifications_async_task",
        options={"queue": CELERY_QUEUE_PERIODIC},
    )

    assert scheduler._is_periodic_task_already_in_queue(entry) is False
    channel.client.lrange.assert_not_called()


def test_is_periodic_task_already_in_queue_closes_channel(make_scheduler):
    channel = FakeRedisChannel(messages_by_queue={CELERY_QUEUE_PERIODIC: []})
    channel.close = MagicMock()
    scheduler = make_scheduler(channel=channel)
    entry = SimpleNamespace(
        name="periodic_grievances_notifications_async_task",
        task="hope.apps.grievance.celery_tasks.periodic_grievances_notifications_async_task",
        options={"queue": CELERY_QUEUE_PERIODIC},
    )

    assert scheduler._is_periodic_task_already_in_queue(entry) is False
    channel.close.assert_called_once_with()


def test_apply_async_skips_publish_when_same_task_is_already_queued(make_scheduler):
    task_name = "hope.apps.payment.celery_tasks.remove_old_cash_plan_payment_verification_xlsx_async_task"
    periodic_task_name = "remove_old_cash_plan_payment_verification_xlsx_async_task"
    queued_message = redis_dumps(
        [
            {"task": task_name, "periodic_task_name": periodic_task_name},
            {"correlation_id": "queued"},
            [[], {}, {}],
            None,
        ]
    )
    channel = FakeRedisChannel(messages_by_queue={CELERY_QUEUE_PERIODIC: [queued_message]})
    scheduler = make_scheduler(channel=channel)
    entry = SimpleNamespace(
        name=periodic_task_name,
        task=task_name,
        options={"queue": CELERY_QUEUE_PERIODIC},
    )

    with patch("hope.models.custom_model_entry.DatabaseScheduler.apply_async", autospec=True) as mock_apply_async:
        result = scheduler.apply_async(entry)

    assert result is None
    mock_apply_async.assert_not_called()
    channel.client.lrange.assert_called_once_with(
        CELERY_QUEUE_PERIODIC,
        0,
        scheduler.queued_task_scan_limit - 1,
    )
    assert channel.closed is True


def test_apply_async_delegates_when_task_is_not_queued(make_scheduler):
    task_name = "hope.apps.payment.celery_tasks.remove_old_cash_plan_payment_verification_xlsx_async_task"
    periodic_task_name = "remove_old_cash_plan_payment_verification_xlsx_async_task"
    other_message = redis_dumps(
        [
            {
                "task": task_name,
                "periodic_task_name": "different_periodic_task_name",
            },
            {"correlation_id": "queued"},
            [[], {}, {}],
            None,
        ]
    )
    channel = FakeRedisChannel(messages_by_queue={CELERY_QUEUE_PERIODIC: [other_message]})
    scheduler = make_scheduler(channel=channel)
    entry = SimpleNamespace(
        name=periodic_task_name,
        task=task_name,
        options={"queue": CELERY_QUEUE_PERIODIC},
    )

    with patch(
        "hope.models.custom_model_entry.DatabaseScheduler.apply_async",
        autospec=True,
        return_value="queued",
    ) as mock_apply_async:
        result = scheduler.apply_async(
            entry,
            producer="producer",
            advance=False,
            routing_key="rk",
        )

    assert result == "queued"
    mock_apply_async.assert_called_once_with(
        scheduler,
        entry,
        producer="producer",
        advance=False,
        routing_key="rk",
    )
    assert channel.closed is True


def test_apply_async_allows_same_task_with_different_periodic_task_name(make_scheduler):
    task_name = "hope.contrib.aurora.celery_tasks.automate_rdi_creation_task"
    queued_message = redis_dumps(
        [
            {
                "task": task_name,
                "periodic_task_name": "Nigeria Support Team",
            },
            {"correlation_id": "queued"},
            [[], {}, {}],
            None,
        ]
    )
    channel = FakeRedisChannel(messages_by_queue={CELERY_QUEUE_PERIODIC: [queued_message]})
    scheduler = make_scheduler(channel=channel)
    entry = SimpleNamespace(
        name="Nigeria March 2026 FLW",
        task=task_name,
        options={"queue": CELERY_QUEUE_PERIODIC},
    )

    with patch(
        "hope.models.custom_model_entry.DatabaseScheduler.apply_async",
        autospec=True,
        return_value="queued",
    ) as mock_apply_async:
        result = scheduler.apply_async(entry)

    assert result == "queued"
    mock_apply_async.assert_called_once_with(scheduler, entry, producer=None, advance=True)


def test_apply_async_skips_queue_scan_for_non_periodic_queue(make_scheduler):
    channel = FakeRedisChannel(messages_by_queue={"default": []})
    scheduler = make_scheduler(channel=channel, default_queue="default")
    entry = SimpleNamespace(
        name="periodic_grievances_notifications_async_task",
        task="hope.apps.grievance.celery_tasks.periodic_grievances_notifications_async_task",
        options={"queue": "default"},
    )

    with patch(
        "hope.models.custom_model_entry.DatabaseScheduler.apply_async",
        autospec=True,
        return_value="queued",
    ) as mock_apply_async:
        result = scheduler.apply_async(entry)

    assert result == "queued"
    mock_apply_async.assert_called_once_with(scheduler, entry, producer=None, advance=True)
    channel.client.lrange.assert_not_called()


def test_apply_async_skips_queue_scan_for_non_redis_transport(make_scheduler):
    channel = FakeRedisChannel(messages_by_queue={CELERY_QUEUE_PERIODIC: []})
    scheduler = make_scheduler(channel=channel, driver_type="memory")
    entry = SimpleNamespace(
        name="periodic_grievances_notifications_async_task",
        task="hope.apps.grievance.celery_tasks.periodic_grievances_notifications_async_task",
        options={"queue": CELERY_QUEUE_PERIODIC},
    )

    with patch(
        "hope.models.custom_model_entry.DatabaseScheduler.apply_async",
        autospec=True,
        return_value="queued",
    ) as mock_apply_async:
        result = scheduler.apply_async(entry)

    assert result == "queued"
    mock_apply_async.assert_called_once_with(scheduler, entry, producer=None, advance=True)
    channel.client.lrange.assert_not_called()
