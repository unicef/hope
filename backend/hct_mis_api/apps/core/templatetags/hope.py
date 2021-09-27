from django import template
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.template.defaultfilters import yesno
from django.templatetags.static import static
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def bool_to_icon(value):
    name = yesno(value)
    return static(f"admin/img/icon-{name}.svg")
