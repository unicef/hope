from typing import Any, TypeVar

from django.db import models
from django.db.models import QuerySet

_T = TypeVar("_T", bound=models.Model)

class NaturalKeyQuerySet(QuerySet[_T, _T]): ...

class NaturalKeyModelManager(models.Manager[_T]):
    def get_by_natural_key(self, *args: Any) -> _T: ...
    def create_by_natural_key(self, *args: Any) -> _T: ...
    def get_or_create_by_natural_key(self, *args: Any) -> tuple[_T, bool]: ...

class NaturalKeyModel(models.Model):
    objects: models.Manager[Any]

    @classmethod
    def get_natural_key_info(cls) -> Any: ...
    def natural_key(self) -> tuple[Any, ...]: ...

    class Meta:
        abstract: bool
