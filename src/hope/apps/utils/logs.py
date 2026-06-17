from functools import wraps
import logging
from typing import Any, Callable, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def log_start_and_end[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.info(f"--- Starting: {func.__name__}")
        result = func(*args, **kwargs)
        logger.info(f"--- Ending: {func.__name__}")
        return result

    return wrapper


def safe_log(value: Any) -> str:
    """Strip CR/LF to prevent log forging (CWE-117).

    ``LogForgingFilter`` covers all ``%s`` log args automatically; call this only
    when you need sanitization outside of the logging system (e.g. building strings
    that are later written to files or returned in responses).
    """
    return str(value).replace("\r", "").replace("\n", "")


class _SanitizedValue:
    """Wraps a log arg; ``str()`` / ``repr()`` strip CR/LF lazily at format time."""

    __slots__ = ("_value",)

    def __init__(self, value: Any) -> None:
        self._value = value

    def __str__(self) -> str:
        return safe_log(self._value)

    def __repr__(self) -> str:
        return safe_log(repr(self._value))


class LogForgingFilter(logging.Filter):
    """Defense-in-depth filter that strips CR/LF from interpolated log args.

    Sanitizes only ``record.args`` (the values passed via ``%s`` / ``%(name)s``).
    Leaves ``record.msg`` (hardcoded template), ``record.exc_text`` and
    ``record.exc_info`` (tracebacks) untouched so multi-line content there is
    preserved.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        args = record.args
        if not args:
            return True
        if isinstance(args, dict):
            record.args = {k: _SanitizedValue(v) for k, v in args.items()}
        elif isinstance(args, tuple):
            record.args = tuple(_SanitizedValue(a) for a in args)
        return True
