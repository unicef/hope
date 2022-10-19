import logging
from functools import wraps
from types import FunctionType
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def log_start_and_end(func: FunctionType) -> FunctionType:
    @wraps(func)
    def wrapper(*args: List, **kwargs: Dict) -> Any:
        logger.info(f"--- Starting: {func.__name__}")
        result = func(*args, **kwargs)
        logger.info(f"--- Ending: {func.__name__}")
        return result

    return wrapper
