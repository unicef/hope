import re
import time
from typing import Any, Optional

from django.core.cache.backends.locmem import LocMemCache as DjangoLocMemCache


class SimpleCacheLock:
    def __init__(self, cache: Any, key: str, blocking_timeout: float, timeout: Optional[float]) -> None:
        self.cache = cache
        self.key = key
        self.blocking_timeout = blocking_timeout
        self.timeout = timeout

    def __enter__(self) -> "SimpleCacheLock":
        start = time.time()
        while True:
            if self.cache.add(self.key, "LOCKED", self.timeout):
                return self
            if time.time() - start > self.blocking_timeout:
                raise TimeoutError(f"Could not acquire lock {self.key}")
            time.sleep(0.1)

    def __exit__(self, exc_type: Optional[type], exc: Optional[BaseException], tb: Optional[Any]) -> None:
        self.cache.delete(self.key)

    def acquire(self, blocking: bool) -> bool:
        return self.cache.add(self.key, "LOCKED", self.timeout)

    def release(self) -> None:
        self.cache.delete(self.key)


class LocMemCache(DjangoLocMemCache):
    def delete_pattern(self, pattern: str) -> None:
        regex_pattern = re.escape(pattern).replace("\\*", "(.*)")
        key_pattern = self.make_key(regex_pattern)
        for key in self._cache.keys():
            if re.match(key_pattern, key):
                self.delete(key)

    def lock(self, key: str, blocking_timeout: float = 0, timeout: Optional[float] = None) -> SimpleCacheLock:
        return SimpleCacheLock(self, key, blocking_timeout, timeout)
