from typing import Any, Callable, Protocol, TypeAlias

from django.db.models import Model
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.template import RequestContext

from .buttons import ButtonWidget, ChoiceButton, LinkButton
from .handlers import BaseExtraHandler, ButtonHandler, ChoiceHandler, LinkHandler
from .mixins import ExtraButtonsMixin

VisibleButton: TypeAlias = ButtonWidget | LinkButton | ChoiceButton

class PermissionHandler(Protocol):
    def __call__(
        self, request: HttpRequest, obj: Model | None = None, handler: BaseExtraHandler | None = None
    ) -> bool: ...

class WidgetProtocol(Protocol):
    button_class: ButtonWidget
    change_list: bool
    change_form: bool

    def get_button_params(self, context: RequestContext, **extra: Any) -> dict[str, Any]: ...
    def get_button(self, context: RequestContext) -> ButtonWidget: ...

class BaseHandlerFunction(Protocol):
    __name__: str
    extra_buttons_handler: BaseExtraHandler

# Widened to accept any pk type (UUID, str, int) and any HttpResponse subclass
ButtonHandlerFunction: TypeAlias = Callable[..., HttpResponseBase | None]
ViewHandlerFunction: TypeAlias = Callable[..., HttpResponseBase | None]

ChoiceHandlerFunction: TypeAlias = Callable[[ExtraButtonsMixin, VisibleButton], HttpResponseBase | None]
LinkHandlerFunction: TypeAlias = Callable[[ExtraButtonsMixin, VisibleButton], HttpResponseBase | None]

GenericHandler: TypeAlias = ButtonHandlerFunction | ViewHandlerFunction | ChoiceHandlerFunction | LinkHandlerFunction

HandlerWithButton: TypeAlias = ButtonHandler | LinkHandler | ChoiceHandler
