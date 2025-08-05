import json
import logging

from hct_mis_api.apps.steficon.config import (
    SAFETY_HIGH,
    SAFETY_NONE,
    SAFETY_STANDARD,
    config,
)

logger = logging.getLogger(__name__)


def clean_context(context: dict) -> dict | None:
    try:
        if config.SAFETY_LEVEL == SAFETY_NONE:
            return context
        if config.SAFETY_LEVEL == SAFETY_STANDARD:
            return context
        if config.SAFETY_LEVEL == SAFETY_HIGH:
            return json.loads(json.dumps(context))
    except Exception as e:
        logger.exception(e)
    return None
