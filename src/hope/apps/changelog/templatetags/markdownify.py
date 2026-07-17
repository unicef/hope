from django import template
from django.conf import settings
from django.utils.safestring import SafeString
import markdown
import nh3

register = template.Library()


@register.filter
def markdownify(value: str) -> str:
    allowed_tags = set(settings.MARKDOWNIFY["default"]["WHITELIST_TAGS"])
    html = markdown.markdown(value or "")
    return SafeString(nh3.clean(html, tags=allowed_tags))
