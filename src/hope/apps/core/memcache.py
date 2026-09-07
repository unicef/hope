import re
import time
from typing import Any

from django.core.cache.backends.locmem import LocMemCache as DjangoLocMemCache

from hope.apps.core.celery_lock import LOCK_PREFIX


class LocMemLock:
    def __init__(self, cache: Any, key: str, expire: float | None) -> None:
        self.cache = cache
        self.key = f"lock:{key}"
        self.expire = expire

    def acquire(self, blocking: bool = True, timeout: float | None = None) -> bool:
        deadline = time.monotonic() + (timeout or 0)
        while not self.cache.add(self.key, "LOCKED", self.expire):
            if not blocking or time.monotonic() >= deadline:
                return False
            time.sleep(0.01)
        return True

    def release(self) -> None:
        self.cache.delete(self.key)


class LocMemCache(DjangoLocMemCache):
    def delete_pattern(self, pattern: str) -> None:
        regex_pattern = re.escape(pattern).replace("\\*", "(.*)")
        key_pattern = self.make_key(regex_pattern)
        for key in self._cache:
            if re.match(key_pattern, key):
                self.delete(key)

    def expire(self, key: str, timeout: float | None = None) -> bool:
        """Set expiration time on an existing key."""
        return self.touch(key, timeout)

    def lock(self, key: str, expire: float | None = None, auto_renewal: bool = False) -> LocMemLock:
        return LocMemLock(self, key, expire)

    def celery_lock_keys(self) -> list[str]:
        prefix = self.make_key(f"lock:{LOCK_PREFIX}")
        return sorted(key.removeprefix(self.make_key("lock:")) for key in self._cache if key.startswith(prefix))

    def delete_celery_lock(self, key: str) -> None:
        self.delete(f"lock:{key}")
