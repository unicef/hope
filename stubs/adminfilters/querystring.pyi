from typing import Any

from django.contrib.admin import ListFilter
from django.db import models
from django.http import HttpRequest

class QueryStringFilter(ListFilter):
    def __init__(
        self,
        request: HttpRequest | None,
        params: dict[str, Any],
        model: type[models.Model] | Any,
        model_admin: Any | None,
    ) -> None: ...
    def get_filters(self, value: str) -> tuple[dict[str, Any], dict[str, Any]]: ...
