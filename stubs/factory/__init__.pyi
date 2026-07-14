from typing import Any, Callable

class FactoryMetaClass(type):
    def __call__(cls, **kwargs: Any) -> Any: ...

def LazyFunction(func: Callable[..., Any]) -> Any: ...  # noqa: N802
def LazyAttribute(func: Callable[..., Any]) -> Any: ...  # noqa: N802
def Faker(provider: str, **kwargs: Any) -> Any: ...  # noqa: N802
