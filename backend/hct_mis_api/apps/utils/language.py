import functools
import weakref
from typing import Any, Callable, Dict, Hashable, Sequence


def weak_lru(maxsize: int = 128, typed: bool = False) -> Callable:
    'LRU Cache decorator that keeps a weak reference to "self"'

    def wrapper(func: Callable) -> Callable:
        @functools.lru_cache(maxsize, typed)
        def _func(_self: Any, *args: Sequence[Any], **kwargs: Dict[str, Any]) -> Any:
            return func(_self(), *args, **kwargs)

        @functools.wraps(func)
        def inner(self: Any, *args: Sequence[Any], **kwargs: Hashable) -> Any:
            return _func(weakref.ref(self), *args, **kwargs)

        return inner

    return wrapper
