import logging
from typing import Callable, Optional

from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


def log_and_raise(txt: str, error: Optional[Exception] = None, error_type: Callable = ValidationError) -> None:
    logger.warning(txt)
    if error is not None:
        raise error_type(txt) from error
    else:
        raise error_type(txt)
