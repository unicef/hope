import base64
import io
import logging
import re

from django.template import Context, Library, Node
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)
register = Library()


class EscapeScriptNode(Node):
    def __init__(self, nodelist: list[Node]) -> None:
        super().__init__()
        self.nodelist = nodelist

    def render(self, context: Context) -> str:
        out = self.nodelist.render(context)
        return out.replace("</script>", "<\\/script>")


@register.tag()
def escapescript(parser: object, token: object) -> EscapeScriptNode:
    nodelist = parser.parse(("endescapescript",))
    parser.delete_first_token()
    return EscapeScriptNode(nodelist)


@register.filter
def islist(value: object) -> bool:
    return isinstance(value, list | tuple)


@register.filter
def isstring(value: object) -> bool:
    return isinstance(value, str)


@register.filter
def isdict(value: object) -> bool:
    return isinstance(value, dict)


@register.inclusion_tag("dump/dump.html")
def dump(value: object, key: object | None = None, original: object | None = None) -> dict:
    return {"value": value, "key": key, "original": original}


@register.inclusion_tag("dump/list.html")
def dump_list(value: object, key: object | None = None, original: object | None = None) -> dict:
    return {"value": value, "key": key, "original": original}


@register.inclusion_tag("dump/dict.html")
def dump_dict(value: object, key: object | None = None, original: object | None = None) -> dict:
    return {"value": value, "key": key, "original": original}


@register.filter(name="smart")
def smart_attr(field: object, attr: object) -> object:
    return field.field.flex_field.advanced.get("smart", {}).get(attr, "")


@register.filter(name="lookup")
def lookup(value: object, arg: object) -> object:
    return value.get(arg, None)


@register.filter()
def is_image(element: object) -> bool:
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
def is_base64(element: object) -> bool:
    expression = "^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$"
    try:
        if isinstance(element, str) and element.strip().endswith("=="):
            return bool(re.match(expression, element))
    except Exception as e:
        logger.exception(e)
    return False


@register.filter
def concat(a: object, b: object) -> str:
    """Concatenate arg1 & arg2."""
    return "".join(map(str, (a, b)))
