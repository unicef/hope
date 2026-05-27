from typing import Any, Callable, TypeVar

_F = TypeVar("_F", bound=Callable[..., Any])

def post_generation[F: Callable[..., Any]](func: _F) -> _F: ...
def lazy_attribute[F: Callable[..., Any]](func: _F) -> _F: ...
def LazyFunction(func: Callable[..., Any]) -> Any: ...  # noqa: N802
def LazyAttribute(func: Callable[..., Any]) -> Any: ...  # noqa: N802
def Faker(provider: str, **kwargs: Any) -> Any: ...  # noqa: N802
def Sequence(func: Callable[..., Any]) -> Any: ...  # noqa: N802
def SubFactory(factory: Any, **kwargs: Any) -> Any: ...  # noqa: N802
