from redis_lock.django_cache import RedisCache as RedisLockCache

from hope.apps.core.celery_lock import LOCK_PREFIX


class RedisCache(RedisLockCache):
    def celery_lock_keys(self) -> list[str]:
        client = self.client.get_client()
        return sorted(key.decode().removeprefix("lock:") for key in client.scan_iter(f"lock:{LOCK_PREFIX}*"))

    def delete_celery_lock(self, key: str) -> None:
        self.client.get_client().delete(f"lock:{key}", f"lock-signal:{key}")
