import urllib.parse

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from hope.apps.administration.section_utils import as_bool

register = template.Library()


@register.simple_tag(takes_context=True)
def smart_toggler(context: template.Context) -> str:
    """Render the Smart Index / Standard Index toggle link.

    Ported from ``smart_admin.templatetags.smart.smart_toggler`` so the
    feature survives the ``django-unfold`` migration.
    """
    request = context["request"]
    page = urllib.parse.quote(request.path)
    if as_bool(request.COOKIES.get("smart", "0")):
        label = _("Standard Index")
        flag = "0"
    else:
        label = _("Smart Index")
        flag = "1"

    toggler = reverse("admin:smart_toggle", args=[flag])
    return mark_safe(  # noqa: S308
        f'<a href="{toggler}?from={page}" class="text-font-important-light '
        f'dark:text-font-important-dark hover:underline">{label}</a>'
    )
