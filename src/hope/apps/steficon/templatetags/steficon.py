import json

from django import template
from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter

register = template.Library()


@register.filter
def pretty_json(json_object: dict) -> str:
    json_str = json.dumps(json_object, indent=4, sort_keys=True)
    lex = lexers.get_lexer_by_name("json")
    return highlight(json_str, lex, HtmlFormatter())


@register.filter
def get_item(dictionary: dict, key: object) -> object:
    return dictionary.get(key)


@register.filter
def pygmentize(code: object) -> str:
    formatter = HtmlFormatter(linenos=True)
    lex = lexers.get_lexer_by_name("python")
    return highlight(code, lex, formatter)


@register.filter(name="split")
def split(value: str) -> list[str]:
    return value.split("\n")
