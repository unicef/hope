from collections.abc import Iterator
from contextlib import contextmanager

from django.core.cache import cache

LOCK_PREFIX = "celery_lock_"
LOCK_EXPIRE = 5 * 60
# a lock left by a dead worker expires after LOCK_EXPIRE; expiry does not wake waiters, so wait a bit longer
LOCK_WAIT = LOCK_EXPIRE + 60


class NonRetriableTaskError(Exception):
    pass


class AlreadyRunningError(NonRetriableTaskError):
    pass


def lock_key(task: str, *parts: object) -> str:
    return ":".join([f"{LOCK_PREFIX}{task}", *map(str, parts)])


@contextmanager
def celery_lock(task: str, *parts: object) -> Iterator[None]:
    key = lock_key(task, *parts)
    lock = cache.lock(key, expire=LOCK_EXPIRE, auto_renewal=True)
    if not lock.acquire(timeout=LOCK_WAIT):
        raise AlreadyRunningError(f"Lock {key} is held by another task")
    try:
        yield
    finally:
        lock.release()
