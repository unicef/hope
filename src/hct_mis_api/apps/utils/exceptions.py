import logging
from typing import Callable

from graphql import GraphQLError

logger = logging.getLogger(__name__)


def log_and_raise(txt: str, error: Exception | None = None, error_type: Callable = GraphQLError) -> None:
    # TODO: need to be refactor to just raise exception
    logger.error(txt)
    if error is not None:
        raise error_type(txt) from error
    raise error_type(txt)
