import logging
from functools import wraps

logger = logging.getLogger(__name__)


def log_start_and_end(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"--- Starting: {func.__name__}")
        result = func(*args, **kwargs)
        logger.info(f"--- Ending: {func.__name__}")
        return result

    return wrapper
