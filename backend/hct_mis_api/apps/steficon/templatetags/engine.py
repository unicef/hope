import difflib
import json

from django import template
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer
from pygments.lexers.python import PythonLexer

register = template.Library()


@register.filter(name='getattr')
def get_attr(d, v):
    return getattr(d, v)


@register.simple_tag
def define(val=None):
    return val


@register.filter
def adults(hh):
    return hh.members.filter(age__gte=18, age__lte=65,
                             work__in=["fulltime", "seasonal", "parttime"]).count()


@register.filter
def pretty_json(json_object):
    json_str = json.dumps(json_object, indent=4, sort_keys=True)
    return mark_safe(highlight(json_str, JsonLexer(), HtmlFormatter()))


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def pygmentize(code, language):
    formatter = HtmlFormatter(style='colorful')
    formatted_code = highlight(code, PythonLexer(), formatter)
    return mark_safe(formatted_code)


@register.filter
def diff(state):
    left = state.previous_state['definition'].split('\n')
    right = state.new_state['definition'].split('\n')
    if state.version + 1 == state.rule.version:
        label = 'Current'
    else:
        label = state.version + 1

    return mark_safe(difflib.HtmlDiff().make_table(left, right,
                                                   f"Code before changes - Version: {state.version}",
                                                   f"Code after changes - {state.updated_by} - Version: {label}",
                                                   ))


@register.filter
def diff_to_current(state):
    left = state.new_state['definition'].split('\n')
    right = state.rule.definition.split('\n')
    return mark_safe(difflib.HtmlDiff().make_table(left, right,
                                                   f"Version: {state.version} code",
                                                   f"Current code: Version {state.rule.version}",
                                                   ))
