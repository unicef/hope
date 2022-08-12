import json

from django import template
from django.utils.safestring import mark_safe

from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter

register = template.Library()


@register.filter
def pretty_json(json_object):
    json_str = json.dumps(json_object, indent=4, sort_keys=True)
    lex = lexers.get_lexer_by_name("json")
    return mark_safe(highlight(json_str, lex, HtmlFormatter()))


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def pygmentize(code):
    formatter = HtmlFormatter(linenos=True)
    lex = lexers.get_lexer_by_name("python")
    formatted_code = highlight(code, lex, formatter)
    return mark_safe(formatted_code)


@register.filter(name="split")
def split(value):
    return value.split("\n")
