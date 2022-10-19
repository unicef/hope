import logging

from graphql import GraphQLError

logger = logging.getLogger(__name__)


def log_and_raise(txt, error=None):
    logger.error(txt)
    if error is not None:
        raise GraphQLError(txt) from error
    else:
        raise GraphQLError(txt)
