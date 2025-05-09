import re

from django.core.cache.backends.locmem import LocMemCache as DjangoLocMemCache


class LocMemCache(DjangoLocMemCache):
    def delete_pattern(self, pattern: str) -> None:
        regex_pattern = re.escape(pattern).replace("\\*", "(.*)")
        key_pattern = self.make_key(regex_pattern)
        for key in self._cache:
            if re.match(key_pattern, key):
                self.delete(key)
