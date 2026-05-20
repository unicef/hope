from typing import Any, Callable

def LazyFunction(func: Callable[..., Any]) -> Any: ...  # noqa: N802
def LazyAttribute(func: Callable[..., Any]) -> Any: ...  # noqa: N802
def Faker(provider: str, **kwargs: Any) -> Any: ...  # noqa: N802
