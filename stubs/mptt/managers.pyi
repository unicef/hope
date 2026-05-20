from typing import TypeVar

from django.db import models
from django.db.models import QuerySet

_T = TypeVar("_T", bound=models.Model)

class TreeQuerySet(QuerySet[_T, _T]): ...

class TreeManager(models.Manager[_T]):
    tree_id_attr: str
    left_attr: str
    right_attr: str
    level_attr: str
    tree_model: type[models.Model] | None
