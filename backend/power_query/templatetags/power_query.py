import json
from typing import Any

from django import template
from django.utils.safestring import mark_safe

from adminactions.utils import get_attr

from power_query.utils import get_sentry_url, sizeof

register = template.Library()


@register.filter()
def field(obj: Any, field_name: str) -> str:
    return get_attr(obj, field_name)


@register.filter()
def link_to_sentry(event_id: Any, href: bool = False) -> str:
    return get_sentry_url(event_id, href)


@register.filter(name="classname")
def get_class(value: Any) -> Any:
    return value.__class__.__name__


@register.filter()
def dataset_to_json(value: Any) -> str:
    return json.dump(value)  # type: ignore # FIXME: json.dump needs a second argument (fp)


@register.filter()
def fmt_size(value: Any) -> str:
    return mark_safe(sizeof(value))
