from typing import Any, Callable, TypeVar
from uuid import UUID

from django.contrib.admin import ModelAdmin
from django.db.models import Model
from django.http import HttpRequest, HttpResponse, HttpResponseBase

_T = TypeVar("_T", bound=Model)

class ExtraButtonsMixin(ModelAdmin[_T]):
    change_list_template: str | None
    change_form_template: str | None

    def get_common_context(
        self, request: HttpRequest, pk: str | int | UUID | None = ..., **kwargs: Any
    ) -> dict[str, Any]: ...

def confirm_action(
    modeladmin: Any,
    request: HttpRequest,
    action: Callable[..., HttpResponseBase | None],
    *,
    message: str,
    success_message: str = ...,
    description: str = ...,
    pk: str | int | UUID | None = ...,
    extra_context: dict[str, Any] | None = ...,
    title: str | None = ...,
    template: str = ...,
    error_message: str | None = ...,
    raise_exception: bool = ...,
) -> HttpResponse: ...
