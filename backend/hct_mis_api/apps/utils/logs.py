import logging
from functools import wraps


def log_start_and_end(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"--- Starting: {func.__name__}")
        result = func(*args, **kwargs)
        logging.info(f"--- Ending: {func.__name__}")
        return result

    return wrapper
