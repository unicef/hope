from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag()
def get_related(user, field):
    related = []
    info = {
        "to": field.model._meta.model_name,
        "field_name": field.name,
        # 'related_name': field.related_name,
        # 'related_query_name': field.related_query_name,
    }

    if field.related_name:
        related = getattr(user, field.related_name).all()
    else:
        related = getattr(user, f"{field.name}_set").all()
    info["related_name"] = related.model._meta.verbose_name
    info["data"] = related

    return info
