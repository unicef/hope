from typing import Any

from django.db.models import QuerySet
from rest_framework import serializers


class ScopedRelatedFieldMixin:
    """Narrows the queryset to the scope of the url path, so an id from outside of it fails like a nonexistent one.

    The field relies on two things: the view has to put the scope object in the serializer context
    under the `scope` key (`BusinessAreaMixin`/`ProgramMixin` do), and `scope_path` has to be a valid
    ORM path from the queryset model to that object (defaults to the `scope` name itself).
    """

    def __init__(self, *args: Any, scope: str = "business_area", scope_path: str | None = None, **kwargs: Any) -> None:
        self.scope = scope
        self.scope_path = scope_path or scope
        super().__init__(*args, **kwargs)

    def get_queryset(self) -> QuerySet:
        if self.scope not in self.context:
            raise KeyError(
                f"'{self.scope}' is missing from the serializer context;"
                f" the view has to provide it for {type(self).__name__}"
            )
        return super().get_queryset().filter(**{self.scope_path: self.context[self.scope]})


class ScopedRelatedField(ScopedRelatedFieldMixin, serializers.PrimaryKeyRelatedField):
    pass


class ScopedSlugRelatedField(ScopedRelatedFieldMixin, serializers.SlugRelatedField):
    pass
