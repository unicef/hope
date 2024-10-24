from typing import TYPE_CHECKING, Any, Dict

from django import template
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.urls import reverse

from hct_mis_api.apps.utils.security import is_root

register = template.Library()


if TYPE_CHECKING:
    from django.http import HttpRequest

    from hct_mis_api.apps.account.models import User


@register.simple_tag()
def get_related(user: "User", field: Any) -> Dict[str, Any]:
    related = []
    info = {
        "to": field.model._meta.model_name,
        "field_name": field.name,
        # 'related_name': field.related_name,
        # 'related_query_name': field.related_query_name,
    }

    if field.related_name:
        related = getattr(user, field.related_name).all()
    else:
        related = getattr(user, f"{field.name}_set").all()
    info["related_name"] = related.model._meta.verbose_name
    info["data"] = related

    return info


@register.filter()
def get_admin_link(record: Any) -> str:
    opts = record._meta
    url_name = admin_urlname(opts, "change")  # type: ignore # str vs SafeString
    return reverse(url_name, args=[record.pk])


@register.filter(name="is_root")
def _is_root(request: "HttpRequest") -> bool:
    return is_root(request)
