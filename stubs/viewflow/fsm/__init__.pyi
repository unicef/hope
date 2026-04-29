from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

class State:
    def __init__(self, enum_type: Any = ..., default: Any = ..., **kwargs: Any) -> None: ...
    def setter(self) -> Callable[[F], F]: ...
    def getter(self) -> Callable[[F], F]: ...
    def transition(
        self,
        source: Any = ...,
        target: Any = ...,
        label: str | None = ...,
        conditions: list[Any] | None = ...,
        permission: Any = ...,
        custom: dict[str, Any] | None = ...,
    ) -> Callable[[F], F]: ...
    def __get__(self, obj: Any, objtype: Any = ...) -> Any: ...
