from typing import TypeVar

from django.db import models
from django.db.models import QuerySet

ModelT = TypeVar("ModelT", bound=models.Model)

class SoftDeletableQuerySetMixin[ModelT: models.Model]:
    def delete(self) -> tuple[int, dict[str, int]]: ...

class SoftDeletableQuerySet(SoftDeletableQuerySetMixin[ModelT], QuerySet[ModelT, ModelT]): ...

class SoftDeletableManagerMixin[ModelT: models.Model]:
    _queryset_class: type[SoftDeletableQuerySet[ModelT]]
    def __init__(self, *args: object, _emit_deprecation_warnings: bool = ..., **kwargs: object) -> None: ...
    def get_queryset(self) -> QuerySet[ModelT, ModelT]: ...

class SoftDeletableManager(SoftDeletableManagerMixin[ModelT], models.Manager[ModelT]): ...
