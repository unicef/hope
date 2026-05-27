from typing import TypeVar

from django.contrib.admin import ModelAdmin
from django.db.models import Model

_T = TypeVar("_T", bound=Model)

class AdminFiltersMixin(ModelAdmin[_T]): ...
