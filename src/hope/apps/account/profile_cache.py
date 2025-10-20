from __future__ import annotations

from typing import Iterable

from django.core.cache import cache
from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.bits import KeyBitBase
from rest_framework_extensions.key_constructor.constructors import KeyConstructor

_NS = "v2"  # if we change something, bump the version


class ProfileVersioner:
    def _global_key(self) -> str:
        return f"profile:global:{_NS}"

    def _user_key(self, user_id: int) -> str:
        return f"profile:user:{_NS}:{user_id}"

    def _get_or_init(self, key: str, default: int = 1) -> int:
        return cache.get_or_set(key, default, timeout=None)

    def get_versions(self, user_id: int) -> tuple[int, int]:
        g = self._get_or_init(self._global_key())
        u = self._get_or_init(self._user_key(user_id))
        return g, u

    def bump_global(self) -> None:
        self._get_or_init(self._global_key())
        cache.incr(self._global_key())

    def bump_user(self, user_id: int) -> None:
        key = self._user_key(user_id)
        self._get_or_init(key)
        cache.incr(key)

    def bump_users(self, user_ids: Iterable[int]) -> None:
        for uid in set(filter(None, user_ids)):
            self.bump_user(uid)

    def etag_for(self, user_id: int) -> str:
        g, u = self.get_versions(user_id)
        return f'W/"profile:{user_id}:{g}.{u}"'

    def cache_key_for(self, user_id: int) -> str:
        g, u = self.get_versions(user_id)
        return f"profile:{user_id}:{g}.{u}"


profile_cache = ProfileVersioner()


class ProfileEtagKey:
    def __call__(self, view_instance, view_method, request, args, kwargs) -> str:
        return profile_cache.etag_for(request.user.id)


class ProfileVersionsKeyBit(KeyBitBase):
    def get_data(self, params, view_instance, view_method, request, args, kwargs):
        return profile_cache.cache_key_for(request.user.id)


class ProfileKeyConstructor(KeyConstructor):
    profile_version = ProfileVersionsKeyBit()
    unique_method_id = bits.UniqueMethodIdKeyBit()
    params = bits.KwargsKeyBit()
