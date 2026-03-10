from functools import wraps
import logging
from typing import Callable, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def log_start_and_end(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.info(f"--- Starting: {func.__name__}")
        result = func(*args, **kwargs)
        logger.info(f"--- Ending: {func.__name__}")
        return result

    return wrapper
