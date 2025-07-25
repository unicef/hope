import logging
from typing import Callable

from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


def log_and_raise(txt: str, error: Exception | None = None, error_type: Callable = ValidationError) -> None:
    logger.warning(txt)
    if error is not None:
        raise error_type(txt) from error
    raise error_type(txt)
