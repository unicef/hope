from django import template
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.urls import reverse

from hct_mis_api.apps.utils.security import is_root

register = template.Library()


@register.simple_tag()
def get_related(user, field):
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
def get_admin_link(record):
    opts = record._meta
    url_name = admin_urlname(opts, "change")
    return reverse(url_name, args=[record.pk])


@register.filter(name="is_root")
def _is_root(request):
    return is_root(request)
