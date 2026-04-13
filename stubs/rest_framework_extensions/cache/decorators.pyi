from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

def cache_response(
    timeout: int | None = ...,
    key_func: Any = ...,
    cache: str | None = ...,
    cache_errors: bool | None = ...,
) -> Callable[[F], F]: ...
