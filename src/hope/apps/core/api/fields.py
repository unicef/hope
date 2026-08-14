from typing import Any

from django.db.models import QuerySet
from rest_framework import serializers


class ScopedRelatedFieldMixin:
    """Object ids in the request body are global, so the queryset is narrowed to the scope from the url path.

    An id outside the scope then fails the same way as an id that does not exist, and nothing about the
    object is revealed. The view has to put the scope in the serializer context, otherwise this raises.
    """

    def __init__(self, *args: Any, scope: str = "business_area", scope_path: str | None = None, **kwargs: Any) -> None:
        self.scope = scope
        self.scope_path = scope_path or scope
        super().__init__(*args, **kwargs)

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(**{self.scope_path: self.context[self.scope]})


class ScopedRelatedField(ScopedRelatedFieldMixin, serializers.PrimaryKeyRelatedField):
    pass


class ScopedSlugRelatedField(ScopedRelatedFieldMixin, serializers.SlugRelatedField):
    pass
