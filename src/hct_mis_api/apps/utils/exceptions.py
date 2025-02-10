import logging
from typing import Callable, Optional

from graphql import GraphQLError

logger = logging.getLogger(__name__)


def log_and_raise(txt: str, error: Optional[Exception] = None, error_type: Callable = GraphQLError) -> None:
    # TODO: need to be refactor to just raise exception
    logger.warning(txt)
    if error is not None:
        raise error_type(txt) from error
    else:
        raise error_type(txt)
