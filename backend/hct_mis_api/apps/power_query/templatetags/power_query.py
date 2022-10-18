import json

from django import template

from adminactions.utils import get_attr

from hct_mis_api.apps.power_query.utils import get_sentry_url

register = template.Library()


@register.filter()
def field(obj, field_name):
    return get_attr(obj, field_name)


@register.filter()
def link_to_sentry(event_id, href=False):
    return get_sentry_url(event_id, href)


@register.filter(name="classname")
def get_class(value):
    return value.__class__.__name__


@register.filter()
def dataset_to_json(value):
    # TODO: json.dump needs a second argument (fp)
    return json.dump(value)  # type: ignore
