from django import template
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag()
def get_related(context, field):
    info = {
        "to": field.model._meta.model_name,
        "field_name": field.name,
    }

    if field.related_name:
        related_attr = getattr(context, field.related_name)
    else:
        related_attr = getattr(context, f"{field.name}_set")

    if hasattr(related_attr, "all") and callable(related_attr.all):
        related = related_attr.all()
        opts = related_attr.model._meta
        info["related_name"] = opts.verbose_name
    else:
        opts = related_attr._meta
        related = [related_attr]
        info["related_name"] = opts.verbose_name
    info["data"] = related

    return info


@register.filter()
def get_admin_link(record):
    opts = record._meta
    url_name = admin_urlname(opts, "change")
    return reverse(url_name, args=[record.pk])
