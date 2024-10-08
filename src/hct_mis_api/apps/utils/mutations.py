import logging
from typing import Any

from django.core.exceptions import ValidationError

import graphene

from hct_mis_api.apps.utils.schema import Arg

logger = logging.getLogger(__name__)


class ValidationErrorMutationMixin(graphene.ObjectType):
    validation_errors = graphene.Field(Arg)

    @classmethod
    def mutate(cls, root: Any, info: Any, **kwargs: Any) -> "ValidationErrorMutationMixin":
        try:
            return cls.processed_mutate(root, info, **kwargs)
        except ValidationError as e:
            logger.warning(e)
            if hasattr(e, "error_dict"):
                return cls(validation_errors=e.message_dict)
            else:
                raise
