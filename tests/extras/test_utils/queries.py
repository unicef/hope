"""Pytest decorator that asserts a Django test executes an exact number of DB queries.

Import path (this file is under ``tests/extras/test_utils/`` which is placed
on ``sys.path`` by ``tests/unit/conftest.py``)::

    from extras.test_utils.queries import assert_db_queries_num

See ``assert_num_queries_exact_decorator.md`` at the repo root for the full spec,
rationale, and usage guidance (how to choose N, multi-DB tests, parametrize, etc.).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
import contextlib
import functools
import inspect
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
    """Assert that the decorated test executes exactly ``n`` DB queries.

    When ``using`` lists multiple aliases, ``n`` is the **sum** across all of them.
    ``using`` must always be a list/tuple of alias names — passing a bare string
    raises ``TypeError`` at decoration time to prevent the silent
    ``"default"`` → ``("d","e","f","a","u","l","t")`` foot-gun.
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("assert_db_queries_num: `n` must be an int")
    if isinstance(using, str):
        raise TypeError(
            "assert_db_queries_num: `using` must be a list/tuple of aliases, "
            f"not a bare string. Did you mean using=[{using!r}]?"
        )
    aliases = tuple(using)
    if not aliases:
        raise TypeError("assert_db_queries_num: `using` must list at least one alias")

    def decorator(func: F) -> F:
        if inspect.iscoroutinefunction(func):
            raise NotImplementedError("@assert_db_queries_num does not yet support async tests")

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

        return wrapper  # type: ignore[return-value]

    return decorator


def _format_message(
    expected: int,
    actual: int,
    queries_by_alias: dict[str, list[dict]],
    func: Callable[..., object],
) -> str:
    delta = actual - expected
    sign = "+" if delta > 0 else ""
    return (
        f"{func.__module__}::{func.__qualname__}: "
        f"expected {expected} queries, got {actual} ({sign}{delta}). "
        f"If this change is intentional, update the decorator value."
    )
