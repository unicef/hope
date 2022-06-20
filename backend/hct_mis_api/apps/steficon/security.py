import json
import logging

from .config import SAFETY_HIGH, SAFETY_NONE, SAFETY_STANDARD, config

logger = logging.getLogger(__name__)
#
# SAFETY_NONE = 0  # accept any value
# SAFETY_STANDARD = 1  # accept
# SAFETY_MINIMUM = 2  # only accept promitives
# SAFETY_HIGH = 3  # only accept json values


def clean_context(context):
    try:
        if config.SAFETY_LEVEL == SAFETY_NONE:
            return context
        elif config.SAFETY_LEVEL == SAFETY_STANDARD:
            return context
        elif config.SAFETY_LEVEL == SAFETY_HIGH:
            return json.loads(json.dumps(context))
    except Exception as e:
        logger.exception(e)
