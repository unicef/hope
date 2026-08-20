from typing import Any

from django.db.models import QuerySet
from rest_framework import serializers


class ScopedRelatedFieldMixin:
    """Narrows the queryset to the scope of the url path, which the view has to put in the context."""

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
