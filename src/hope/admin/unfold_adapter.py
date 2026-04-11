"""Bridge between ``admin_extra_buttons`` and ``django-unfold`` actions.

``admin_extra_buttons`` exposes ``@button`` / ``@link`` / ``@choice`` / ``@view``
decorators that register handlers in ``self.extra_button_handlers`` and render
into ``{% block object-tools-items %}`` via its own template. Unfold's
changelist template moved that block inside ``{% block nav-global-side %}``
and renders it through its ``change_list_object_tools`` tag, which only
reads names listed in ``actions_list`` / ``actions_detail``. The mixin in
this module exposes pure ``ButtonHandler`` instances through the Unfold
``actions_*`` API while leaving URL registration to ``admin_extra_buttons``.
"""

from functools import wraps
from typing import Any

from admin_extra_buttons.handlers import ButtonHandler
from admin_extra_buttons.utils import labelize
from django.http import HttpRequest
from unfold.enums import ActionVariant


def _wrap_aeb_handler_for_unfold(model_admin: Any, name: str, handler: ButtonHandler) -> Any:
    @wraps(handler.func)
    def _view(request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if handler.single_object_invocation:
            return handler(model_admin, request)
        object_id = kwargs.get("object_id")
        if object_id is None and args:
            object_id = args[0]
        pk_kwarg = handler.func_args[2]
        return handler(model_admin, request, **{pk_kwarg: object_id})

    _view.short_description = handler.config.get("label") or labelize(name)
    _view.attrs = {}
    _view.icon = None
    _view.variant = ActionVariant.DEFAULT
    _view.url_path = name
    _view.original_function_name = name

    # Permission checks (string or callable) stay with admin_extra_buttons:
    # BaseExtraHandler.__call__ invokes check_permission before dispatch.
    # Exposing allowed_permissions to Unfold would trigger admin.E129 when
    # the string perm isn't registered as a Django Permission row.
    return _view


class ExtraButtonsUnfoldAdapterMixin:
    """Exposes ``@button`` handlers through Unfold's ``actions_*`` slots.

    URL registration stays with ``admin_extra_buttons`` but we strip the
    duplicate ``ButtonHandler`` URLs from its output so Unfold owns the
    canonical ``admin:<app>_<model>_<name>`` path. ``LinkHandler``,
    ``ChoiceHandler`` and ``@view`` URLs are preserved.
    """

    excluded_buttons: set[str] = set()

    def _aeb_button_handlers(self) -> dict[str, ButtonHandler]:
        handlers = getattr(self, "extra_button_handlers", None) or {}
        if not handlers and hasattr(self, "get_extra_urls"):
            super().get_extra_urls()  # type: ignore[misc]
            handlers = self.extra_button_handlers  # type: ignore[attr-defined]
        excluded = self.excluded_buttons
        return {n: h for n, h in handlers.items() if isinstance(h, ButtonHandler) and n not in excluded}

    @property
    def actions_list(self) -> list[str]:
        return [
            name
            for name, h in self._aeb_button_handlers().items()
            if h.change_list in (True, None) and h.single_object_invocation
        ]

    @property
    def actions_detail(self) -> list[str]:
        return [
            name
            for name, h in self._aeb_button_handlers().items()
            if h.change_form in (True, None) and not h.single_object_invocation
        ]

    def _get_instance_method(self, method_name: str) -> Any:
        handlers = self._aeb_button_handlers()
        if method_name in handlers:
            return _wrap_aeb_handler_for_unfold(self, method_name, handlers[method_name])
        return super()._get_instance_method(method_name)  # type: ignore[misc]

    def get_extra_urls(self) -> list[Any]:
        urls = super().get_extra_urls()  # type: ignore[misc]
        opts = self.model._meta  # type: ignore[attr-defined]
        button_names = {
            f"{opts.app_label}_{opts.model_name}_{name}"
            for name, h in self.extra_button_handlers.items()  # type: ignore[attr-defined]
            if isinstance(h, ButtonHandler)
        }
        return [u for u in urls if getattr(u, "name", None) not in button_names]
