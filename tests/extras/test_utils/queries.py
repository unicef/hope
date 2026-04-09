from __future__ import annotations

from collections.abc import Callable, Sequence
import contextlib
import functools
from typing import TypeVar

from django.db import DEFAULT_DB_ALIAS, connections
from django.test.utils import CaptureQueriesContext

__all__ = ["assert_db_queries_num"]

F = TypeVar("F", bound=Callable[..., object])


def assert_db_queries_num(
    n: int,
    *,
    using: Sequence[str] = (DEFAULT_DB_ALIAS,),
) -> Callable[[F], F]:
    aliases = tuple(using)

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            with contextlib.ExitStack() as stack:
                ctxs = {alias: stack.enter_context(CaptureQueriesContext(connections[alias])) for alias in aliases}
                result = func(*args, **kwargs)
            queries_by_alias = {alias: list(ctx.captured_queries) for alias, ctx in ctxs.items()}
            actual = sum(len(qs) for qs in queries_by_alias.values())
            if actual != n:
                raise AssertionError(_format_message(n, actual, queries_by_alias, func))
            return result

        return wrapper

    return decorator


def _format_message(
    expected: int,
    actual: int,
    func: Callable[..., object],
) -> str:
    delta = actual - expected
    sign = "+" if delta > 0 else ""
    return (
        f"{func.__module__}::{func.__qualname__}: "
        f"expected {expected} queries, got {actual} ({sign}{delta}). "
        f"If this change is intentional, update the decorator value."
    )
