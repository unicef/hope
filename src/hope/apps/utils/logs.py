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
    """Strip CR/LF to prevent log forging (CWE-117) when logging user-controlled values.

    Use at the call site whenever a log argument originates from outside the codebase
    (HTTP input, file contents, external API responses, model fields editable by users).
    Explicit calls are preferred over a global filter because they document intent at
    the point where the security review matters; ``LogForgingFilter`` below acts as a
    defense-in-depth safety net for anything missed.
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
    preserved. Call sites that want explicit intent should still use ``safe_log()``.
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
