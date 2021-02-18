import graphene
from django.core.exceptions import ValidationError

from hct_mis_api.apps.utils.schema import Arg


class ValidationErrorMutationMixin(graphene.ObjectType):
    validation_errors = graphene.Field(Arg)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            return cls.processed_mutate(root, info, **kwargs)
        except ValidationError as e:
            if hasattr(e,"error_dict"):
                return cls(validation_errors=e.message_dict)
            else:
                raise
