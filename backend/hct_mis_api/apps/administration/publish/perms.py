from django.db.models import Model
from django.http import HttpRequest

from admin_extra_buttons.handlers import BaseExtraHandler

from hct_mis_api.apps.utils.security import is_root


def check_publish_permission(request: HttpRequest, obj: Model, handler: BaseExtraHandler, **kwargs) -> bool:
    if hasattr(handler.model_admin, "check_publish_permission"):
        return handler.model_admin.check_publish_permission(request, obj)
    return is_root(request.user)


def check_load_permission(request, obj, handler: BaseExtraHandler, **kwargs):
    if hasattr(handler.model_admin, "check_load_permission"):
        return handler.model_admin.check_load_permission(request, obj)
    return request.user.is_staff
