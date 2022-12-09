import logging

from graphql import GraphQLError

logger = logging.getLogger(__name__)


def log_and_raise(txt, error=None, error_type=GraphQLError) -> None:
    logger.error(txt)
    if error is not None:
        raise error_type(txt) from error
    else:
        raise error_type(txt)
