from typing import Any

from django.db import models

from mptt.managers import TreeManager

class MPTTModel(models.Model):
    objects: TreeManager[Any]
    _tree_manager: TreeManager[Any]

    class Meta:
        abstract: bool
