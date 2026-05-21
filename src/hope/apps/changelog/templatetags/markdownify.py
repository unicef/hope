import markdown
import nh3
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_ALLOWED_TAGS = {
    "a", "abbr", "acronym", "b", "blockquote", "em",
    "i", "li", "ol", "p", "strong", "ul", "br",
}


@register.filter
def markdownify(value: str) -> str:
    html = markdown.markdown(value or "")
    return mark_safe(nh3.clean(html, tags=_ALLOWED_TAGS))
