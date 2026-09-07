from unittest.mock import MagicMock

from django.core.cache import cache
import pytest

from hope.apps.core.cache import RedisCache
from hope.apps.core.celery_lock import LOCK_PREFIX, AlreadyRunningError, celery_lock, lock_key
from hope.apps.core.memcache import LocMemLock


@pytest.fixture
def no_wait(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("hope.apps.core.celery_lock.LOCK_WAIT", 0)


@pytest.fixture
def held_lock() -> LocMemLock:
    lock = cache.lock(lock_key("task", 1))
    lock.acquire()
    return lock


@pytest.fixture
def redis_backend(monkeypatch: pytest.MonkeyPatch) -> tuple[RedisCache, MagicMock]:
    backend = RedisCache("redis://localhost:6379/1", {})
    client = MagicMock()
    client.scan_iter.return_value = [b"lock:celery_lock_b:1", b"lock:celery_lock_a:2"]
    monkeypatch.setattr(backend.client, "get_client", lambda *args, **kwargs: client)
    return backend, client


@pytest.mark.parametrize(
    ("parts", "expected"),
    [
        ((), "celery_lock_task"),
        ((1,), "celery_lock_task:1"),
        (("a", 2), "celery_lock_task:a:2"),
    ],
)
def test_lock_key_joins_task_and_parts(parts: tuple, expected: str) -> None:
    assert lock_key("task", *parts) == expected


def test_celery_lock_holds_lock_inside_and_releases_after() -> None:
    with celery_lock("task", 1):
        assert cache.celery_lock_keys() == ["celery_lock_task:1"]

    assert cache.celery_lock_keys() == []


def test_celery_lock_releases_on_exception() -> None:
    with pytest.raises(RuntimeError), celery_lock("task", 1):
        raise RuntimeError

    assert cache.celery_lock_keys() == []


def test_celery_lock_raises_non_retriable_when_held(no_wait: None, held_lock: LocMemLock) -> None:
    with pytest.raises(AlreadyRunningError, match="Lock celery_lock_task:1 is held by another task"):
        with celery_lock("task", 1):
            pass  # pragma: no cover

    assert held_lock.locked()


def test_locmem_lock_non_blocking_acquire_returns_false_when_held(held_lock: LocMemLock) -> None:
    assert cache.lock(lock_key("task", 1)).acquire(blocking=False) is False


def test_locmem_lock_blocking_acquire_gives_up_after_timeout(held_lock: LocMemLock) -> None:
    assert cache.lock(lock_key("task", 1)).acquire(timeout=0.05) is False


def test_locmem_lock_blocking_acquire_succeeds_once_released(held_lock: LocMemLock) -> None:
    held_lock.release()

    assert cache.lock(lock_key("task", 1)).acquire(timeout=0.05) is True


def test_locmem_lock_extend_refreshes_expiry(held_lock: LocMemLock) -> None:
    assert held_lock.extend(60) is True
    assert held_lock.locked()


def test_locmem_lock_extend_fails_when_not_held(held_lock: LocMemLock) -> None:
    held_lock.release()

    assert held_lock.extend() is False
    assert not held_lock.locked()


def test_locmem_celery_lock_keys_lists_only_celery_locks_sorted() -> None:
    cache.lock("other").acquire()
    cache.lock(lock_key("b", 1)).acquire()
    cache.lock(lock_key("a", 2)).acquire()

    assert cache.celery_lock_keys() == [f"{LOCK_PREFIX}a:2", f"{LOCK_PREFIX}b:1"]


def test_locmem_delete_celery_lock_removes_key(held_lock: LocMemLock) -> None:
    cache.delete_celery_lock(lock_key("task", 1))

    assert not held_lock.locked()


def test_redis_celery_lock_keys_scans_prefix_and_strips_lock_marker(
    redis_backend: tuple[RedisCache, MagicMock],
) -> None:
    backend, client = redis_backend

    assert backend.celery_lock_keys() == ["celery_lock_a:2", "celery_lock_b:1"]
    client.scan_iter.assert_called_once_with("lock:celery_lock_*")


def test_redis_delete_celery_lock_removes_lock_and_signal(redis_backend: tuple[RedisCache, MagicMock]) -> None:
    backend, client = redis_backend

    backend.delete_celery_lock("celery_lock_a:2")

    client.delete.assert_called_once_with("lock:celery_lock_a:2", "lock-signal:celery_lock_a:2")
