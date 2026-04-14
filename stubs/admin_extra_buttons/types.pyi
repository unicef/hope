from typing import Any, Callable, Protocol

from django.db.models import Model
from django.http import HttpRequest, HttpResponseBase
from django.template import RequestContext

from .buttons import ButtonWidget, ChoiceButton, LinkButton
from .handlers import BaseExtraHandler, ButtonHandler, ChoiceHandler, LinkHandler
from .mixins import ExtraButtonsMixin

type VisibleButton = ButtonWidget | LinkButton | ChoiceButton

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
type ButtonHandlerFunction = Callable[..., HttpResponseBase | None]
type ViewHandlerFunction = Callable[..., HttpResponseBase | None]

type ChoiceHandlerFunction = Callable[[ExtraButtonsMixin, VisibleButton], HttpResponseBase | None]
type LinkHandlerFunction = Callable[[ExtraButtonsMixin, VisibleButton], HttpResponseBase | None]

type GenericHandler = ButtonHandlerFunction | ViewHandlerFunction | ChoiceHandlerFunction | LinkHandlerFunction

type HandlerWithButton = ButtonHandler | LinkHandler | ChoiceHandler
