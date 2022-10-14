from django import template
from django.contrib.admin.models import LogEntry
from django.template import TemplateSyntaxError
from django.template.base import kwarg_re
from django.template.defaulttags import URLNode, url
from django.utils.html import conditional_escape

register = template.Library()


class AdminLogNode(template.Node):
    def __init__(self, limit, varname, user):
        self.limit, self.varname, self.user = limit, varname, user

    def __repr__(self):
        return "<GetAdminLog Node>"

    def render(self, context):
        if self.user is None:
            entries = LogEntry.objects.all()
        else:
            user_id = self.user
            if not user_id.isdigit():
                user_id = context[self.user].pk
            entries = LogEntry.objects.filter(user__pk=user_id)
        context[self.varname] = entries.select_related("content_type", "user")[: int(self.limit)]
        return ""


@register.tag
def get_admin_log(parser, token):
    """
    Populate a template variable with the admin log for the given criteria.

    Usage::

        {% get_admin_log [limit] as [varname] for_user [context_var_containing_user_obj] %}

    Examples::

        {% get_admin_log 10 as admin_log for_user 23 %}
        {% get_admin_log 10 as admin_log for_user user %}
        {% get_admin_log 10 as admin_log %}

    Note that ``context_var_containing_user_obj`` can be a hard-coded integer
    (user ID) or the name of a template context variable containing the user
    object whose ID you want.
    """
    tokens = token.contents.split()
    if len(tokens) < 4:
        raise template.TemplateSyntaxError("'get_admin_log' statements require two arguments")
    if not tokens[1].isdigit():
        raise template.TemplateSyntaxError("First argument to 'get_admin_log' must be an integer")
    if tokens[2] != "as":
        raise template.TemplateSyntaxError("Second argument to 'get_admin_log' must be 'as'")
    if len(tokens) > 4:
        if tokens[4] != "for_user":
            raise template.TemplateSyntaxError("Fourth argument to 'get_admin_log' must be 'for_user'")
    return AdminLogNode(limit=tokens[1], varname=tokens[3], user=(tokens[5] if len(tokens) > 5 else None))


class URLNode2(URLNode):
    def render(self, context):
        from django.urls import NoReverseMatch, reverse

        args = [arg.resolve(context) for arg in self.args]
        kwargs = {k: v.resolve(context) for k, v in self.kwargs.items()}
        view_name = self.view_name.resolve(context)
        try:
            current_app = context.request.current_app
        except AttributeError:
            try:
                current_app = context.request.resolver_match.namespace
            except AttributeError:
                current_app = None
        # Try to look up the URL. If it fails, raise NoReverseMatch unless the
        # {% url ... as var %} construct is used, in which case return nothing.
        if view_name.startswith("admin:"):
            prefix, name = view_name.split(":")
            site = context["admin_site"]
            view_name = f"{site.name}:{name}"

        url = ""
        try:
            url = reverse(view_name, args=args, kwargs=kwargs, current_app=current_app)
        except NoReverseMatch:
            if self.asvar is None:
                raise

        if self.asvar:
            context[self.asvar] = url
            return ""
        else:
            if context.autoescape:
                url = conditional_escape(url)
            return url


@register.tag
def url2(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument, a URL pattern name." % bits[0])
    viewname = parser.compile_filter(bits[1])
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == "as":
        asvar = bits[-1]
        bits = bits[:-2]

    for bit in bits:
        match = kwarg_re.match(bit)
        if not match:
            raise TemplateSyntaxError("Malformed arguments to url tag")
        name, value = match.groups()
        if name:
            kwargs[name] = parser.compile_filter(value)
        else:
            args.append(parser.compile_filter(value))
    return URLNode2(viewname, args, kwargs, asvar)
