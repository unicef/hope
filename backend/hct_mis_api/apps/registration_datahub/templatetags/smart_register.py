import base64
import io
import logging
import re
from typing import Any, Dict

from django.template import Library, Node

from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)
register = Library()


class EscapeScriptNode(Node):
    def __init__(self, nodelist) -> None:
        super(EscapeScriptNode, self).__init__()
        self.nodelist = nodelist

    def render(self, context) -> str:
        out = self.nodelist.render(context)
        escaped_out = out.replace("</script>", "<\\/script>")
        return escaped_out


@register.tag()
def escapescript(parser, token) -> EscapeScriptNode:
    nodelist = parser.parse(("endescapescript",))
    parser.delete_first_token()
    return EscapeScriptNode(nodelist)


@register.filter
def islist(value) -> bool:
    return isinstance(value, (list, tuple))


@register.filter
def isstring(value) -> bool:
    return isinstance(value, (str,))


@register.filter
def isdict(value) -> bool:
    return isinstance(value, (dict,))


@register.inclusion_tag("dump/dump.html")
def dump(value, key=None, original=None) -> Dict:
    return {"value": value, "key": key, "original": original}


@register.inclusion_tag("dump/list.html")
def dump_list(value, key=None, original=None) -> Dict:
    return {"value": value, "key": key, "original": original}


@register.inclusion_tag("dump/dict.html")
def dump_dict(value, key=None, original=None) -> Dict:
    return {"value": value, "key": key, "original": original}


@register.filter(name="smart")
def smart_attr(field, attr) -> Any:
    return field.field.flex_field.advanced.get("smart", {}).get(attr, "")


@register.filter(name="lookup")
def lookup(value, arg) -> Any:
    return value.get(arg, None)


@register.filter()
def is_image(element) -> bool:
    if not isinstance(element, str) or len(element) < 200 or (isinstance(element, str) and not element.isascii()):
        return False
    try:
        imgdata = base64.b64decode(str(element))
        im = Image.open(io.BytesIO(imgdata))
        im.verify()
        return True
    except (UnidentifiedImageError, ValueError):
        return False


@register.filter()
def is_base64(element) -> bool:
    expression = "^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$"
    try:
        if isinstance(element, str) and element.strip().endswith("=="):
            return bool(re.match(expression, element))
    except Exception as e:
        logger.exception(e)
    return False


@register.filter
def concat(a, b) -> str:
    """concatenate arg1 & arg2"""
    return "".join(map(str, (a, b)))
