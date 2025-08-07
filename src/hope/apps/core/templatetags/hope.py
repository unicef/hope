from typing import Any

from django import template
from django.template.defaultfilters import yesno
from django.templatetags.static import static

register = template.Library()


@register.filter()
def bool_to_icon(value: Any) -> str:
    name = yesno(value)
    return static(f"admin/img/icon-{name}.svg")
