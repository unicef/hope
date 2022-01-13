import json

from django import template
from django.core import serializers
from django.db.models import Model
from django.utils.safestring import mark_safe

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

register = template.Library()

json_value_escapes = {
    ord(">"): "\\u003E",
    ord("<"): "\\u003C",
    ord("&"): "\\u0026",
    ord('"'): "\\u0022",
}


@register.filter
def pretty_json(value):
    response = json.dumps(value, sort_keys=True, indent=2)
    formatter = HtmlFormatter(style="colorful")
    response = highlight(response, JsonLexer(), formatter)
    return mark_safe(response)


@register.filter
def smart_json(value):
    if isinstance(value, Model):
        data = json.loads(serializers.serialize("json", [value]))
    else:
        data = value
    return pretty_json(data)


@register.filter(name="repr")
def _repr(value):
    return repr(value)


#
# @register.filter
# def json_value(value):
#     from django.core.serializers.json import DjangoJSONEncoder
#
#     json_str = json.dumps(value, cls=DjangoJSONEncoder).translate(json_value_escapes)
#     return mark_safe(json_str)
