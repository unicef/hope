from django import template

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
